def test_get_queryset(api_client, test_connection):
    workspace_id = 1

    access_token = test_connection.access_token
    url = '/api/workspaces/{}/tasks/all/'.format(workspace_id)

    api_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token))

    response = api_client.get(url, {
        'expense_group_ids': '4',
        'task_type': 'CREATING_EXPENSE',
        'status': 'ALL'
    })
    assert response.status_code==200
