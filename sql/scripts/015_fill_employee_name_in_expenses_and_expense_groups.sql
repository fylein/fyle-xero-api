rollback;
begin;

update 
  expense_groups 
set 
  employee_name = (select distinct expense_attributes.detail ->> 'full_name' 
from 
    expense_attributes where expense_groups.description ->> 'employee_email' = expense_attributes.value);

-- Run this in after running the above query.
update 
  expenses 
set 
  employee_name = (
    select 
      distinct expense_groups.employee_name 
    from 
      expense_groups 
      inner join expense_groups_expenses on expense_groups.id = expense_groups_expenses.expensegroup_id 
      inner join expenses on expense_groups_expenses.expense_id = expenses.id
  )
