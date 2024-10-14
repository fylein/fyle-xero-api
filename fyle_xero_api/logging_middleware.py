import json
import logging
import traceback

from django.conf import settings
from django.http import HttpResponse

logger = logging.getLogger(__name__)
logger.level = logging.INFO


class ErrorHandlerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        if not settings.DEBUG:
            if exception:
                message = {
                    "url": request.build_absolute_uri(),
                    "error": repr(exception),
                    "traceback": traceback.format_exc(),
                }
                logger.error(str(message).replace("\n", ""))

            return HttpResponse("Error processing the request.", status=500)


class LogPostRequestMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method in ['POST', 'PUT']:
            try:
                body_unicode = request.body.decode('utf-8')
                request_body = json.loads(body_unicode)
                logger.info("POST request to %s: %s", request.path, request_body)
            except (json.JSONDecodeError, UnicodeDecodeError):
                logger.warning("Failed to decode POST request body for %s", request.path)
            except Exception as e:
                logger.info('Something went wrong when logging post call - %s', e)
        response = self.get_response(request)
        return response
