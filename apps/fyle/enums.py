"""
This file contains all the enums used in the Fyle app
"""

class FundSourceEnum:
    """
    Enum for Fund Source
    """
    PERSONAL = 'PERSONAL'
    CCC = 'CCC'


class FyleAttributeEnum:
    """
    Enum for Fyle Attributes
    """
    CATEGORY = 'CATEGORY'
    CATEGORY_DISPLAY = 'Category'

    PROJECT = 'PROJECT'
    PROJECT_DISPLAY = 'Project'

    COST_CENTER = 'COST_CENTER'
    COST_CENTER_DISPLAY = 'Cost Center'

    CORPORATE_CARD = 'CORPORATE_CARD'
    CORPORATE_CARD_DISPLAY = 'Corporate Card'

    TAX_GROUP = 'TAX_GROUP'
    TAX_GROUP_DISPLAY = 'Tax Group'

    EMPLOYEE = 'EMPLOYEE'
    EMPLOYEE_DISPLAY = 'Employee'


class ExpenseStateEnum:
    """
    Enum for Expense State
    """
    APPROVED = 'APPROVED'
    PAYMENT_PROCESSING = 'PAYMENT_PROCESSING'
    PAID = 'PAID'


class PlatformExpensesEnum:
    """
    Enum for Platform Expenses
    """
    PERSONAL_CASH_ACCOUNT = 'PERSONAL_CASH_ACCOUNT'
    PERSONAL_CORPORATE_CREDIT_CARD_ACCOUNT = 'PERSONAL_CORPORATE_CREDIT_CARD_ACCOUNT'
    REIMBURSEMENT_COMPLETE = 'COMPLETE'
    REIMBURSEMENT_PENDING = 'PENDING'
