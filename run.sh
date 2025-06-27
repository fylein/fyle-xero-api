#!/bin/bash

if [ "$STRICT_MODE" == "false" ]; then
  set -e
fi

# Run db migrations
python manage.py migrate

# Creating the cache table
python manage.py createcachetable --database cache_db

# Running development server
gunicorn -c gunicorn_config.py fyle_xero_api.wsgi -b 0.0.0.0:8000
