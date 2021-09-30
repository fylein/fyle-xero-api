import os

import sentry_sdk

from sentry_sdk.integrations.django import DjangoIntegration

class Sentry:

    @staticmethod
    def init():
        sentry_sdk.init(
            dsn=os.environ.get('SENTRY_DSN'),
            send_default_pii=True,
            integrations=[DjangoIntegration()],
            environment='xero-api',
            traces_sampler=Sentry.traces_sampler,
            release=os.environ.get('RELEASE'),
            attach_stacktrace=True,
            request_bodies='small',
            in_app_include=['apps.users',
            'apps.workspaces',
            'apps.mappings',
            'apps.fyle',
            'apps.xero',
            'apps.tasks',
            'fyle_rest_auth',
            'fyle_accounting_mappings'],
        )

    @staticmethod
    def traces_sampler(sampling_context):
        # avoiding ready APIs in performance tracing
        if sampling_context.get('wsgi_environ') is not None:
            if sampling_context['wsgi_environ']['PATH_INFO'] in ['/ready']:
                return 0

        return 0.2
