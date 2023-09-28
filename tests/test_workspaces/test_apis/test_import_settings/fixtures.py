data = {
    "import_settings": {
        "workspace_general_settings": {
            "import_categories": True,
            "charts_of_accounts": ["Expense", "COST of goods"],
            "import_tax_codes": True,
            "import_customers": True,
            "import_suppliers_as_merchants": True,
        },
        "general_mappings": {"default_tax_code": {"id": "129", "name": "GST@0%"}},
        "mapping_settings": [
            {
                "source_field": "KRATOS",
                "destination_field": "ITEM",
                "import_to_fyle": True,
                "is_custom": True,
                "source_placeholder": "This is a custom placeholder",
            },
            {
                "source_field": "Weekend",
                "destination_field": "REGION",
                "import_to_fyle": True,
                "is_custom": True,
                "source_placeholder": "This will be added by postman",
            },
        ],
    },
    "import_settings_2": {
        "workspace_general_settings": {
            "import_categories": True,
            "charts_of_accounts": ["Expense", "COST of goods"],
            "import_tax_codes": True,
            "import_customers": False,
            "import_suppliers_as_merchants": False,
        },
        "general_mappings": {"default_tax_code": {"id": "129", "name": "GST@0%"}},
        "mapping_settings": [
            {
                "source_field": "PROJECT",
                "destination_field": "ITEM",
                "import_to_fyle": True,
                "is_custom": False,
                "source_placeholder": None,
            },
            {
                "source_field": "COST_CENTER",
                "destination_field": "REGION",
                "import_to_fyle": True,
                "is_custom": False,
                "source_placeholder": None,
            },
        ],
    },
    "import_settings_response": {
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
    "import_settings_missing_values": {
        "workspace_general_settings": {},
        "general_mappings": {},
        "mapping_settings": [],
    },
}
