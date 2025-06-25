data = {
    "export_settings": {
        "expense_group_settings": {
            "reimbursable_expense_state": "PAYMENT_PROCESSING",
            "reimbursable_export_date_type": "",
            "ccc_expense_state": "PAYMENT_PROCESSING",
            "ccc_export_date_type": "",
            "expense_state": "",
            "split_expense_grouping": "MULTIPLE_LINE_ITEM",
        },
        "workspace_general_settings": {
            "reimbursable_expenses_object": "PURCHASE BILL",
            "corporate_credit_card_expenses_object": "BANK TRANSACTION",
            "auto_map_employees": "EMAIL",
        },
        "general_mappings": {
            "bank_account": {"id": "10", "name": "Visa"},
            "payment_account": {"id": "11", "name": "Credit card"},
        },
    },
    "export_settings_response": {
        "workspace_general_settings": {
            "reimbursable_expenses_object": "PURCHASE BILL",
            "corporate_credit_card_expenses_object": "BANK TRANSACTION",
            "auto_map_employees": "EMAIL",
        },
        "expense_group_settings": {
            "reimbursable_expense_group_fields": [
                "fund_source",
                "report_id",
                "employee_email",
                "claim_number",
            ],
            "reimbursable_export_date_type": "current_date",
            "reimbursable_expense_state": "PAYMENT_PROCESSING",
            "corporate_credit_card_expense_group_fields": [
                "employee_email",
                "claim_number",
                "fund_source",
                "report_id",
                "expense_id",
                "spent_at",
            ],
            "ccc_export_date_type": "spent_at",
            "ccc_expense_state": "PAYMENT_PROCESSING",
            "split_expense_grouping": "MULTIPLE_LINE_ITEM",
        },
        "general_mappings": {
            "bank_account": {"id": "10", "name": "Visa"},
            "payment_account": {"id": "11", "name": "Credit card"},
        },
        "workspace_id": 1,
    },
    "export_settings_missing_values": {
        "expense_group_settings": "",
        "workspace_general_settings": "",
        "general_mappings": "",
    },
}
