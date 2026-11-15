set -eu

if [ "${DJANGO_LOCAL_MODE:-0}" = "1" ] && [ -z "${DJANGO_SECRET_KEY:-}" ]; then
    key_file="$(dirname "$DJANGO_DB_PATH")/local-secret"
    if [ ! -s "$key_file" ]; then
        (umask 077; python -c 'from secrets import token_urlsafe; print(token_urlsafe(56))' > "$key_file")
    fi
fi

python manage.py migrate --noinput
if [ "${DJANGO_SEED_DEMO:-0}" = "1" ]; then
    python manage.py seed_demo
fi
exec "$@"
