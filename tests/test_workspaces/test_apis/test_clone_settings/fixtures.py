data = {
    "clone_settings_response": {
        "export_settings": {
            "workspace_general_settings": {
                "reimbursable_expenses_object": "PURCHASE BILL",
                "corporate_credit_card_expenses_object": "BANK TRANSACTION",
                "auto_map_employees": "EMAIL",
                "is_simplify_report_closure_enabled": True,
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
                "import_card_credits": True,
                "split_expense_grouping": "MULTIPLE_LINE_ITEM",
            },
            "general_mappings": {
                "bank_account": {"id": "10", "name": "Visa"},
                "payment_account": {"id": "11", "name": "Credit card"},
            },
            "workspace_id": 1,
        },
        "import_settings": {
            "workspace_general_settings": {
                "import_categories": True,
                "charts_of_accounts": ["Expense", "COST of goods"],
                "import_tax_codes": True,
                "import_customers": True,
                "import_suppliers_as_merchants": True,
            },
            "general_mappings": {"default_tax_code": {"name": "GST@0%", "id": "129"}},
            "mapping_settings": [
                {
                    "source_field": "KRATOS",
                    "destination_field": "ITEM",
                    "import_to_fyle": True,
                    "is_custom": True,
                    "source_placeholder": "This is a custom placeholder",
                },
                {
                    "source_field": "WEEKEND",
                    "destination_field": "REGION",
                    "import_to_fyle": True,
                    "is_custom": True,
                    "source_placeholder": "This will be added by postman",
                },
            ],
            "workspace_id": 1,
        },
        "advanced_settings": {
            "workspace_general_settings": {
                "change_accounting_period": True,
                "sync_fyle_to_xero_payments": False,
                "sync_xero_to_fyle_payments": True,
                "auto_create_destination_entity": True,
                "auto_create_merchant_destination_entity": True,
            },
            "general_mappings": {
                "payment_account": {"id": "2", "name": "Business Savings Account"}
            },
            "workspace_schedules": {
                "enabled": True,
                "interval_hours": 1,
                "additional_email_options": [],
                "emails_selected": ["anish.ks@fyle.in"],
            },
            "workspace_id": 1,
        },
        "workspace_id": 1,
    },
    "clone_settings_missing_values": {
        "export_settings": {},
        "import_settings": None,
        "advanced_settings": False,
        "workspace_id": 1,
    },
    "clone_settings": {
        "export_settings": {
            "expense_group_settings": {
                "reimbursable_expense_state": "PAYMENT_PROCESSING",
                "reimbursable_export_date_type": "current_date",
                "ccc_expense_state": "PAID",
                "ccc_export_date_type": "spent_at",
                "split_expense_grouping": "MULTIPLE_LINE_ITEM",
            },
            "workspace_general_settings": {
                "reimbursable_expenses_object": "PURCHASE BILL",
                "corporate_credit_card_expenses_object": None,
                "auto_map_employees": "NAME",
            },
            "general_mappings": {"bank_account": {"id": None, "name": None}},
        },
        "import_settings": {
            "workspace_general_settings": {
                "import_categories": False,
                "charts_of_accounts": ["EXPENSE"],
                "import_tax_codes": False,
                "import_suppliers_as_merchants": False,
                "import_customers": False,
            },
            "general_mappings": {"default_tax_code": {"id": None, "name": None}},
            "mapping_settings": [],
        },
        "advanced_settings": {
            "workspace_general_settings": {
                "sync_fyle_to_xero_payments": False,
                "sync_xero_to_fyle_payments": False,
                "auto_create_destination_entity": False,
                "change_accounting_period": False,
                "auto_create_merchant_destination_entity": False,
            },
            "general_mappings": {"payment_account": {"name": None, "id": None}},
            "workspace_schedules": {
                "enabled": True,
                "interval_hours": 1,
                "start_datetime": "2023-04-04T14:14:02.462Z",
                "emails_selected": ["ashwin.t+ajhsdg@fyle.in"],
                "additional_email_options": [],
            },
        },
    },
    "clone_settings_exists": {"is_available": True, "workspace_name": "FAE"},
    "clone_settings_not_exists": {"is_available": False, "workspace_name": None},
}
