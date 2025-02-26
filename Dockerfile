# Pull python base image
FROM python:3.10-slim

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get -y install libpq-dev gcc && apt-get install git -y --no-install-recommends

ARG CI
RUN if [ "$CI" = "ENABLED" ]; then \
        apt-get update; \
        apt-get install lsb-release gnupg2 wget -y --no-install-recommends; \
        apt-cache search postgresql | grep postgresql; \
        sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'; \
        wget --no-check-certificate --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add - ; \
        apt -y update; \
        apt-get install postgresql-15 -y --no-install-recommends; \
    fi

# Installing requirements
COPY requirements.txt /tmp/requirements.txt
RUN pip install --upgrade pip && pip install -r /tmp/requirements.txt && pip install flake8


# Copy Project to the container
RUN mkdir -p /fyle-xero-api
COPY . /fyle-xero-api/
WORKDIR /fyle-xero-api

# Do linting checks
RUN flake8 . --exclude=fyle_integrations_platform_connector/,fylesdk/,fyle_accounting_mappings/,fyle_accounting_library/,common/,consumer/

# Expose development port
EXPOSE 8000

# Run development server
CMD /bin/bash run.sh
