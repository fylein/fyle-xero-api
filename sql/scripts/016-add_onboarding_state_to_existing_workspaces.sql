-- Create a view for joined on all settings tables to figure out onboarding progress
create or replace view all_settings_view as 
select 
    w.id as workspace_id,
    wgs.id as configuration_id,
    gm.id as general_mappings_id,
    xc.id as xero_creds_id 
from workspaces w 
left join 
    workspace_general_settings wgs on w.id = wgs.workspace_id 
left join 
    xero_credentials xc on xc.workspace_id = w.id 
left join 
    general_mappings gm on gm.workspace_id = w.id
where w.onboarding_state = 'CONNECTION';

begin; -- Start Transaction Block

-- Count of all workspaces where xero creds are present, configuration is present and general mappings are present
select 
    'XC=TRUE, C=TRUE, GM=TRUE' as setting, count(*) 
from all_settings_view 
where 
    configuration_id is not null and general_mappings_id is not null and xero_creds_id is not null;

--- Update all of the above to have onboarding state set to 'COMPLETE'
update workspaces 
set 
    onboarding_state = 'COMPLETE' 
where id in (
    select 
        workspace_id 
    from all_settings_view 
    where 
        configuration_id is not null and general_mappings_id is not null and xero_creds_id is not null
);

-- Count of all workspaces where xero creds are present, configuration is present and general mappings are not present
select 
    'XC=TRUE, C=TRUE, GM=FALSE' as settings, count(*) 
from all_settings_view 
where 
    configuration_id is not null and general_mappings_id is null and xero_creds_id is not null;

--- Update all of the above to have onboarding state set to 'EXPORT_SETTINGS'
update workspaces 
set 
    onboarding_state = 'EXPORT_SETTINGS'
where id in (
    select 
        workspace_id 
    from all_settings_view 
    where 
        configuration_id is not null and general_mappings_id is not null and xero_creds_id is not null
);


-- Count of all workspaces where xero creds are present, configuration is not present and general mappings are not present
select 
    'XC=TRUE, C=FALSE, GM=FALSE' as settings, count(*) 
from all_settings_view 
where 
    configuration_id is null and general_mappings_id is null and xero_creds_id is not null;

--- Update all of the above to have onboarding state set to 'MAP_EMPLOYEES'
update workspaces 
set 
    onboarding_state = 'EXPORT_SETTINGS' 
where id in (
    select 
        workspace_id 
    from all_settings_view 
    where 
        configuration_id is null and general_mappings_id is not null and xero_creds_id is not null
);


-- Count of all workspaces where xero creds is not present, configuration is present and general mappings is present
select 
    'XC=FALSE, C=TRUE, GM=TRUE' as settings, count(*) 
from all_settings_view 
where 
    configuration_id is not null and general_mappings_id is not null and xero_creds_id is null;

--- Update all of the above to have onboarding state set to 'COMPLETE'
update workspaces 
set 
    onboarding_state = 'COMPLETE' 
where id in (
    select 
        workspace_id 
    from all_settings_view 
    where 
        configuration_id is not null and general_mappings_id is not null and xero_creds_id is null
);


-- Count of all workspaces where xero creds are not present, configuration is present and general mappings are not present
select 
    'XC=FALSE, C=TRUE, GM=FALSE' as settings, count(*) 
from all_settings_view 
where 
    configuration_id is not null and general_mappings_id is null and xero_creds_id is null;

--- Update all of the above to have onboarding state set to 'EXPORT_SETTINGS'
update workspaces 
set 
    onboarding_state = 'EXPORT_SETTINGS' 
where id in (
    select 
        workspace_id 
    from all_settings_view 
    where 
        configuration_id is not null and general_mappings_id is null and xero_creds_id is null
);
