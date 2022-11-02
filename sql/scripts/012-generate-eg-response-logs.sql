rollback;
begin;

with tl as (
  select 
    t.detail as detail,
    t.expense_group_id as expense_group_id
  from task_logs t
    where expense_group_id is not null 
    and status = 'COMPLETE'
)
update expense_groups
    set response_logs = tl.detail
from tl
    where id = tl.expense_group_id;
