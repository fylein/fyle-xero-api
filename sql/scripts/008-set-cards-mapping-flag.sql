-- Set skip_cards_mapping to true for current workspaces who are onboarded

rollback; begin;

update workspace_general_settings set skip_cards_mapping = true where 
    workspace_id in (
        select workspace_id from xero_credentials
    ) and workspace_id in (
        select workspace_id from tenant_mappings
    ) and workspace_id in (
        select workspace_id from general_mappings
    ) and workspace_id in (
        select distinct workspace_id from mappings where source_type = 'EMPLOYEE'
    ) and workspace_id in (
        select distinct workspace_id from mappings where source_type = 'CATEGORY'
    )
;
