DROP FUNCTION if exists delete_workspace_v2;

CREATE OR REPLACE FUNCTION delete_workspace_v2(IN _workspace_id integer) RETURNS void AS $$
DECLARE
  rcount integer;
  _org_id varchar(255);
BEGIN
  RAISE NOTICE 'Deleting data from workspace % ', _workspace_id;

  DELETE
  FROM task_logs tl
  WHERE tl.workspace_id = _workspace_id;
  GET DIAGNOSTICS rcount = ROW_COUNT;
  RAISE NOTICE 'Deleted % task_logs', rcount;

  DELETE
  FROM errors er
  where er.workspace_id = _workspace_id;
  GET DIAGNOSTICS rcount = ROW_COUNT;
  RAISE NOTICE 'Deleted % errors', rcount;

  DELETE
  FROM last_export_details l
  where l.workspace_id = _workspace_id;
  GET DIAGNOSTICS rcount = ROW_COUNT;
  RAISE NOTICE 'Deleted % last_export_details', rcount;

  DELETE
  FROM bill_lineitems bl
  WHERE bl.bill_id IN (
      SELECT b.id FROM bills b WHERE b.expense_group_id IN (
          SELECT eg.id FROM expense_groups eg WHERE eg.workspace_id = _workspace_id
      ) 
  );
  GET DIAGNOSTICS rcount = ROW_COUNT;
  RAISE NOTICE 'Deleted % bill_lineitems', rcount;

  DELETE
  FROM bills b
  WHERE b.expense_group_id IN (
      SELECT eg.id FROM expense_groups eg WHERE eg.workspace_id = _workspace_id
  );
  GET DIAGNOSTICS rcount = ROW_COUNT;
  RAISE NOTICE 'Deleted % bills', rcount;

  DELETE
  FROM bank_transaction_lineitems btl
  WHERE btl.bank_transaction_id IN (
      SELECT bt.id FROM bank_transactions bt WHERE bt.expense_group_id IN (
          SELECT eg.id FROM expense_groups eg WHERE eg.workspace_id = _workspace_id
      )
  );
  GET DIAGNOSTICS rcount = ROW_COUNT;
  RAISE NOTICE 'Deleted % bank_transaction_lineitems', rcount;

  DELETE
  FROM bank_transactions bt
  WHERE bt.expense_group_id IN (
      SELECT eg.id FROM expense_groups eg WHERE eg.workspace_id = _workspace_id
  );
  GET DIAGNOSTICS rcount = ROW_COUNT;
  RAISE NOTICE 'Deleted % bank_transactions', rcount;

  DELETE
  FROM payments p
  WHERE p.workspace_id = _workspace_id;
  GET DIAGNOSTICS rcount = ROW_COUNT;
  RAISE NOTICE 'Deleted % payments', rcount;

  DELETE
  FROM reimbursements r
  WHERE r.workspace_id = _workspace_id;
  GET DIAGNOSTICS rcount = ROW_COUNT;
  RAISE NOTICE 'Deleted % reimbursements', rcount;

  DELETE
  FROM expenses e
  WHERE e.id IN (
      SELECT expense_id FROM expense_groups_expenses ege WHERE ege.expensegroup_id IN (
          SELECT eg.id FROM expense_groups eg WHERE eg.workspace_id = _workspace_id
      )
  );
  GET DIAGNOSTICS rcount = ROW_COUNT;
  RAISE NOTICE 'Deleted % expenses', rcount;

  DELETE
  FROM expense_groups_expenses ege
  WHERE ege.expensegroup_id IN (
      SELECT eg.id FROM expense_groups eg WHERE eg.workspace_id = _workspace_id
  );
  GET DIAGNOSTICS rcount = ROW_COUNT;
  RAISE NOTICE 'Deleted % expense_groups_expenses', rcount;

  DELETE
  FROM expense_groups eg
  WHERE eg.workspace_id = _workspace_id;
  GET DIAGNOSTICS rcount = ROW_COUNT;
  RAISE NOTICE 'Deleted % expense_groups', rcount;

  DELETE
  FROM tenant_mappings tm
  WHERE tm.workspace_id = _workspace_id;
  GET DIAGNOSTICS rcount = ROW_COUNT;
  RAISE NOTICE 'Deleted % tenant_mappings', rcount;

  DELETE
  FROM mappings m
  WHERE m.workspace_id = _workspace_id;
  GET DIAGNOSTICS rcount = ROW_COUNT;
  RAISE NOTICE 'Deleted % mappings', rcount;

  DELETE
  FROM mapping_settings ms
  WHERE ms.workspace_id = _workspace_id;
  GET DIAGNOSTICS rcount = ROW_COUNT;
  RAISE NOTICE 'Deleted % mapping_settings', rcount;

  DELETE
  FROM general_mappings gm
  WHERE gm.workspace_id = _workspace_id;
  GET DIAGNOSTICS rcount = ROW_COUNT;
  RAISE NOTICE 'Deleted % general_mappings', rcount;

  DELETE
  FROM workspace_general_settings wgs
  WHERE wgs.workspace_id = _workspace_id;
  GET DIAGNOSTICS rcount = ROW_COUNT;
  RAISE NOTICE 'Deleted % workspace_general_settings', rcount;

  DELETE
  FROM expense_group_settings egs
  WHERE egs.workspace_id = _workspace_id;
  GET DIAGNOSTICS rcount = ROW_COUNT;
  RAISE NOTICE 'Deleted % expense_group_settings', rcount;

  DELETE
  FROM fyle_credentials fc
  WHERE fc.workspace_id = _workspace_id;
  GET DIAGNOSTICS rcount = ROW_COUNT;
  RAISE NOTICE 'Deleted % fyle_credentials', rcount;

  DELETE
  FROM xero_credentials xc
  WHERE xc.workspace_id = _workspace_id;
  GET DIAGNOSTICS rcount = ROW_COUNT;
  RAISE NOTICE 'Deleted % xero_credentials', rcount;

  DELETE
  FROM expense_attributes ea
  WHERE ea.workspace_id = _workspace_id;
  GET DIAGNOSTICS rcount = ROW_COUNT;
  RAISE NOTICE 'Deleted % expense_attributes', rcount;

  DELETE
  FROM destination_attributes da
  WHERE da.workspace_id = _workspace_id;
  GET DIAGNOSTICS rcount = ROW_COUNT;
  RAISE NOTICE 'Deleted % destination_attributes', rcount;

  DELETE
  FROM expense_fields ef
  WHERE ef.workspace_id = _workspace_id;
  GET DIAGNOSTICS rcount = ROW_COUNT;
  RAISE NOTICE 'Deleted % expense_fields', rcount;

  DELETE
  FROM workspace_schedules wsch
  WHERE wsch.workspace_id = _workspace_id;
  GET DIAGNOSTICS rcount = ROW_COUNT;
  RAISE NOTICE 'Deleted % workspace_schedules', rcount;

  DELETE
  FROM django_q_schedule dqs
  WHERE dqs.args = _workspace_id::varchar(255);
  GET DIAGNOSTICS rcount = ROW_COUNT;
  RAISE NOTICE 'Deleted % django_q_schedule', rcount;

  DELETE
  FROM auth_tokens aut
  WHERE aut.user_id IN (
      SELECT u.id FROM users u WHERE u.id IN (
          SELECT wu.user_id FROM workspaces_user wu WHERE workspace_id = _workspace_id
      )
  );
  GET DIAGNOSTICS rcount = ROW_COUNT;
  RAISE NOTICE 'Deleted % auth_tokens', rcount;

  DELETE
  FROM workspaces_user wu
  WHERE workspace_id = _workspace_id;
  GET DIAGNOSTICS rcount = ROW_COUNT;
  RAISE NOTICE 'Deleted % workspaces_user', rcount;

  DELETE
  FROM users u
  WHERE u.id IN (
      SELECT wu.user_id FROM workspaces_user wu WHERE workspace_id = _workspace_id
  );
  GET DIAGNOSTICS rcount = ROW_COUNT;
  RAISE NOTICE 'Deleted % users', rcount;

  _org_id := (SELECT fyle_org_id FROM workspaces WHERE id = _workspace_id);

  DELETE
  FROM workspaces w
  WHERE w.id = _workspace_id;
  GET DIAGNOSTICS rcount = ROW_COUNT;
  RAISE NOTICE 'Deleted % workspaces', rcount;

  RAISE NOTICE E'\n\n\n\n\n\n\n\n\nSwitch to integration_settings db and run the below query to delete the integration';
  RAISE NOTICE E'\\c integration_settings; \n\n begin; select delete_integration(''%'');\n\n\n\n\n\n\n\n\n\n\n', _org_id;

  RAISE NOTICE E'\n\n\n\n\n\n\n\n\nSwitch to prod db and run the below query to update the subscription';
  RAISE NOTICE E'begin; update platform_schema.admin_subscriptions set is_enabled = false where org_id = ''%'';\n\n\n\n\n\n\n\n\n\n\n', _org_id;

RETURN;
END
$$ LANGUAGE plpgsql;
