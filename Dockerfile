FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 DJANGO_DB_PATH=/data/db.sqlite3
WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt \
    && useradd --uid 10001 --no-create-home app \
    && install -d -o app -g app /data /app/staticfiles

COPY . ./
USER 10001
RUN DJANGO_DEBUG=1 python manage.py collectstatic --noinput

EXPOSE 8000
ENTRYPOINT ["/bin/sh", "/app/entrypoint.sh"]
CMD ["gunicorn", "django_concert.wsgi:application", "--bind", "0.0.0.0:8000", "--threads", "4", "--no-control-socket"]
