DROP FUNCTION if exists reset_workspace;

CREATE OR REPLACE FUNCTION reset_workspace(IN _workspace_id integer) RETURNS void AS $$
DECLARE
  rcount integer;
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

--   DELETE
--   FROM last_export_details l
--   where l.workspace_id = _workspace_id;
--   GET DIAGNOSTICS rcount = ROW_COUNT;
--   RAISE NOTICE 'Deleted % errors', rcount;

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
  FROM xero_expense_lineitems qel
  WHERE qel.xero_expense_id IN (
      SELECT qe.id FROM xero_expenses qe WHERE qe.expense_group_id IN (
          SELECT eg.id FROM expense_groups eg WHERE eg.workspace_id = _workspace_id
      )
  );
  GET DIAGNOSTICS rcount = ROW_COUNT;
  RAISE NOTICE 'Deleted % xero_expense_lineitems', rcount;

  DELETE
  FROM xero_expenses qe
  WHERE qe.expense_group_id IN (
      SELECT eg.id FROM expense_groups eg WHERE eg.workspace_id = _workspace_id
  );
  GET DIAGNOSTICS rcount = ROW_COUNT;
  RAISE NOTICE 'Deleted % xero_expenses', rcount;

  DELETE
  FROM cheque_lineitems cl
  WHERE cl.cheque_id IN (
      SELECT c.id FROM cheques c WHERE c.expense_group_id IN (
          SELECT eg.id FROM expense_groups eg WHERE eg.workspace_id = _workspace_id
      )
  );
  GET DIAGNOSTICS rcount = ROW_COUNT;
  RAISE NOTICE 'Deleted % cheque_lineitems', rcount;

  DELETE
  FROM cheques c
  WHERE c.expense_group_id IN (
      SELECT eg.id FROM expense_groups eg WHERE eg.workspace_id = _workspace_id
  );
  GET DIAGNOSTICS rcount = ROW_COUNT;
  RAISE NOTICE 'Deleted % cheques', rcount;

  DELETE
  FROM credit_card_purchase_lineitems ccpl
  WHERE ccpl.credit_card_purchase_id IN (
      SELECT ccp.id FROM credit_card_purchases ccp WHERE ccp.expense_group_id IN (
          SELECT eg.id FROM expense_groups eg WHERE eg.workspace_id = _workspace_id
      )
  );
  GET DIAGNOSTICS rcount = ROW_COUNT;
  RAISE NOTICE 'Deleted % credit_card_purchase_lineitems', rcount;

  DELETE
  FROM credit_card_purchases ccp
  WHERE ccp.expense_group_id IN (
      SELECT eg.id FROM expense_groups eg WHERE eg.workspace_id = _workspace_id
  );
  GET DIAGNOSTICS rcount = ROW_COUNT;
  RAISE NOTICE 'Deleted % credit_card_purchases', rcount;

  DELETE
  FROM journal_entry_lineitems jel
  WHERE jel.journal_entry_id IN (
      SELECT c.id FROM journal_entries c WHERE c.expense_group_id IN (
          SELECT eg.id FROM expense_groups eg WHERE eg.workspace_id = _workspace_id
      )
  );
  GET DIAGNOSTICS rcount = ROW_COUNT;
  RAISE NOTICE 'Deleted % journal_entry_lineitems', rcount;

  DELETE
  FROM journal_entries je
  WHERE je.expense_group_id IN (
      SELECT eg.id FROM expense_groups eg WHERE eg.workspace_id = _workspace_id
  );
  GET DIAGNOSTICS rcount = ROW_COUNT;
  RAISE NOTICE 'Deleted % journal_entries', rcount;

  DELETE
  FROM bill_payment_lineitems bpl
  WHERE bpl.bill_payment_id IN (
      SELECT bp.id FROM bill_payments bp WHERE bp.expense_group_id IN (
          SELECT eg.id FROM expense_groups eg WHERE eg.workspace_id = _workspace_id
      )
  );
  GET DIAGNOSTICS rcount = ROW_COUNT;
  RAISE NOTICE 'Deleted % bill_payment_lineitems', rcount;

  DELETE
  FROM bill_payments bp
  WHERE bp.expense_group_id IN (
      SELECT eg.id FROM expense_groups eg WHERE eg.workspace_id = _workspace_id
  );
  GET DIAGNOSTICS rcount = ROW_COUNT;
  RAISE NOTICE 'Deleted % bill_payments', rcount;

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
  FROM employee_mappings em
  WHERE em.workspace_id = _workspace_id;
  GET DIAGNOSTICS rcount = ROW_COUNT;
  RAISE NOTICE 'Deleted % employee_mappings', rcount;

  DELETE
  FROM category_mappings cm
  WHERE cm.workspace_id = _workspace_id;
  GET DIAGNOSTICS rcount = ROW_COUNT;
  RAISE NOTICE 'Deleted % category_mappings', rcount;

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

--   DELETE
--   FROM expense_group_settings egs
--   WHERE egs.workspace_id = _workspace_id;
--   GET DIAGNOSTICS rcount = ROW_COUNT;
--   RAISE NOTICE 'Deleted % expense_group_settings', rcount;

--   DELETE
--   FROM fyle_credentials fc
--   WHERE fc.workspace_id = _workspace_id;
--   GET DIAGNOSTICS rcount = ROW_COUNT;
--   RAISE NOTICE 'Deleted % fyle_credentials', rcount;

  DELETE
  FROM xero_credentials qc
  WHERE qc.workspace_id = _workspace_id;
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
  FROM workspace_schedules wsch
  WHERE wsch.workspace_id = _workspace_id;
  GET DIAGNOSTICS rcount = ROW_COUNT;
  RAISE NOTICE 'Deleted % workspace_schedules', rcount;

  DELETE
  FROM django_q_schedule dqs
  WHERE dqs.args = _workspace_id::varchar(255);
  GET DIAGNOSTICS rcount = ROW_COUNT;
  RAISE NOTICE 'Deleted % django_q_schedule', rcount;

--   DELETE
--   FROM auth_tokens aut
--   WHERE aut.user_id IN (
--       SELECT u.id FROM users u WHERE u.id IN (
--           SELECT wu.user_id FROM workspaces_user wu WHERE workspace_id = _workspace_id
--       )
--   );
--   GET DIAGNOSTICS rcount = ROW_COUNT;
--   RAISE NOTICE 'Deleted % auth_tokens', rcount;

--   DELETE
--   FROM workspaces_user wu
--   WHERE workspace_id = _workspace_id;
--   GET DIAGNOSTICS rcount = ROW_COUNT;
--   RAISE NOTICE 'Deleted % workspaces_user', rcount;

--   DELETE
--   FROM users u
--   WHERE u.id IN (
--       SELECT wu.user_id FROM workspaces_user wu WHERE workspace_id = _workspace_id
--   );
--   GET DIAGNOSTICS rcount = ROW_COUNT;
--   RAISE NOTICE 'Deleted % users', rcount;

--   DELETE
--   FROM workspaces w
--   WHERE w.id = _workspace_id;
--   GET DIAGNOSTICS rcount = ROW_COUNT;
--   RAISE NOTICE 'Deleted % workspaces', rcount;

    UPDATE workspaces
    SET onboarding_state = 'CONNECTION', last_synced_at = null, destination_synced_at =  null, source_synced_at = null, xero_realm_id = null
    WHERE id = _workspace_id;

    UPDATE last_export_details
    SET last_exported_at = null, export_mode = null, total_expense_groups_count = null, successful_expense_groups_count = null, failed_expense_groups_count = null
    WHERE workspace_id = _workspace_id;

RETURN;
END
$$ LANGUAGE plpgsql;
