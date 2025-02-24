import os
import json
import signal

from consumer.event_consumer import EventConsumer
from common import log
from common.qconnector import RabbitMQConnector

from .actions import handle_exports


logger = log.get_logger(__name__)


class ExportWorker(EventConsumer):
    def __init__(self, *, qconnector_cls, **kwargs):
        super().__init__(qconnector_cls=qconnector_cls, event_cls=None, **kwargs)

    def process_message(self, _, payload_dict):
        try:
            handle_exports(payload_dict['data'])
        except Exception as e:
            logger.info('Error while handling exports for workspace - %s, error: %s', payload_dict, str(e))

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
        binding_keys='exports.p1',
        qconnector_cls=RabbitMQConnector
    )

    signal.signal(signal.SIGTERM, export_worker.shutdown)
    signal.signal(signal.SIGINT, export_worker.shutdown)

    export_worker.connect()
    export_worker.start_consuming()


if __name__ == "__main__":
    consume()
