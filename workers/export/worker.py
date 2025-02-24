import os
import json
import signal

from .actions import handle_exports

from fyle_accounting_library.fyle_platform.enums import RoutingKeyEnum
from fyle_accounting_library.rabbitmq.models import FailedEvent
from consumer.event_consumer import EventConsumer
from common import log
from common.qconnector import RabbitMQConnector



logger = log.get_logger(__name__)


class ExportWorker(EventConsumer):
    def __init__(self, *, qconnector_cls, **kwargs):
        super().__init__(qconnector_cls=qconnector_cls, event_cls=None, **kwargs)

    def process_message(self, routing_key, payload_dict):
        try:
            handle_exports(payload_dict['data'])
            raise Exception('Test error')
        except Exception as e:
            self.handle_exception(routing_key, payload_dict, e)

    def handle_exception(self, routing_key, payload_dict, error):
        logger.error('Error while handling exports for workspace - %s, error: %s', payload_dict, str(error))
        FailedEvent.objects.create(
            routing_key=routing_key,
            payload=payload_dict,
            error_traceback=str(error),
            workspace_id=payload_dict['workspace_id'] if payload_dict.get('workspace_id') else None
        )

    def start_consuming(self):
        def stream_consumer(routing_key, payload):
            payload_dict = json.loads(payload)

            self.process_message(routing_key, payload_dict)
            self.check_shutdown()

        self.qconnector.consume_stream(
            callback_fn=stream_consumer
        )

    def shutdown(self, signum=None, frame=None):
        """Override shutdown to handle signal arguments"""
        super().shutdown()


def consume():
    rabbitmq_url = os.environ.get('RABBITMQ_URL')

    export_worker = ExportWorker(
        rabbitmq_url=rabbitmq_url,
        rabbitmq_exchange='xero_exchange',
        queue_name='xero_p1_exports_queue',
        binding_keys=RoutingKeyEnum.EXPORT,
        qconnector_cls=RabbitMQConnector
    )

    signal.signal(signal.SIGTERM, export_worker.shutdown)
    signal.signal(signal.SIGINT, export_worker.shutdown)

    export_worker.connect()
    export_worker.start_consuming()


if __name__ == "__main__":
    consume()
