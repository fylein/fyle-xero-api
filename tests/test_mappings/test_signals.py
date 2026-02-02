from datetime import datetime

import pytest
from django_q.models import Schedule
from fyle_accounting_mappings.models import Mapping, MappingSetting

from apps.mappings.models import TenantMapping
from apps.workspaces.models import LastExportDetail, Workspace, WorkspaceGeneralSettings
from tests.test_fyle.fixtures import data as fyle_data


def test_run_post_mapping_settings_triggers(db, mocker, test_connection):
    mocker.patch(
        "fyle_integrations_platform_connector.apis.ExpenseCustomFields.post",
        return_value=[],
    )

    mocker.patch(
        "fyle.platform.apis.v1.admin.ExpenseFields.list_all",
        return_value=fyle_data["get_all_expense_fields"],
    )

    workspace_id = 1

    mapping_setting = MappingSetting(
        source_field="PROJECT",
        destination_field="PROJECT",
        workspace_id=workspace_id,
        import_to_fyle=True,
        is_custom=False,
    )

    mapping_setting.save()

    schedule = Schedule.objects.filter(
        func="apps.mappings.queue.construct_tasks_and_chain_import_fields_to_fyle",
        args="{}".format(workspace_id),
    ).first()

    assert schedule.func == "apps.mappings.queue.construct_tasks_and_chain_import_fields_to_fyle"
    assert schedule.args == "1"

    mapping_setting = MappingSetting(
        source_field="COST_CENTER",
        destination_field="CLASS",
        workspace_id=workspace_id,
        import_to_fyle=True,
        is_custom=False,
    )
    mapping_setting.save()

    schedule = Schedule.objects.filter(
        func="apps.mappings.queue.construct_tasks_and_chain_import_fields_to_fyle",
        args="{}".format(workspace_id),
    ).first()

    assert schedule.func == "apps.mappings.queue.construct_tasks_and_chain_import_fields_to_fyle"
    assert schedule.args == "1"

    mapping_setting = MappingSetting(
        source_field="SAMPLEs",
        destination_field="SAMPLEs",
        workspace_id=workspace_id,
        import_to_fyle=True,
        is_custom=True,
    )
    mapping_setting.save()

    schedule = Schedule.objects.filter(
        func="apps.mappings.queue.construct_tasks_and_chain_import_fields_to_fyle",
        args="{}".format(workspace_id),
    ).first()

    assert (
        schedule.func == "apps.mappings.queue.construct_tasks_and_chain_import_fields_to_fyle"
    )
    assert schedule.args == "1"

    mapping_setting = MappingSetting.objects.filter(
        source_field="PROJECT", workspace_id=workspace_id
    ).delete()
    workspace_general_settings = WorkspaceGeneralSettings.objects.filter(
        workspace_id=workspace_id
    ).first()
    workspace_general_settings.import_categories = False
    workspace_general_settings.import_vendors_as_merchants = False
    workspace_general_settings.save()

    mapping_setting = MappingSetting(
        source_field="LOLOOO",
        destination_field="HEHEHE",
        workspace_id=workspace_id,
        import_to_fyle=True,
        is_custom=False,
    )
    mapping_setting.save()

    schedule = Schedule.objects.filter(
        func="apps.mappings.queue.construct_tasks_and_chain_import_fields_to_fyle",
        args="{}".format(workspace_id),
    ).first()

    assert schedule.func == "apps.mappings.queue.construct_tasks_and_chain_import_fields_to_fyle"


def test_run_pre_mapping_settings_triggers(db, mocker, test_connection):
    mocker.patch(
        "fyle_integrations_platform_connector.apis.ExpenseCustomFields.post",
        return_value=[],
    )

    mocker.patch(
        "fyle.platform.apis.v1.admin.ExpenseFields.list_all",
        return_value=fyle_data["get_all_expense_fields"],
    )

    workspace_id = 1

    custom_mappings = Mapping.objects.filter(
        workspace_id=workspace_id, source_type="CUSTOM_INTENTs"
    ).count()
    assert custom_mappings == 0

    mapping_setting = MappingSetting(
        source_field="CUSTOM_INTENTs",
        destination_field="CUSTOM_INTENTs",
        workspace_id=workspace_id,
        import_to_fyle=True,
        is_custom=True,
    )
    mapping_setting.save()

    custom_mappings = Mapping.objects.last()

    custom_mappings = Mapping.objects.filter(
        workspace_id=workspace_id, source_type="CUSTOM_INTENTs"
    ).count()
    assert custom_mappings == 0

    mapping = Mapping.objects.filter(
        workspace_id=workspace_id, source_type="CATEGORY", source_id=112
    ).first()
    mapping.created_at = datetime.now()
    mapping.save()


def test_run_post_tenant_mapping_trigger(db, test_connection, mocker):
    mocker.patch("apps.mappings.signals.publish_to_rabbitmq")

    workspace = Workspace.objects.create(
        id=97,
        name="Fyle for sample",
        fyle_org_id="Testing",
    )
    workspace.save()

    tenant_mapping = TenantMapping(
        tenant_name="sample", tenant_id="wertyui", workspace=workspace
    )
    tenant_mapping.save()
    LastExportDetail.objects.create(workspace=workspace)


@pytest.mark.django_db()
def test_patch_integration_settings_on_card_mapping(test_connection, mocker, add_corporate_card_attributes):
    """
    Test patch_corporate_card_integration_settings is called when corporate card mapping is created
    """
    workspace_id = 1

    # Get attributes from fixture
    corporate_card = add_corporate_card_attributes['corporate_card']
    category = add_corporate_card_attributes['category']
    bank_account = add_corporate_card_attributes['bank_account']
    account = add_corporate_card_attributes['account']

    mock_patch = mocker.patch('apps.mappings.signals.patch_corporate_card_integration_settings')
    mapping = Mapping(source_type='CORPORATE_CARD', destination_type='BANK_ACCOUNT',
                     source_id=corporate_card.id, destination_id=bank_account.id, workspace_id=workspace_id)
    mapping.save()
    mock_patch.assert_called_once_with(workspace_id=workspace_id)

    mock_patch.reset_mock()
    mapping = Mapping(source_type='CATEGORY', destination_type='ACCOUNT',
                     source_id=category.id, destination_id=account.id, workspace_id=workspace_id)
    mapping.save()
    mock_patch.assert_not_called()
