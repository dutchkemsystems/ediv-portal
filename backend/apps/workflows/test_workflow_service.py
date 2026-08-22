from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.workflows.models import Workflow, WorkflowStep
from apps.workflows.services.workflow_service import WorkflowService
from apps.workflows.workflow_definitions import ALL_WORKFLOWS

User = get_user_model()


class WorkflowServiceSeedTest(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            email="admin@ediv.gov.ng",
            password="AdminPass123!@#",
            first_name="Admin",
            last_name="User",
            role="SYSADMIN",
        )
        self.reg_officer = User.objects.create_user(
            email="reg@ediv.gov.ng",
            password="RegPass123!@#",
            first_name="Reg",
            last_name="Officer",
            role="REG_OFF",
        )
        self.tg = User.objects.create_user(
            email="tg@ediv.gov.ng",
            password="TgPass123!@#",
            first_name="Tutor",
            last_name="General",
            role="TG_PS",
        )

    def test_seed_all_creates_all_workflows_and_steps(self):
        stats = WorkflowService.seed_all()
        self.assertEqual(stats["created"], len(ALL_WORKFLOWS))
        self.assertEqual(stats["updated"], 0)

        for wf_type, definition in ALL_WORKFLOWS.items():
            wf = WorkflowService.get_workflow_by_type(wf_type)
            self.assertIsNotNone(wf, f"No workflow for {wf_type}")
            self.assertEqual(wf.name, definition["name"])
            self.assertEqual(wf.status, "ACTIVE")
            self.assertTrue(wf.is_template)
            self.assertEqual(wf.steps.count(), len(definition["steps"]))

    def test_seed_all_is_idempotent(self):
        WorkflowService.seed_all()
        stats = WorkflowService.seed_all()
        self.assertEqual(stats["created"], 0)
        self.assertEqual(stats["updated"], len(ALL_WORKFLOWS))
        self.assertEqual(Workflow.objects.count(), len(ALL_WORKFLOWS))
        total_steps = sum(len(d["steps"]) for d in ALL_WORKFLOWS.values())
        self.assertEqual(WorkflowStep.objects.count(), total_steps)

    def test_seed_maps_definition_roles_to_user_roles(self):
        WorkflowService.seed_all()
        incoming = WorkflowService.get_workflow_by_type("INCOMING_MAIL")
        first_step = incoming.steps.get(order=1)
        self.assertEqual(first_step.assigned_role, "REG_OFF")
        tg_step = incoming.steps.get(order=11)
        self.assertEqual(tg_step.assigned_role, "TG_PS")

    def test_seed_raises_without_sysadmin(self):
        User.objects.filter(role="SYSADMIN").delete()
        with self.assertRaises(ValueError):
            WorkflowService.seed_all()


class WorkflowServiceInstanceTest(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            email="admin@ediv.gov.ng",
            password="AdminPass123!@#",
            first_name="Admin",
            last_name="User",
            role="SYSADMIN",
        )
        self.reg_officer = User.objects.create_user(
            email="reg@ediv.gov.ng",
            password="RegPass123!@#",
            first_name="Reg",
            last_name="Officer",
            role="REG_OFF",
        )
        self.staff = User.objects.create_user(
            email="staff@ediv.gov.ng",
            password="StaffPass123!@#",
            first_name="Staff",
            last_name="Member",
            role="SA_OFF",
        )
        WorkflowService.seed_all()
        self.workflow_type = "INTERNAL_MEMO"

    def test_start_instance_assigns_first_task(self):
        instance = WorkflowService.start_instance(
            workflow_type=self.workflow_type,
            initiated_by=self.admin,
            reference_number="MEMO-0001",
        )
        self.assertEqual(instance.status, "IN_PROGRESS")
        self.assertIsNotNone(instance.current_step)
        self.assertEqual(instance.current_step.order, 1)
        task = instance.tasks.first()
        self.assertEqual(task.status, "PENDING")
        self.assertEqual(task.assigned_to, self.staff)

    def test_start_instance_unknown_type_raises(self):
        with self.assertRaises(ValueError):
            WorkflowService.start_instance(
                workflow_type="UNKNOWN_TYPE",
                initiated_by=self.admin,
                reference_number="MEMO-0002",
            )

    def test_advance_walks_through_all_steps(self):
        instance = WorkflowService.start_instance(
            workflow_type=self.workflow_type,
            initiated_by=self.admin,
            reference_number="MEMO-0003",
        )
        step_count = instance.workflow.steps.count()

        for _ in range(step_count - 1):
            current_step = instance.current_step
            assignee = instance.tasks.filter(step=current_step, status="PENDING").first().assigned_to
            result = WorkflowService.advance(instance, user=assignee, decision="APPROVE")
            self.assertEqual(result["status"], "IN_PROGRESS")
            self.assertGreater(instance.current_step.order, current_step.order)

        final_step = instance.current_step
        final_assignee = instance.tasks.filter(step=final_step, status="PENDING").first().assigned_to
        result = WorkflowService.advance(instance, user=final_assignee, decision="APPROVE")
        self.assertEqual(result["status"], "COMPLETED")
        instance.refresh_from_db()
        self.assertEqual(instance.status, "COMPLETED")
        self.assertIsNone(instance.current_step)
        self.assertIsNotNone(instance.completed_at)
        self.assertEqual(instance.tasks.filter(status="COMPLETED").count(), step_count)

    def test_advance_rejects_unassigned_user(self):
        instance = WorkflowService.start_instance(
            workflow_type=self.workflow_type,
            initiated_by=self.admin,
            reference_number="MEMO-0004",
        )
        other = User.objects.create_user(
            email="other@ediv.gov.ng",
            password="OtherPass123!@#",
            first_name="Other",
            last_name="User",
            role="SA_OFF",
        )
        with self.assertRaises(ValueError):
            WorkflowService.advance(instance, user=other, decision="APPROVE")

    def test_advance_completed_instance_raises(self):
        instance = WorkflowService.start_instance(
            workflow_type=self.workflow_type,
            initiated_by=self.admin,
            reference_number="MEMO-0005",
        )
        for _ in range(instance.workflow.steps.count()):
            assignee = instance.tasks.filter(status="PENDING").first().assigned_to
            WorkflowService.advance(instance, user=assignee, decision="APPROVE")
            instance.refresh_from_db()

        with self.assertRaises(ValueError):
            WorkflowService.advance(instance, user=self.admin, decision="APPROVE")

    def test_reference_number_uniqueness_enforced(self):
        WorkflowService.start_instance(
            workflow_type=self.workflow_type,
            initiated_by=self.admin,
            reference_number="MEMO-0006",
        )
        with self.assertRaises(Exception):
            WorkflowService.start_instance(
                workflow_type=self.workflow_type,
                initiated_by=self.admin,
                reference_number="MEMO-0006",
            )
