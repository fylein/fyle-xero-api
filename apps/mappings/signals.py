"""
Mapping Signals
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_q.tasks import async_task

from .models import TenantMapping


@receiver(post_save, sender=TenantMapping)
def run_post_tenant_mapping_trigger(sender, instance: TenantMapping, **kwargs):
    """
    :param sender: Sender Class
    :param instance: Row Instance of Sender Class
    :return: None
    """
    async_task('apps.xero.tasks.create_missing_currency', int(instance.workspace_id))
