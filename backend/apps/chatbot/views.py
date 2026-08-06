from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import ChatSession, ChatMessage, ChatIntent
from .serializers import (
    ChatSessionSerializer, ChatMessageSerializer, ChatIntentSerializer,
    ChatRequestSerializer, ChatResponseSerializer
)
from .services.chatbot_engine import ChatbotEngine


class ChatSessionViewSet(viewsets.ModelViewSet):
    serializer_class = ChatSessionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ChatSession.objects.filter(user=self.request.user, is_active=True)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['post'], url_path='send')
    def send_message(self, request):
        serializer = ChatRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        message = serializer.validated_data['message']
        session_id = serializer.validated_data.get('session_id')

        if session_id:
            session = ChatSession.objects.filter(id=session_id, user=request.user).first()
            if not session:
                return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            session = ChatSession.objects.create(user=request.user)

        ChatMessage.objects.create(session=session, role='user', content=message)

        intent_result = ChatbotEngine.detect_intent(message)
        intent = intent_result['intent']
        confidence = intent_result['confidence']

        if intent == 'unknown':
            reply = ChatbotEngine.get_response('unknown', request.user)
        else:
            reply = ChatbotEngine.get_response(intent, request.user)

        ChatMessage.objects.create(
            session=session, role='assistant', content=reply,
            intent=intent, confidence=confidence
        )
        session.save()

        suggestions = ChatbotEngine._get_suggestions(request.user.role)

        return Response({
            'reply': reply,
            'intent': intent,
            'confidence': confidence,
            'session_id': session.id,
            'suggestions': suggestions,
        })

    @action(detail=False, methods=['get'], url_path='history')
    def chat_history(self, request):
        sessions = ChatSession.objects.filter(user=request.user, is_active=True)[:10]
        serializer = ChatSessionSerializer(sessions, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='suggestions')
    def suggestions(self, request):
        suggestions = ChatbotEngine._get_suggestions(request.user.role)
        return Response({'suggestions': suggestions})


class ChatIntentViewSet(viewsets.ModelViewSet):
    queryset = ChatIntent.objects.all()
    serializer_class = ChatIntentSerializer
    permission_classes = [permissions.IsAdminUser]
