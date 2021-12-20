-- IMPORTANT IMPORTANT IMPORTANT: This is a pre deployment script.
-- Create mapping settings for Fyle Cards <> Xero Bank Account

rollback; begin;

create temp view enable_cards_mapping_workspaces as 
select
    'CORPORATE_CARD' as source_field,
    'BANK_ACCOUNT' as destination_field,
    now() as created_at,
    now() as updated_at,
    wgs.id as workspace_id,
    false as import_to_fyle,
    false as is_custom
from workspace_general_settings wgs
where wgs.map_fyle_cards_xero_bank_account = 'f';


insert into mapping_settings (source_field, destination_field, created_at, updated_at, workspace_id, import_to_fyle, is_custom) 
select 
    source_field,
    destination_field,
    created_at,
    updated_at,
    workspace_id,
    import_to_fyle,
    is_custom
from enable_cards_mapping_workspaces;
