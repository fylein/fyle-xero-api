from datetime import datetime
from typing import Dict, List

from apps.workspaces.models import Workspace

from fyle_accounting_mappings.models import ExpenseAttribute


class Base:
    """The base class for all API classes."""

    def __init__(self, attribute_type: str = None, query_params: dict = {}):
        self.attribute_type = attribute_type
        self.query_params = query_params
        self.connection = None
        self.workspace_id = None
        self.workspace = None


    def set_connection(self, connection):
        self.connection = connection


    def set_workspace_id(self, workspace_id):
        self.workspace_id = workspace_id
        self.workspace = Workspace.objects.filter(id=self.workspace_id).first()


    def format_date(self, last_synced_at: datetime) -> str:
        """
        Formats the date in the format of gte.2021-09-30T11:00:57.000Z
        """
        return 'gte.{}'.format(datetime.strftime(last_synced_at, '%Y-%m-%dT%H:%M:%S.000Z'))


    def __get_last_synced_at(self):
        """
        Returns the last time the API was synced.
        """
        return ExpenseAttribute.get_last_synced_at(self.attribute_type, self.workspace_id)


    def construct_query_params(self, sync_after: datetime = None) -> dict:
        """
        Constructs the query params for the API call.
        :return: dict
        """
        if self.attribute_type in ['CATEGORY', 'PROJECT']:
            params = {'order': 'updated_at.desc'}
            params.update(self.query_params)
            return params

        if sync_after:
            updated_at = self.format_date(sync_after)
        else:
            last_synced_record = self.__get_last_synced_at()
            updated_at = self.format_date(last_synced_record.updated_at) if last_synced_record else None

        params = {'order': 'updated_at.desc'}
        params.update(self.query_params)

        if sync_after:
            params['updated_at'] = updated_at
        elif updated_at and self.attribute_type not in ('CATEGORY', 'EMPLOYEE', 'CORPORATE_CARD', 'MERCHANT'):
            params['updated_at'] = updated_at

        return params


    def get_all_generator(self, sync_after: datetime = None):
        """
        Returns the generator for retrieving data from the API.
        :return: Generator
        """
        query_params = self.construct_query_params(sync_after)

        return self.connection.list_all(query_params)

    def post_bulk(self, payload: List[Dict]):
        """
        Post data to Fyle in Bulk
        """
        return self.connection.post_bulk({'data': payload})
    
    def post(self, payload: Dict):
        """
        Post date to Fyle
        """
        return self.connection.post({'data': payload})

    def bulk_create_or_update_expense_attributes(self, attributes: List[dict], update_existing: bool = False) -> None:
        """
        Bulk creates or updates expense attributes.
        :param attributes: List of expense attributes.
        :param update_existing: If True, updates/creates the existing expense attributes.
        """
        ExpenseAttribute.bulk_create_or_update_expense_attributes(
            attributes, self.attribute_type, self.workspace_id, update_existing
        )
    
    def bulk_update_deleted_expense_attributes(self) -> None:
        """
        Bulk updates the deleted expense attributes.
        """
        ExpenseAttribute.bulk_update_deleted_expense_attributes(self.attribute_type, self.workspace_id)

    def __construct_expense_attribute_objects(self, generator) -> List[dict]:
        """
        Constructs the expense attribute objects.
        :param generator: Generator
        :return: List of expense attribute objects.
        """
        attributes = []
        for items in generator:
            for row in items['data']:
                if self.attribute_is_valid(row):
                    attributes.append({
                        'attribute_type': self.attribute_type,
                        'display_name': self.attribute_type.replace('_', ' ').title(),
                        'value': row['name'],
                        'active': True,
                        'source_id': row['id']
                    })

        return attributes

    def attribute_is_valid(self, attribute):
        """
        Validate whether attribute is from the same org or not.
        """
        if hasattr(self.workspace, 'fyle_org_id'):
            return attribute['org_id'] == self.workspace.fyle_org_id

        elif hasattr(self.workspace, 'org_id'):
            return attribute['org_id'] == self.workspace.org_id


    def sync(self, sync_after: datetime = None) -> None:
        """
        Syncs the latest API data to DB.
        """
        generator = self.get_all_generator(sync_after)
        attributes = self.__construct_expense_attribute_objects(generator)
        self.bulk_create_or_update_expense_attributes(attributes)

    def get_by_id(self, id):
        """
        Get Single Resource object by ID
        :param id: Resource object ID
        :return: Resource Object
        """
        return self.connection.get_by_id(id)['data']
