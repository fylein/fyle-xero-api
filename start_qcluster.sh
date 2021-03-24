# Creating the cache table
python manage.py createcachetable --database cache_db

# Run Worker
python manage.py qcluster
