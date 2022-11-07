from fyle_accounting_mappings.models import ExpenseAttribute

from apps.fyle.models import ExpenseGroup

expense_groups = ExpenseGroup.objects.all()

for expense_group in expense_groups:
    if expense_group.employee_name is not None:
        pass
    else:
        employee = ExpenseAttribute.objects.filter(
            workspace_id=expense_group.workspace_id, value=expense_group.description['employee_email'], attribute_type='EMPLOYEE'
        ).first()
        if employee and employee.detail:
            expense_group.employee_name = employee.detail['full_name']
            expense_group.save()
        else:
            pass

for expense_group in expense_groups:
    if expense_group.employee_name:
        expenses = expense_group.expenses.all()
        if expenses:
            for expense in expenses:
                expense.employee_name = expense_group.employee_name
                expense.save()
