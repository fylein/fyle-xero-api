# Pull python base image
FROM python:3.10-slim

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get -y install libpq-dev gcc && apt-get install git curl postgresql-client -y --no-install-recommends

# Installing requirements
COPY requirements.txt /tmp/requirements.txt
RUN pip install --upgrade pip && pip install -U pip wheel setuptools && pip install -r /tmp/requirements.txt && pip install flake8

# Copy Project to the container
RUN mkdir -p /fyle-xero-api
COPY . /fyle-xero-api/
WORKDIR /fyle-xero-api

#================================================================
# Set default GID if not provided during build
#================================================================
ARG SERVICE_GID=1001

#================================================================
# Setup non-root user and permissions
#================================================================
RUN groupadd -r -g ${SERVICE_GID} xero_api_service && \
    useradd -r -g xero_api_service xero_api_user && \
    chown -R xero_api_user:xero_api_service /fyle-xero-api

# Switch to non-root user
USER xero_api_user


# Do linting checks
RUN flake8 .

# Expose development port
EXPOSE 8000

# Run development server
CMD /bin/bash run.sh
