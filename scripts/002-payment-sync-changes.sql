rollback;
begin;

-- change expense_state from PAYMENT_PENDING to PAYMENT_PROCESSING
update fyle_expensegroupsettings
set expense_state = 'PAYMENT_PROCESSING'
where fyle_expensegroupsettings.expense_state = 'PAYMENT_PENDING';

-- bills
update bills
set payment_synced = True
where bills.payment_synced = False;

-- bills
update bills
set paid_on_xero = True
where bills.paid_on_xero = False;

-- expenses
update expenses
set paid_on_xero = True
where expenses.paid_on_xero = False;