from datetime import datetime, timedelta
from typing import List

from django_q.models import Schedule

from apps.workspaces.models import WorkspaceSchedule


def schedule_email_notification(workspace_id: int, schedule_enabled: bool, hours: int):
    if schedule_enabled and hours:
        schedule, _ = Schedule.objects.update_or_create(
            func="apps.workspaces.tasks.run_email_notification",
            args="{}".format(workspace_id),
            cluster='import',
            defaults={
                "schedule_type": Schedule.MINUTES,
                "minutes": hours * 60,
                "next_run": datetime.now() + timedelta(minutes=10),
            },
        )
    else:
        schedule: Schedule = Schedule.objects.filter(
            func="apps.workspaces.tasks.run_email_notification",
            args="{}".format(workspace_id),
        ).first()

        if schedule:
            schedule.delete()


def schedule_sync(
    workspace_id: int,
    schedule_enabled: bool,
    hours: int,
    email_added: List,
    emails_selected: List,
    is_real_time_export_enabled: bool,
):
    ws_schedule, _ = WorkspaceSchedule.objects.get_or_create(workspace_id=workspace_id)

    schedule_email_notification(
        workspace_id=workspace_id, schedule_enabled=schedule_enabled, hours=hours
    )

    if schedule_enabled:
        ws_schedule.enabled = schedule_enabled
        ws_schedule.start_datetime = datetime.now()
        ws_schedule.interval_hours = hours
        ws_schedule.emails_selected = emails_selected
        ws_schedule.is_real_time_export_enabled = is_real_time_export_enabled

        for email in email_added:
            if email not in ws_schedule.additional_email_options:
                ws_schedule.additional_email_options.append(email)

        if is_real_time_export_enabled:
            # Delete existing schedule since user changed the setting to real time export
            schedule = ws_schedule.schedule
            if schedule:
                ws_schedule.schedule = None
                schedule.delete()
        else:
            schedule, _ = Schedule.objects.update_or_create(
                func="apps.workspaces.tasks.run_sync_schedule",
                args="{}".format(workspace_id),
                defaults={
                    "schedule_type": Schedule.MINUTES,
                    "minutes": hours * 60,
                    "next_run": datetime.now() + timedelta(hours=hours),
                }
            )
            ws_schedule.schedule = schedule

        ws_schedule.save()

    elif not schedule_enabled and ws_schedule.schedule:
        schedule = ws_schedule.schedule
        ws_schedule.enabled = schedule_enabled
        ws_schedule.schedule = None
        ws_schedule.save()
        schedule.delete()

    return ws_schedule
