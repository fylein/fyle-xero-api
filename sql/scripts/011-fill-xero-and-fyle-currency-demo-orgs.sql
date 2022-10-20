rollback;
begin;

update 
  workspaces 
set 
  xero_currency = 'USD', 
  fyle_currency = 'USD' 
where 
  id not in (
    select 
      workspace_id as id 
    from 
      ws_prod()
  );
