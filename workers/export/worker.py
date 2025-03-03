import os
import signal

from .actions import handle_exports

from fyle_accounting_library.fyle_platform.enums import RoutingKeyEnum
from fyle_accounting_library.rabbitmq.models import FailedEvent
from consumer.event_consumer import EventConsumer
from common import log
from common.qconnector import RabbitMQConnector
from common.event import BaseEvent


logger = log.get_logger(__name__)


class ExportWorker(EventConsumer):
    def __init__(self, *, qconnector_cls, **kwargs):
        super().__init__(qconnector_cls=qconnector_cls, **kwargs)

    def process_message(self, routing_key, event: BaseEvent, delivery_tag):
        try:
            payload_dict = event.new
            logger.info('Processing message for workspace - %s with routing key - %s and payload - %s with delivery tag - %s', payload_dict['workspace_id'], routing_key, payload_dict, delivery_tag)

            # We're gonna retry failed events since this queue is primarily webhook calls from Fyle, if this is a scheduled export, it doesn't necessarily needs to be retried
            retry_count = payload_dict.get('retry_count', 0)
            if retry_count >= 2:
                logger.error('Message failed after %s retries, dropping message', retry_count)
                self.qconnector.reject_message(delivery_tag, requeue=False)
                return

            handle_exports(payload_dict['data'])
            self.qconnector.acknowledge_message(delivery_tag)
        except Exception as e:
            self.handle_exception(routing_key, payload_dict, e, delivery_tag)

    def handle_exception(self, routing_key, payload_dict, error, delivery_tag):
        logger.error('Error while handling exports for workspace - %s, error: %s', payload_dict, str(error))

        payload_dict['retry_count'] = payload_dict.get('retry_count', 0) + 1

        FailedEvent.objects.create(
            routing_key=routing_key,
            payload=payload_dict,
            error_traceback=str(error),
            workspace_id=payload_dict['workspace_id'] if payload_dict.get('workspace_id') else None
        )

        if payload_dict['retry_count'] < 2:
            self.qconnector.reject_message(delivery_tag, requeue=True)
        else:
            self.qconnector.reject_message(delivery_tag, requeue=False)

    def shutdown(self, _, __):
        logger.info('Received signal %s, shutting down...', _)
        super().shutdown()


def consume():
    rabbitmq_url = os.environ.get('RABBITMQ_URL')

    export_worker = ExportWorker(
        rabbitmq_url=rabbitmq_url,
        rabbitmq_exchange='xero_exchange',
        queue_name='xero_p1_exports_queue',
        binding_keys=RoutingKeyEnum.EXPORT,
        qconnector_cls=RabbitMQConnector,
        event_cls=BaseEvent
    )

    signal.signal(signal.SIGTERM, export_worker.shutdown)
    signal.signal(signal.SIGINT, export_worker.shutdown)

    export_worker.connect()
    export_worker.start_consuming()


if __name__ == "__main__":
    consume()
