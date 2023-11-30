"""
All the task logs related enums are defined here
"""


class TaskLogStatusEnum:
    """
    Enum for Task Log Status
    """
    ENQUEUED = 'ENQUEUED'
    IN_PROGRESS = 'IN_PROGRESS'
    FAILED = 'FAILED'
    COMPLETE = 'COMPLETE'
    FATAL = 'FATAL'


class TaskLogTypeEnum:
    """
    Enum for Task Log Type
    """
    FETCHING_EXPENSES = 'FETCHING_EXPENSES'
    CREATING_BILL = 'CREATING_BILL'
    CREATING_BANK_TRANSACTION = 'CREATING_BANK_TRANSACTION'
    CREATING_PAYMENT = 'CREATING_PAYMENT'

class ErrorTypeEnum:
    """
    Enum for Error Type
    """
    EMPLOYEE_MAPPING = 'EMPLOYEE_MAPPING'
    CATEGORY_MAPPING = 'CATEGORY_MAPPING'
    XERO_ERROR = 'XERO_ERROR'
