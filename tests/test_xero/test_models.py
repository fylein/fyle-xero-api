from datetime import datetime
from apps.fyle.models import ExpenseGroup
from fyle_accounting_mappings.models import MappingSetting
from apps.xero.models import Bill, BillLineItem, get_tax_code_id_or_none, get_customer_id_or_none, get_tracking_category, \
    get_expense_purpose, get_transaction_date, get_item_code_or_none, BankTransaction, BankTransactionLineItem, Payment


def test_create_bill(db):
    expense_group = ExpenseGroup.objects.get(id=4)

    bill = Bill.create_bill(expense_group)
    bill_lineitems = BillLineItem.create_bill_lineitems(expense_group)

    for bill_lineitem in bill_lineitems:
        assert bill_lineitem.amount == 10.0
        assert bill_lineitem.description == 'sravan.kumar@fyle.in, category - Food spent on 2020-01-01, report number - C/2022/06/R/1  - https://staging.fyle.tech/app/main/#/enterprise/view_expense/txGilVGolf60?org_id=orPJvXuoLqvJ'

    assert bill.currency == 'USD'


def test_bank_transaction(db):
    expense_group = ExpenseGroup.objects.get(id=5)

    bank_transaction = BankTransaction.create_bank_transaction(expense_group, True)
    bank_transaction_lineitems = BankTransactionLineItem.create_bank_transaction_lineitems(expense_group)

    for bank_transaction_lineitem in bank_transaction_lineitems:
        assert bank_transaction_lineitem.amount == 101.0
        
    assert bank_transaction.currency == 'USD'
    assert bank_transaction.transaction_date == '2022-05-24'


def test_create_payment(db):
    expense_group = ExpenseGroup.objects.get(id=7)

    payment = Payment.create_payment(expense_group=expense_group, invoice_id='sdfgh', account_id='sdfgh')

    assert payment.amount == 45.0
    assert payment.invoice_id == 'sdfgh'


def test_get_tracking_category(db):
    expense_group = ExpenseGroup.objects.get(id=8)
    expenses = expense_group.expenses.all()

    for lineitem in expenses:
        tracking_categories = get_tracking_category(expense_group, lineitem)
        assert tracking_categories == []


def test_get_item_code_or_none(db):
    expense_group = ExpenseGroup.objects.get(id=8)
    expenses = expense_group.expenses.all()
    
    mapping_setting = MappingSetting.objects.filter( 
        workspace_id=expense_group.workspace_id, 
    ).first() 

    mapping_setting.destination_field = 'ITEM'
    mapping_setting.save()

    for lineitem in expenses:
        item_code = get_item_code_or_none(expense_group, lineitem)
        assert item_code == None
    
    mapping_setting.source_field == 'PROJECT'
    mapping_setting.save()

    for lineitem in expenses:
        lineitem.project = 'Bank West'
        item_code = get_item_code_or_none(expense_group, lineitem)
        assert item_code == None

    mapping_setting.source_field == 'COST_CENTER'
    mapping_setting.save()

    for lineitem in expenses:
        lineitem.cost_center = 'Adidas'
        item_code = get_item_code_or_none(expense_group, lineitem)
        assert item_code == None


def test_get_tax_code_id_or_none(db):
    expense_group = ExpenseGroup.objects.get(id=8)
    expenses = expense_group.expenses.all()

    for lineitem in expenses:
        tax_code = get_tax_code_id_or_none(expense_group, lineitem)
        assert tax_code == None


def test_get_customer_id_or_none(db):
    expense_group = ExpenseGroup.objects.get(id=8)
    expenses = expense_group.expenses.all()

    for lineitem in expenses:
        lineitem.billable = True
        lineitem.project = 'Bank West'
        bill_lineitem_objects = get_customer_id_or_none(expense_group, lineitem)
        assert bill_lineitem_objects == '47f61ab1-5245-40a2-a3a5-bc224c850c8d'
    
    mapping_setting = MappingSetting.objects.filter( 
        workspace_id=expense_group.workspace_id, 
        destination_field='CUSTOMER' 
    ).first() 
    mapping_setting.source_field = 'PROJECT'
    mapping_setting.save()

    for lineitem in expenses:
        bill_lineitem_objects = get_customer_id_or_none(expense_group, lineitem)
        assert bill_lineitem_objects == '47f61ab1-5245-40a2-a3a5-bc224c850c8d'

    mapping_setting.source_field = 'COST_CENTER'
    mapping_setting.save()
    for lineitem in expenses:
        bill_lineitem_objects = get_customer_id_or_none(expense_group, lineitem)
        assert bill_lineitem_objects == None


def test_get_expense_purpose(db):
    workspace_id = 1

    expense_group = ExpenseGroup.objects.get(id=10)
    expenses = expense_group.expenses.all()

    for lineitem in expenses:
        category = lineitem.category if lineitem.category == lineitem.sub_category else '{0} / {1}'.format(
            lineitem.category, lineitem.sub_category)
    
        expense_purpose = get_expense_purpose(workspace_id, lineitem, category)

        assert expense_purpose == 'sravan.kumar@fyle.in, category - WIP / None spent on 2022-05-25, report number - C/2022/05/R/13  - https://staging.fyle.tech/app/main/#/enterprise/view_expense/txBMQRkBQciI?org_id=orPJvXuoLqvJ'


def test_get_transaction_date(db):
    expense_group = ExpenseGroup.objects.get(id=8)

    transaction_date = get_transaction_date(expense_group)
    assert transaction_date <= datetime.now().strftime('%Y-%m-%d')

    expense_group.description.pop('spent_at')

    approved_at = {'approved_at': '2000-09-14'}
    expense_group.description.update(approved_at)

    transaction_date = get_transaction_date(expense_group)
    assert transaction_date <= datetime.now().strftime('%Y-%m-%d')

    verified_at = {'verified_at': '2000-09-14'}
    expense_group.description.pop('approved_at')
    expense_group.description.update(verified_at)

    transaction_date = get_transaction_date(expense_group)
    assert transaction_date <= datetime.now().strftime('%Y-%m-%d')

    last_spent_at = {'last_spent_at': '2000-09-14'}
    expense_group.description.pop('verified_at')
    expense_group.description.update(last_spent_at)

    transaction_date = get_transaction_date(expense_group)
    assert transaction_date <= datetime.now().strftime('%Y-%m-%d')
