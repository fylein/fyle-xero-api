from datetime import datetime, timedelta

from django_q.models import Schedule

from apps.mappings.models import GeneralMapping


def schedule_payment_creation(sync_fyle_to_xero_payments, workspace_id):
    general_mappings: GeneralMapping = GeneralMapping.objects.filter(
        workspace_id=workspace_id
    ).first()
    if general_mappings:
        if sync_fyle_to_xero_payments and general_mappings.payment_account_id:
            start_datetime = datetime.now()
            schedule, _ = Schedule.objects.update_or_create(
                func="apps.xero.tasks.create_payment",
                args="{}".format(workspace_id),
                defaults={
                    "schedule_type": Schedule.MINUTES,
                    "minutes": 24 * 60,
                    "next_run": start_datetime,
                },
            )
    if not sync_fyle_to_xero_payments:
        schedule: Schedule = Schedule.objects.filter(
            func="apps.xero.tasks.create_payment", args="{}".format(workspace_id)
        ).first()

        if schedule:
            schedule.delete()


def schedule_xero_objects_status_sync(sync_xero_to_fyle_payments, workspace_id):
    if sync_xero_to_fyle_payments:
        start_datetime = datetime.now()
        schedule, _ = Schedule.objects.update_or_create(
            func="apps.xero.tasks.check_xero_object_status",
            args="{}".format(workspace_id),
            defaults={
                "schedule_type": Schedule.MINUTES,
                "minutes": 24 * 60,
                "next_run": start_datetime,
            },
        )
    else:
        schedule: Schedule = Schedule.objects.filter(
            func="apps.xero.tasks.check_xero_object_status",
            args="{}".format(workspace_id),
        ).first()

        if schedule:
            schedule.delete()


def schedule_reimbursements_sync(sync_xero_to_fyle_payments, workspace_id):
    if sync_xero_to_fyle_payments:
        start_datetime = datetime.now() + timedelta(hours=12)
        schedule, _ = Schedule.objects.update_or_create(
            func="apps.xero.tasks.process_reimbursements",
            args="{}".format(workspace_id),
            defaults={
                "schedule_type": Schedule.MINUTES,
                "minutes": 24 * 60,
                "next_run": start_datetime,
            },
        )
    else:
        schedule: Schedule = Schedule.objects.filter(
            func="apps.xero.tasks.process_reimbursements",
            args="{}".format(workspace_id),
        ).first()

        if schedule:
            schedule.delete()
