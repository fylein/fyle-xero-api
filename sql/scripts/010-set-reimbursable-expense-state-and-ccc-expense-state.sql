rollback;
begin;

update 
  expense_group_settings 
set 
  reimbursable_expense_state = expense_group_settings.expense_state, 
  ccc_expense_state = expense_group_settings.expense_state 
where 
  workspace_id in (
    select 
      workspace_id 
    from 
      expense_group_settings 
    where 
      ccc_expense_state is null 
      or reimbursable_expense_state is null
  );