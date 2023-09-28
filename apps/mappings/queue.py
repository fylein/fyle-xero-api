from datetime import datetime, timedelta

from django_q.models import Schedule
from fyle_accounting_mappings.models import MappingSetting


def schedule_auto_map_employees(employee_mapping_preference: str, workspace_id: str):
    if employee_mapping_preference:
        Schedule.objects.update_or_create(
            func="apps.mappings.tasks.async_auto_map_employees",
            args="{}".format(workspace_id),
            defaults={
                "schedule_type": Schedule.MINUTES,
                "minutes": 24 * 60,
                "next_run": datetime.now(),
            },
        )
    else:
        schedule: Schedule = Schedule.objects.filter(
            func="apps.mappings.tasks.async_auto_map_employees",
            args="{}".format(workspace_id),
        ).first()

        if schedule:
            schedule.delete()


def schedule_cost_centers_creation(import_to_fyle, workspace_id: int):
    if import_to_fyle:
        schedule, _ = Schedule.objects.update_or_create(
            func="apps.mappings.tasks.auto_create_cost_center_mappings",
            args="{}".format(workspace_id),
            defaults={
                "schedule_type": Schedule.MINUTES,
                "minutes": 24 * 60,
                "next_run": datetime.now(),
            },
        )
    else:
        schedule: Schedule = Schedule.objects.filter(
            func="apps.mappings.tasks.auto_create_cost_center_mappings",
            args="{}".format(workspace_id),
        ).first()

        if schedule:
            schedule.delete()


def schedule_tax_groups_creation(import_tax_codes, workspace_id):
    if import_tax_codes:
        schedule, _ = Schedule.objects.update_or_create(
            func="apps.mappings.tasks.auto_create_tax_codes_mappings",
            args="{}".format(workspace_id),
            defaults={
                "schedule_type": Schedule.MINUTES,
                "minutes": 24 * 60,
                "next_run": datetime.now(),
            },
        )
    else:
        schedule: Schedule = Schedule.objects.filter(
            func="apps.mappings.tasks.auto_create_tax_codes_mappings",
            args="{}".format(workspace_id),
        ).first()

        if schedule:
            schedule.delete()


def schedule_fyle_attributes_creation(workspace_id: int):
    mapping_settings = MappingSetting.objects.filter(
        is_custom=True, import_to_fyle=True, workspace_id=workspace_id
    ).all()

    if mapping_settings:
        schedule, _ = Schedule.objects.get_or_create(
            func="apps.mappings.tasks.async_auto_create_custom_field_mappings",
            args="{0}".format(workspace_id),
            defaults={
                "schedule_type": Schedule.MINUTES,
                "minutes": 24 * 60,
                "next_run": datetime.now() + timedelta(hours=24),
            },
        )
    else:
        schedule: Schedule = Schedule.objects.filter(
            func="apps.mappings.tasks.async_auto_create_custom_field_mappings",
            args=workspace_id,
        ).first()

        if schedule:
            schedule.delete()
