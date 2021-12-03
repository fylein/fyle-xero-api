-- We've added enable_payments_to_account to the detail column in this commit
-- We query to xero api with modified after param which is updated_at of the latest destination attribute

-- So, we are setting updated at of destination attributes to workspace created time to retrieve even older records 
-- even though they exist in db.

-- Note: This will not be 100% accurate since there can be accounts created even before the workspace was created

rollback; begin;

with ws as (
  select 
    w.id as w_id,
    w.created_at as workspace_created_at
  from workspaces w
)
update destination_attributes 
    set updated_at = ws.workspace_created_at
from ws
    where workspace_id = ws.w_id and attribute_type = 'ACCOUNT';
