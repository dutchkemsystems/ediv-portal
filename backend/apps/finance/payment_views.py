import json
import logging
from datetime import date
from decimal import Decimal

from django.db import transaction
from django.db.models import Sum
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import permissions, status, views
from rest_framework.response import Response

from .korapay import KoraPayService
from .models import Payment, StudentFee

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name="dispatch")
class InitializePaymentView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        student_fee_id = request.data.get("student_fee_id")
        amount = request.data.get("amount")

        if not student_fee_id or not amount:
            return Response({"error": "student_fee_id and amount are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            student_fee = StudentFee.objects.select_related("student__user", "fee_structure__school").get(
                id=student_fee_id
            )
        except StudentFee.DoesNotExist:
            return Response({"error": "Student fee not found"}, status=status.HTTP_404_NOT_FOUND)

        amount = Decimal(str(amount))
        if amount <= 0:
            return Response({"error": "Amount must be greater than zero"}, status=status.HTTP_400_BAD_REQUEST)

        if amount > student_fee.balance:
            return Response(
                {"error": f"Amount exceeds outstanding balance of {student_fee.balance}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        korapay = KoraPayService()
        reference = korapay.generate_reference()

        user = student_fee.student.user
        customer_name = user.get_full_name()
        customer_email = user.email

        notification_url = None
        # Webhook URL would be configured on the KoraPay dashboard
        # For now, we'll use the verify endpoint

        payment_data = korapay.initialize_payment(
            amount=amount,
            reference=reference,
            customer_name=customer_name,
            customer_email=customer_email,
            metadata={
                "student_fee_id": student_fee_id,
                "school": student_fee.fee_structure.school.name,
                "fee_type": student_fee.fee_structure.fee_type,
            },
            notification_url=notification_url,
        )

        # Create pending payment record
        Payment.objects.create(
            student_fee=student_fee,
            amount=amount,
            payment_method="ONLINE",
            reference_number=reference,
            payment_date=date.today(),
            received_by=request.user,
            notes="KoraPay online payment initiated",
        )

        return Response(payment_data)


@method_decorator(csrf_exempt, name="dispatch")
class KoraPayWebhookView(views.APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request):
        try:
            payload = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        # Verify webhook signature
        signature = request.META.get("HTTP_X_KORAPAY_SIGNATURE", "")
        korapay = KoraPayService()

        if korapay.webhook_secret and not korapay.verify_webhook_signature(request.body, signature):
            logger.warning("Invalid KoraPay webhook signature")
            return JsonResponse({"error": "Invalid signature"}, status=401)

        event = payload.get("event")
        data = payload.get("data", {})

        if event == "charge.success":
            reference = data.get("payment_reference") or data.get("reference")
            transaction_status = data.get("transaction_status")
            amount_paid = Decimal(str(data.get("amount", 0))) / 100  # Convert from kobo

            try:
                payment = Payment.objects.select_related("student_fee").get(reference_number=reference)
            except Payment.DoesNotExist:
                logger.warning(f"Payment not found for reference: {reference}")
                return JsonResponse({"status": "ignored"}, status=200)

            if transaction_status == "success":
                payment.is_confirmed = True
                payment.confirmed_by = payment.received_by
                payment.transaction_id = data.get("reference", "")
                payment.save()

                # Atomic update with row-level lock to prevent race conditions
                with transaction.atomic():
                    student_fee = StudentFee.objects.select_for_update().get(
                        pk=payment.student_fee_id
                    )
                    total_paid = (
                        student_fee.payments.filter(is_confirmed=True).aggregate(total=Sum("amount"))["total"] or 0
                    )
                    student_fee.amount_paid = total_paid
                    student_fee.balance = student_fee.amount_due - student_fee.amount_paid
                    if student_fee.balance <= 0:
                        student_fee.status = "COMPLETED"
                    elif student_fee.amount_paid > 0:
                        student_fee.status = "PARTIAL"
                    else:
                        student_fee.status = "PENDING"
                    student_fee.save(update_fields=["amount_paid", "balance", "status", "updated_at"])

                logger.info(f"Payment confirmed: {reference} - {amount_paid} NGN")
            elif transaction_status in ("underpaid", "overpaid"):
                payment.notes += (
                    f' | {transaction_status}: expected {data.get("amount_expected")}, got {data.get("amount")}'
                )
                payment.save()
                logger.warning(f"Payment {transaction_status}: {reference}")

        return JsonResponse({"status": "ok"}, status=200)


class VerifyPaymentView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, reference):
        try:
            payment = Payment.objects.select_related("student_fee__student__user", "student_fee__fee_structure").get(
                reference_number=reference
            )
        except Payment.DoesNotExist:
            return Response({"error": "Payment not found"}, status=status.HTTP_404_NOT_FOUND)

        return Response(
            {
                "reference": payment.reference_number,
                "amount": str(payment.amount),
                "status": "confirmed" if payment.is_confirmed else "pending",
                "payment_method": payment.payment_method,
                "payment_date": str(payment.payment_date),
                "student_fee": {
                    "id": payment.student_fee.id,
                    "amount_due": str(payment.student_fee.amount_due),
                    "amount_paid": str(payment.student_fee.amount_paid),
                    "balance": str(payment.student_fee.balance),
                    "fee_name": payment.student_fee.fee_structure.name,
                    "student_name": payment.student_fee.student.user.get_full_name(),
                },
            }
        )
