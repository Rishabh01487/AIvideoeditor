web: sh /app/entrypoint.sh
worker: celery -A workers.celery_app worker --loglevel=info --workdir=/app/backend