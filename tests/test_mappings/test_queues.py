from apps.mappings.queue import construct_tasks_and_chain_import_fields_to_fyle
from apps.workspaces.models import WorkspaceGeneralSettings


def test_construct_tasks_and_chain_import_fields_to_fyle(
    db,
    mocker,
    create_temp_workspace,
    add_xero_credentials,
    create_mapping_setting
):
    workspace_id = 3
    mocker.patch('apps.mappings.queue.chain_import_fields_to_fyle')

    WorkspaceGeneralSettings.objects.create(
        workspace_id=workspace_id,
        import_suppliers_as_merchants=True,
        import_categories=True,
        import_tax_codes=True,
        charts_of_accounts=['Income'],
        import_customers=True
    )

    construct_tasks_and_chain_import_fields_to_fyle(workspace_id)
