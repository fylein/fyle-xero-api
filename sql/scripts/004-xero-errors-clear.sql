rollback;
begin;

update task_logs set xero_errors = null where status = 'COMPLETE' and xero_errors is not null;