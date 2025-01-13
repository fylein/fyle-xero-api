from apps.fyle.models import (
    Expense,
    ExpenseGroup,
    ExpenseGroupSettings,
    Reimbursement,
    _group_expenses,
    get_default_expense_group_fields,
    get_default_expense_state,
)
from apps.workspaces.models import Workspace, WorkspaceGeneralSettings
from tests.test_fyle.fixtures import data


def test_default_fields():
    expense_group_field = get_default_expense_group_fields()
    expense_state = get_default_expense_state()

    assert expense_group_field == [
        "employee_email",
        "report_id",
        "claim_number",
        "fund_source",
    ]
    assert expense_state == "PAYMENT_PROCESSING"


def test_create_expense_objects(db):
    workspace_id = 1
    payload = data["expenses"]

    Expense.create_expense_objects(payload, workspace_id)
    expense = Expense.objects.last()

    assert expense.expense_id == "tx4ziVSAyIsv"


def test_create_eliminated_expense_objects(db):
    workspace_id = 1
    payload = data["eliminated_expenses"]

    Expense.create_expense_objects(payload, workspace_id)
    expense = Expense.objects.filter(expense_id="tx6wOnBVaumk")

    assert len(expense) == 0


def test_expense_group_settings(create_temp_workspace, db):
    workspace_id = 98
    payload = data["expense_group_settings_payload"]

    user = Workspace.objects.get(id=1).user

    ExpenseGroupSettings.update_expense_group_settings(payload, workspace_id, user)

    settings = ExpenseGroupSettings.objects.last()

    assert settings.reimbursable_expense_state == "PAYMENT_PROCESSING"
    assert settings.ccc_expense_state == "PAYMENT_PROCESSING"
    assert settings.ccc_export_date_type == "spent_at"


def test_create_reimbursement(db):
    workspace_id = 1
    reimbursements = data["reimbursements"]

    Reimbursement.create_or_update_reimbursement_objects(
        reimbursements=reimbursements, workspace_id=workspace_id
    )

    pending_reimbursement = Reimbursement.objects.get(reimbursement_id="reimgCW1Og0BcM")

    pending_reimbursement.state = "PENDING"
    pending_reimbursement.settlement_id = "setgCxsr2vTmZ"

    reimbursements[0]["is_paid"] = True

    Reimbursement.create_or_update_reimbursement_objects(
        reimbursements=reimbursements, workspace_id=workspace_id
    )

    paid_reimbursement = Reimbursement.objects.get(reimbursement_id="reimgCW1Og0BcM")
    paid_reimbursement.state == "PAID"


def test_create_expense_groups_by_report_id_fund_source(db):
    workspace_id = 1
    payload = data["expenses"]

    Expense.create_expense_objects(payload, workspace_id)
    expense_objects = Expense.objects.last()

    expense_group_settings = ExpenseGroupSettings.objects.get(workspace_id=workspace_id)
    expense_group_settings.reimbursable_export_date_type = "last_spent_at"
    expense_group_settings.ccc_export_date_type = "last_spent_at"
    expense_group_settings.save()

    expense_groups = _group_expenses(
        [],
        ["claim_number", "fund_source", "projects", "employee_email", "report_id"],
        4,
    )
    assert expense_groups == []

    ExpenseGroup.create_expense_groups_by_report_id_fund_source(
        [expense_objects], workspace_id
    )

    expense_groups = ExpenseGroup.objects.last()
    assert expense_groups.exported_at == None


def test_split_expense_grouping_with_no_bank_transaction_id(db, update_config_for_split_expense_grouping):
    '''
    Test for grouping of 2 expenses with no bank transaction id
    '''
    workspace_id = 1

    # Update settings
    general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=workspace_id)
    expense_group_settings = ExpenseGroupSettings.objects.get(workspace_id=workspace_id)
    update_config_for_split_expense_grouping(general_settings, expense_group_settings)

    # Get reference to expense objects
    expenses = data['ccc_split_expenses'][:2]
    for expense in expenses:
        expense['bank_transaction_id'] = None

    Expense.create_expense_objects(expenses, workspace_id=workspace_id)
    expense_objects = Expense.objects.filter(expense_id__in=[expense['id'] for expense in expenses])

    assert len(expense_objects) == 2, f'Expected 2 expenses, got {len(expense_objects)}'

    # Test for SINGLE_LINE_ITEM split expense grouping
    groups = ExpenseGroup.create_expense_groups_by_report_id_fund_source(expense_objects, workspace_id)
    assert len(groups) == 2, f'Expected 2 groups, got {len(groups)}'

    # Test for MULTIPLE_LINE_ITEM split expense grouping
    expense_group_settings.split_expense_grouping = 'MULTIPLE_LINE_ITEM'
    expense_group_settings.save()

    groups = ExpenseGroup.create_expense_groups_by_report_id_fund_source(expense_objects, workspace_id)
    assert len(groups) == 2, f'Expected 2 groups, got {len(groups)}'


def test_split_expense_grouping_with_same_and_different_ids(db, update_config_for_split_expense_grouping):
    '''
    Test for grouping of 2 expenses with the same bank transaction id,
    and one expense with a different bank transaction id
    '''
    workspace_id = 1

    # Update settings
    general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=workspace_id)
    expense_group_settings = ExpenseGroupSettings.objects.get(workspace_id=workspace_id)
    update_config_for_split_expense_grouping(general_settings, expense_group_settings)

    # Get reference to expense objects
    expenses = data['ccc_split_expenses'][:3]
    expenses[0]['bank_transaction_id'] = 'sample_1'
    expenses[1]['bank_transaction_id'] = 'sample_1'
    expenses[2]['bank_transaction_id'] = 'sample_2'

    Expense.create_expense_objects(expenses, workspace_id=workspace_id)
    expense_objects = Expense.objects.filter(expense_id__in=[expense['id'] for expense in expenses])

    assert len(expense_objects) == 3, f'Expected 3 expenses, got {len(expense_objects)}'

    # Test for SINGLE_LINE_ITEM split expense grouping
    groups = ExpenseGroup.create_expense_groups_by_report_id_fund_source(expense_objects, workspace_id)
    assert len(groups) == 3, f'Expected 3 groups, got {len(groups)}'

    # Test for MULTIPLE_LINE_ITEM split expense grouping
    expense_group_settings.split_expense_grouping = 'MULTIPLE_LINE_ITEM'
    expense_group_settings.save()

    groups = ExpenseGroup.create_expense_groups_by_report_id_fund_source(expense_objects, workspace_id)
    assert len(groups) == 2, f'Expected 2 groups, got {len(groups)}'


def test_split_expense_grouping_pairs_of_same_ids(db, update_config_for_split_expense_grouping):
    '''
    Test for grouping of 2 pairs of expenses with the same bank transaction ids
    '''
    workspace_id = 1

    # Update settings
    general_settings = WorkspaceGeneralSettings.objects.get(workspace_id=workspace_id)
    expense_group_settings = ExpenseGroupSettings.objects.get(workspace_id=workspace_id)
    update_config_for_split_expense_grouping(general_settings, expense_group_settings)

    # Get reference to expense objects
    expenses = data['ccc_split_expenses'][:4]
    expenses[0]['bank_transaction_id'] = 'sample_1'
    expenses[1]['bank_transaction_id'] = 'sample_1'
    expenses[2]['bank_transaction_id'] = 'sample_2'
    expenses[3]['bank_transaction_id'] = 'sample_2'

    Expense.create_expense_objects(expenses, workspace_id=workspace_id)
    expense_objects = Expense.objects.filter(expense_id__in=[expense['id'] for expense in expenses])

    assert len(expense_objects) == 4, f'Expected 4 expenses, got {len(expense_objects)}'

    # Test for SINGLE_LINE_ITEM split expense grouping
    groups = ExpenseGroup.create_expense_groups_by_report_id_fund_source(expense_objects, workspace_id)
    assert len(groups) == 4, f'Expected 4 groups, got {len(groups)}'

    # Test for MULTIPLE_LINE_ITEM split expense grouping
    expense_group_settings.split_expense_grouping = 'MULTIPLE_LINE_ITEM'
    expense_group_settings.save()

    groups = ExpenseGroup.create_expense_groups_by_report_id_fund_source(expense_objects, workspace_id)
    assert len(groups) == 2, f'Expected 2 groups, got {len(groups)}'
