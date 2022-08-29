data = {
    'bill_payload':{
        'VendorRef':{
            'value':'43'
        },
        'APAccountRef':{
            'value':'33'
        },
        'DepartmentRef':{
            'value':'None'
        },
        'TxnDate':'2022-01-21',
        'CurrencyRef':{
            'value':'USD'
        },
        'PrivateNote':'Reimbursable expense by ashwin.t@fyle.in on 2022-01-21 ',
        'Line':[
            {
                'Description':'ashwin.t@fyle.in - Travel - 2022-01-21 - C/2022/01/R/8 -  - https://staging.fyle.tech/app/main/#/enterprise/view_expense/txlPjmNxssq1?org_id=orGcBCVPijjO',
                'DetailType':'AccountBasedExpenseLineDetail',
                'Amount':60.0,
                'AccountBasedExpenseLineDetail':{
                    'AccountRef':{
                        'value':'57'
                    },
                    'CustomerRef':{
                        'value':'None'
                    },
                    'ClassRef':{
                        'value':'None'
                    },
                    'TaxCodeRef':{
                        'value':'None'
                    },
                    'TaxAmount':0.0,
                    'BillableStatus':'NotBillable'
                }
            }
        ]
    },
    'bank_transaction_payload':{
        'DocNumber':'E/2022/01/T/9',
        'PaymentType':'CreditCard',
        'AccountRef':{
            'value':'42'
        },
        'EntityRef':{
            'value':'58'
        },
        'DepartmentRef':{
            'value':'None'
        },
        'TxnDate':'2022-01-21',
        'CurrencyRef':{
            'value':'USD'
        },
        'PrivateNote':'Credit card expense by ashwin.t@fyle.in on 2022-01-21 ',
        'Credit':False,
        'Line':[
            {
                'Description':'ashwin.t@fyle.in - Travel - 2022-01-21 - C/2022/01/R/8 -  - https://staging.fyle.tech/app/main/#/enterprise/view_expense/txvh8qm7RTRI?org_id=orGcBCVPijjO',
                'DetailType':'AccountBasedExpenseLineDetail',
                'Amount':30.0,
                'AccountBasedExpenseLineDetail':{
                    'AccountRef':{
                        'value':'57'
                    },
                    'CustomerRef':{
                        'value':'None'
                    },
                    'ClassRef':{
                        'value':'None'
                    },
                    'TaxCodeRef':{
                        'value':'None'
                    },
                    'TaxAmount':0.0,
                    'BillableStatus':'NotBillable'
                }
            }
        ]
    },
    'bill_response':{
        'DueDate':'2020-01-14',
        'Balance':1000.0,
        'domain':'QBO',
        'sparse':False,
        'Id':'146',
        'SyncToken':'0',
        'MetaData':{
            'CreateTime':'2020-01-14T02:18:29-08:00',
            'LastUpdatedTime':'2020-01-14T02:18:29-08:00'
        },
        'DocNumber':'rphZKTDmSLU2',
        'TxnDate':'2020-01-14',
        'CurrencyRef':{
            'value':'USD',
            'name':'United States Dollar'
        },
        'PrivateNote':'Report None / rphZKTDmSLU2 approved on 2020-01-14',
        'Line':[
            {
                'Id':'1',
                'LineNum':1,
                'Description':'Testing',
                'Amount':1000.0,
                'DetailType':'AccountBasedExpenseLineDetail',
                'AccountBasedExpenseLineDetail':{
                    'AccountRef':{
                        'value':'2',
                        'name':'Retained Earnings'
                    },
                    'BillableStatus':'NotBillable',
                    'TaxCodeRef':{
                        'value':'NON'
                    }
                }
            }
        ],
        'VendorRef':{
            'value':'56',
            'name':'Gokul'
        },
        'APAccountRef':{
            'value':'33',
            'name':'Accounts Payable (A/P)'
        },
        'TotalAmt':1000.0
    },
    'create_contact': {
        'Contacts': [{
            'ContactID':'79c88297-27fb-4f6f-87a8-fe27017031c6',
            'ContactStatus':'ACTIVE',
            'Name':'sample',
            'FirstName':'sample',
            'LastName':'',
            'EmailAddress':'sample@fyle.in',
            'BankAccountDetails':'',
            'Addresses':[
                {
                    'AddressType':'STREET',
                    'City':'',
                    'Region':'',
                    'PostalCode':'',
                    'Country':''
                },
                {
                    'AddressType':'POBOX',
                    'City':'',
                    'Region':'',
                    'PostalCode':'',
                    'Country':''
                }
            ],
            'Phones':[
                {
                    'PhoneType':'DEFAULT',
                    'PhoneNumber':'',
                    'PhoneAreaCode':'',
                    'PhoneCountryCode':''
                },
                {
                    'PhoneType':'DDI',
                    'PhoneNumber':'',
                    'PhoneAreaCode':'',
                    'PhoneCountryCode':''
                },
                {
                    'PhoneType':'FAX',
                    'PhoneNumber':'',
                    'PhoneAreaCode':'',
                    'PhoneCountryCode':''
                },
                {
                    'PhoneType':'MOBILE',
                    'PhoneNumber':'',
                    'PhoneAreaCode':'',
                    'PhoneCountryCode':''
                }
            ],
            'UpdatedDateUTC':'/Date(1660754701320+0000)/',
            'ContactGroups':[
                
            ],
            'IsSupplier':False,
            'IsCustomer':False,
            'SalesTrackingCategories':[
                
            ],
            'PurchasesTrackingCategories':[
                
            ],
            'ContactPersons':[
                
            ],
            'HasValidationErrors':False
        }]
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
            'settlement_id': 'setrunCck8hLH',
            'updated_at': '2022-01-20T16:30:44.584100',
            'user_id': 'usqywo0f3nBY',
        },
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
            'reimbursement_number': 'P/2022/01/R/3',
            'settlement_id': 'setrunCck8hLH',
            'updated_at': '2022-01-20T16:30:44.584100',
            'user_id': 'usqywo0f3nBY',
        },
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
            'reimbursement_number': 'P/2022/01/R/4',
            'settlement_id': 'setlpIUKpdvsT',
            'updated_at': '2022-01-20T16:30:44.584100',
            'user_id': 'usqywo0f3nBY',
        },
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
            'reimbursement_number': 'P/2022/01/R/5',
            'settlement_id': 'set33iAVXO7BA',
            'updated_at': '2022-01-20T16:30:44.584100',
            'user_id': 'usqywo0f3nBY',
        },
    ],
    'bill_object': {
        "Id":"21a31ed7-0a35-44d4-b4a1-64c0fdc65a1a",
        "Status":"OK",
        "ProviderName":"Fyle Staging",
        "DateTimeUTC":"/Date(1660833015693)/",
        "Invoices":[
            {
                "Type":"ACCPAY",
                "InvoiceID":"c35cf4b3-784a-408b-9ddf-df111dd2e073",
                "InvoiceNumber":"",
                "Reference":"2 - ashwin.t@fyle.in",
                "Prepayments":[
                    
                ],
                "Overpayments":[
                    
                ],
                "AmountDue":5.0,
                "AmountPaid":0.0,
                "SentToContact":False,
                "CurrencyRate":1.0,
                "IsDiscounted":False,
                "HasAttachments":False,
                "HasErrors":False,
                "Attachments":[
                    
                ],
                "Contact":{
                    "ContactID":"9eecdd86-78bb-47c9-95df-986369748151",
                    "ContactStatus":"ACTIVE",
                    "Name":"Joanna",
                    "FirstName":"Joanna",
                    "LastName":"",
                    "EmailAddress":"ashwin.t@fyle.in",
                    "BankAccountDetails":"",
                    "Addresses":[
                        {
                            "AddressType":"STREET",
                            "City":"",
                            "Region":"",
                            "PostalCode":"",
                            "Country":""
                        },
                        {
                            "AddressType":"POBOX",
                            "City":"",
                            "Region":"",
                            "PostalCode":"",
                            "Country":""
                        }
                    ],
                    "Phones":[
                        {
                            "PhoneType":"DEFAULT",
                            "PhoneNumber":"",
                            "PhoneAreaCode":"",
                            "PhoneCountryCode":""
                        },
                        {
                            "PhoneType":"DDI",
                            "PhoneNumber":"",
                            "PhoneAreaCode":"",
                            "PhoneCountryCode":""
                        },
                        {
                            "PhoneType":"FAX",
                            "PhoneNumber":"",
                            "PhoneAreaCode":"",
                            "PhoneCountryCode":""
                        },
                        {
                            "PhoneType":"MOBILE",
                            "PhoneNumber":"",
                            "PhoneAreaCode":"",
                            "PhoneCountryCode":""
                        }
                    ],
                    "UpdatedDateUTC":"/Date(1659085778640+0000)/",
                    "ContactGroups":[
                        
                    ],
                    "IsSupplier":True,
                    "IsCustomer":False,
                    "SalesTrackingCategories":[
                        
                    ],
                    "PurchasesTrackingCategories":[
                        
                    ],
                    "ContactPersons":[
                        
                    ],
                    "HasValidationErrors":False
                },
                "DateString":"2022-08-02T00:00:00",
                "Date":"/Date(1659398400000+0000)/",
                "DueDateString":"2022-08-16T00:00:00",
                "DueDate":"/Date(1660608000000+0000)/",
                "Status":"PAID",
                "LineAmountTypes":"Exclusive",
                "LineItems":[
                    {
                        "Description":"ashwin.t@fyle.in, category - Food spent on 2020-05-25, report number - C/2022/05/R/16  - https://staging.fyle.tech/app/main/#/enterprise/view_expense/txUDvDmEV4ep?org_id=orPJvXuoLqvJ",
                        "UnitAmount":4.62,
                        "TaxType":"INPUT",
                        "TaxAmount":0.38,
                        "LineAmount":4.62,
                        "AccountCode":"429",
                        "Tracking":[
                            
                        ],
                        "Quantity":1.0,
                        "LineItemID":"51cca2e7-5bef-452c-83fb-2ca8c0865f37",
                        "ValidationErrors":[
                            
                        ]
                    }
                ],
                "SubTotal":4.62,
                "TotalTax":0.38,
                "Total":5.0,
                "UpdatedDateUTC":"/Date(1659472064663+0000)/",
                "CurrencyCode":"USD"
            }
        ]
    },
    'bank_transaction_object': {
        "Id":"c22e17e3-3c85-4026-97d4-ea721bb6c232",
        "Status":"OK",
        "ProviderName":"Fyle Staging",
        "DateTimeUTC":"/Date(1661360170676)/",
        "BankTransactions":[
            {
                "BankTransactionID":"3022c267-f40c-4050-8018-ca42643d8b95",
                "BankAccount":{
                    "AccountID":"562555f2-8cde-4ce9-8203-0363922537a4",
                    "Code":"090",
                    "Name":"Business Bank Account"
                },
                "Type":"SPEND",
                "Reference":"521254 - sravan.kumar@fyle.in",
                "IsReconciled":False,
                "CurrencyRate":1.0,
                "Contact":{
                    "ContactID":"3aaf24ba-6d35-455f-b92a-9e0dc20d3d9a",
                    "ContactStatus":"ACTIVE",
                    "Name":"Credit Card Misc",
                    "FirstName":"Credit",
                    "LastName":"Misc",
                    "EmailAddress":"",
                    "BankAccountDetails":"",
                    "Addresses":[
                        {
                            "AddressType":"STREET",
                            "City":"",
                            "Region":"",
                            "PostalCode":"",
                            "Country":""
                        },
                        {
                            "AddressType":"POBOX",
                            "City":"",
                            "Region":"",
                            "PostalCode":"",
                            "Country":""
                        }
                    ],
                    "Phones":[
                        {
                            "PhoneType":"DEFAULT",
                            "PhoneNumber":"",
                            "PhoneAreaCode":"",
                            "PhoneCountryCode":""
                        },
                        {
                            "PhoneType":"DDI",
                            "PhoneNumber":"",
                            "PhoneAreaCode":"",
                            "PhoneCountryCode":""
                        },
                        {
                            "PhoneType":"FAX",
                            "PhoneNumber":"",
                            "PhoneAreaCode":"",
                            "PhoneCountryCode":""
                        },
                        {
                            "PhoneType":"MOBILE",
                            "PhoneNumber":"",
                            "PhoneAreaCode":"",
                            "PhoneCountryCode":""
                        }
                    ],
                    "UpdatedDateUTC":"/Date(1659470543540+0000)/",
                    "ContactGroups":[
                        
                    ],
                    "ContactPersons":[
                        
                    ],
                    "HasValidationErrors":False
                },
                "DateString":"2022-05-24T00:00:00",
                "Date":"/Date(1653350400000+0000)/",
                "Status":"AUTHORISED",
                "LineAmountTypes":"Exclusive",
                "LineItems":[
                    {
                        "Description":"sravan.kumar@fyle.in, category - WIP spent on 2022-05-24, report number - C/2022/05/R/12  - https://staging.fyle.tech/app/main/#/enterprise/view_expense/txkw3dt3umkN?org_id=orPJvXuoLqvJ",
                        "UnitAmount":93.3,
                        "TaxType":"INPUT",
                        "TaxAmount":7.7,
                        "LineAmount":93.3,
                        "AccountCode":"429",
                        "Tracking":[
                            
                        ],
                        "Quantity":1.0,
                        "LineItemID":"088e4457-05f3-432d-91d0-a599ebd0a284",
                        "AccountID":"4281c446-efb4-445d-b32d-c441a4ef5678",
                        "ValidationErrors":[
                            
                        ]
                    }
                ],
                "SubTotal":93.3,
                "TotalTax":7.7,
                "Total":101.0,
                "UpdatedDateUTC":"/Date(1661360170477+0000)/",
                "CurrencyCode":"USD"
            }
        ]
    }
}