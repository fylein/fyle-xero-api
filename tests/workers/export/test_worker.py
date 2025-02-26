import json
import pytest
from unittest.mock import Mock, patch

from workers.export.worker import ExportWorker
from fyle_accounting_library.rabbitmq.models import FailedEvent


@pytest.fixture
def mock_qconnector():
    return Mock()


@pytest.fixture
def export_worker(mock_qconnector):
    worker = ExportWorker(
        rabbitmq_url='mock_url',
        rabbitmq_exchange='mock_exchange',
        queue_name='mock_queue',
        binding_keys=['mock.binding.key'],
        qconnector_cls=Mock(return_value=mock_qconnector)
    )
    worker.qconnector = mock_qconnector
    return worker


@pytest.mark.django_db
def test_process_message_success(export_worker):
    with patch('workers.export.worker.handle_exports') as mock_handle_exports:
        mock_handle_exports.side_effect = Exception('Test error')

        routing_key = 'test.routing.key'
        payload_dict = {
            'data': {'some': 'data'},
            'workspace_id': 123
        }

        # The process_message should handle the exception internally
        export_worker.process_message(routing_key, payload_dict)

        mock_handle_exports.assert_called_once_with({'some': 'data'})


@pytest.mark.django_db
def test_handle_exception(export_worker):
    routing_key = 'test.routing.key'
    payload_dict = {
        'data': {'some': 'data'},
        'workspace_id': 123
    }
    error = Exception('Test error')

    export_worker.handle_exception(routing_key, payload_dict, error)

    failed_event = FailedEvent.objects.get(
        routing_key=routing_key,
        workspace_id=123
    )
    assert failed_event.payload == payload_dict
    assert failed_event.error_traceback == 'Test error'


def test_start_consuming(export_worker):
    mock_payload = json.dumps({'test': 'data'})

    # Simulate the callback being called
    export_worker.qconnector.consume_stream.side_effect = lambda callback_fn: callback_fn('test.key', mock_payload)

    with patch.object(export_worker, 'process_message') as mock_process:
        export_worker.start_consuming()

        mock_process.assert_called_once_with('test.key', {'test': 'data'})


def test_shutdown(export_worker):
    # Test shutdown with signal arguments
    with patch.object(export_worker, 'shutdown', wraps=export_worker.shutdown) as mock_shutdown:
        export_worker.shutdown(signum=15, frame=None)  # SIGTERM = 15
        mock_shutdown.assert_called_once_with(signum=15, frame=None)

    # Test shutdown without arguments
    with patch.object(export_worker, 'shutdown', wraps=export_worker.shutdown) as mock_shutdown:
        export_worker.shutdown()
        mock_shutdown.assert_called_once_with()


@patch('workers.export.worker.signal.signal')
@patch('workers.export.worker.ExportWorker')
def test_consume(mock_worker_class, mock_signal):
    mock_worker = Mock()
    mock_worker_class.return_value = mock_worker

    with patch.dict('os.environ', {'RABBITMQ_URL': 'test_url'}):
        from workers.export.worker import consume
        consume()

    mock_worker.connect.assert_called_once()
    mock_worker.start_consuming.assert_called_once()
    assert mock_signal.call_count == 2  # Called for both SIGTERM and SIGINT
