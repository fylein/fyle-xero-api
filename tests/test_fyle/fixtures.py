data = {
    "expenses": [
        {
            'id': 'tx4ziVSAyIsv',
            'employee_email': 'jhonsnow@fyle.in',
            'category': 'Accounts Payable',
            'sub_category': 'Accounts Payable',
            'project': 'Aaron Abbott',
            'project_id': 263589,
            'expense_number': 'E/2021/12/T/3',
            'org_id': 'orsO0VW86WLQ',
            'claim_number': 'C/2021/12/R/2',
            'amount': 150,
            'tax_amount': 0,
            'tax_group_id': 'tgWdIdEwcKlK',
            'settled_at': '2021-12-23T07:16:17.034079+00:00',
            'currency': 'USD',
            'foreign_amount': None,
            'foreign_currency': None,
            'settlement_id': 'seteYqkAfuWOS',
            'reimbursable': True,
            'billable': False,
            'state': 'PAID',
            'vendor': None,
            'cost_center': None,
            'corporate_card_id': None,
            'purpose': None,
            'report_id': 'rpqaDywYdbbw',
            'file_ids': [],
            'spent_at': '2021-12-22T07:30:26.289842+00:00',
            'approved_at': '2021-12-22T07:30:26.289842+00:00',
            'expense_created_at': '2021-12-23T07:14:13.990650+00:00',
            'expense_updated_at': '2021-12-27T05:26:43.954470+00:00',
            'source_account_type': 'PERSONAL_CASH_ACCOUNT',
            'verified_at': None,
            'custom_properties': {
                  'Vehicle Type': '',
                  'Fyle Categories': '',
            },
        },
    ],
    "eliminated_expenses": [
        {
            'id': 'tx6wOnBVaumk',
            'employee_email': 'jhonsnow@fyle.in',
            'category': 'Accounts Payable',
            'sub_category': 'Accounts Payable',
            'project': 'Aaron Abbott',
            'project_id': 263589,
            'expense_number': 'E/2021/12/T/3',
            'org_id': 'orsO0VW86WLQ',
            'claim_number': 'C/2021/12/R/2',
            'amount': 150,
            'tax_amount': 0,
            'tax_group_id': 'tgWdIdEwcKlK',
            'settled_at': '2020-12-23T07:16:17.034079+00:00',
            'currency': 'USD',
            'foreign_amount': None,
            'foreign_currency': None,
            'settlement_id': 'seteYqkAfuWOS',
            'reimbursable': True,
            'billable': False,
            'state': 'PAID',
            'vendor': None,
            'cost_center': None,
            'corporate_card_id': None,
            'purpose': None,
            'report_id': 'rpqaDywYdbbw',
            'file_ids': [],
            'spent_at': '2020-12-22T07:30:26.289842+00:00',
            'approved_at': '2020-12-22T07:30:26.289842+00:00',
            'expense_created_at': '2020-12-23T07:14:13.990650+00:00',
            'expense_updated_at': '2020-12-27T05:26:43.954470+00:00',
            'source_account_type': 'PERSONAL_CASH_ACCOUNT',
            'verified_at': None,
            'custom_properties': {
                  'Vehicle Type': '',
                  'Fyle Categories': '',
            },
        }
    ],
    "expense_group_id": {
        "id": 1,
        "fund_source": "PERSONAL",
        "description": {
            "report_id": "rpuN3bgphxbK",
            "fund_source": "PERSONAL",
            "claim_number": "C/2021/11/R/5",
            "employee_email": "ashwin.t@fyle.in",
        },
        "response_logs": {
            "name": None,
            "type": "expenseReport",
            "externalId": "03294720937402397402937",
            "internalId": "116142",
        },
        "created_at": "2021-11-15T10:29:07.618062Z",
        "exported_at": "2021-11-15T11:02:55.125205Z",
        "updated_at": "2021-11-15T11:02:55.125634Z",
        "workspace": 1,
        "expenses": [1],
    },
    "expense_group_setting_response": {
        "id": 1,
        "reimbursable_expense_group_fields": [
            "employee_email",
            "report_id",
            "claim_number",
            "fund_source"
        ],
        "corporate_credit_card_expense_group_fields": [
            "employee_email",
            "report_id",
            "claim_number",
            "fund_source"
        ],
        "expense_state": "PAYMENT_PROCESSING",
        "reimbursable_export_date_type": "current_date",
        "ccc_export_date_type": "current_date",
        "import_card_credits": "false",
        "created_at": "2021-11-15T08:46:16.069944Z",
        "updated_at": "2021-11-15T08:46:16.069986Z",
        "workspace": 1
    },
    'reimbursements': [
        {
            'amount': 76,
            'code': None,
            'created_at': '2022-01-20T16:30:44.584100',
            'creator_user_id': 'usqywo0f3nBY',
            'currency': 'USD',
            'id': 'reimgCW1Og0BcM',
            'is_exported': False,
            'is_paid': False,
            'mode': 'OFFLINE',
            'org_id': 'orsO0VW86WLQ',
            'paid_at': None,
            'purpose': 'C/2022/01/R/2;Ashwin',
            'reimbursement_number': 'P/2022/01/R/2',
            'settlement_id': 'setgCxsr2vTmZ',
            'updated_at': '2022-01-20T16:30:44.584100',
            'user_id': 'usqywo0f3nBY',
        }
    ],
    'expense_group_settings_payload': {
        'reimbursable_expense_group_fields': ['claim_number'],
        'corporate_credit_card_expense_group_fields': ['claim_number'],
        'expense_state': 'PAYMENT_PROCESSING',
        'reimbursable_export_date_type': 'spent_at',
        'ccc_export_date_type': 'spent_at',
    },
    "expense_fields_response":[
        {
            "attribute_type":"COST_CENTER",
            "display_name":"Cost Center"
        },
        {
            "attribute_type":"PROJECT",
            "display_name":"Project"
        },
        {
            "attribute_type":"CLASS",
            "display_name":"Class"
        }
    ],
    "cost_centers_view":[
        {
            "id":1802,
            "attribute_type":"COST_CENTER",
            "display_name":"Cost Center",
            "value":"1200191",
            "source_id":"9556",
            "auto_mapped":False,
            "auto_created":False,
            "active":None,
            "detail":None,
            "created_at":"2022-08-02T20:25:10.752731Z",
            "updated_at":"2022-08-02T20:25:10.752760Z",
            "workspace":1
        }
   ],
   "categories_view":[
        {
            "id":221,
            "attribute_type":"CATEGORY",
            "display_name":"Category",
            "value":"ABN",
            "source_id":"196431",
            "auto_mapped":False,
            "auto_created":False,
            "active":None,
            "detail":None,
            "created_at":"2022-08-02T20:25:06.664182Z",
            "updated_at":"2022-08-02T20:25:06.664205Z",
            "workspace":1
        }
   ],
   "employee_view":[
        {
            "id":10,
            "attribute_type":"EMPLOYEE",
            "display_name":"Employee",
            "value":"arun.tvs@fyle.in",
            "source_id":"ouyf10hfUkrB",
            "auto_mapped":False,
            "auto_created":False,
            "active":None,
            "detail":{
                "user_id":"usEyHSLj6aHw",
                "location":None,
                "full_name":"kk",
                "department":None,
                "department_id":None,
                "employee_code":None,
                "department_code":None
            },
            "created_at":"2022-08-02T20:25:06.274482Z",
            "updated_at":"2022-08-02T20:25:06.274511Z",
            "workspace":1
        }
   ],
   "project_view":[
        {
            "id":542,
            "attribute_type":"PROJECT",
            "display_name":"Project",
            "value":"116142-Voya-EBSalesforce-OFS",
            "source_id":"1182",
            "auto_mapped":False,
            "auto_created":False,
            "active":None,
            "detail":None,
            "created_at":"2022-08-02T20:25:07.837942Z",
            "updated_at":"2022-08-02T20:25:07.837969Z",
            "workspace":1
        }
   ],
   "expense_group_id_response":{
        "id":1,
        "fund_source":"PERSONAL",
        "description":{
            "report_id":"rp9EvDF8Umk6",
            "fund_source":"PERSONAL",
            "claim_number":"C/2022/06/R/2",
            "employee_email":"ashwin.t@fyle.in"
        },
        "created_at":"2022-08-02T20:26:22.939437Z",
        "exported_at":"2022-08-02T20:27:52.017417Z",
        "updated_at":"2022-08-02T20:27:52.017711Z",
        "workspace":1,
        "expenses":[
            1
        ]
    },
    "expense_group_by_id_expenses_response":{
        "id":1,
        "fund_source":"PERSONAL",
        "description":{
            "report_id":"rp9EvDF8Umk6",
            "fund_source":"PERSONAL",
            "claim_number":"C/2022/06/R/2",
            "employee_email":"ashwin.t@fyle.in"
        },
        "created_at":"2022-08-02T20:26:22.939437Z",
        "exported_at":"2022-08-02T20:27:52.017417Z",
        "updated_at":"2022-08-02T20:27:52.017711Z",
        "workspace":1,
        "expenses":[
            1
        ]
    },
} 
