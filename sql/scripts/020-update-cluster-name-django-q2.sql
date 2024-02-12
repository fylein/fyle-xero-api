rollback;
begin;

update django_q_schedule set cluster = null where func in ('apps.workspaces.tasks.run_sync_schedule', 'apps.xero.tasks.check_xero_object_status', 'apps.xero.tasks.process_reimbursements', 'apps.xero.tasks.create_payment');

update django_q_schedule set cluster = 'import' where func not in ('apps.workspaces.tasks.run_sync_schedule', 'apps.xero.tasks.check_xero_object_status', 'apps.xero.tasks.process_reimbursements', 'apps.xero.tasks.create_payment');
