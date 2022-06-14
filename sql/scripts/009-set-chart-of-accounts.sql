rollback; begin;

update workspace_general_settings set charts_of_accounts = ['EXPENSE', 'ASSET', 'REVENUE']
where workspace_id in (92, 121, 132, 126, 130, 129, 131, 124, 123);