# Djirection · Django band website

Djirection is the band website for the IBM Back-end Application Development Capstone. It combines a Django application with two Flask APIs for songs and concert pictures. Visitors can browse both catalogs, read song lyrics, register, and record an RSVP for an upcoming concert. Django Admin manages the concert schedule.

- [Pictures service](https://github.com/Nurzhan-Zhumabekov/Back-End-Development-Pictures) supplies the gallery through `GET /picture`.
- [Songs service](https://github.com/Nurzhan-Zhumabekov/Back-End-Development-Songs) supplies titles and lyrics from MongoDB through `GET /song`.

## Run locally

Start both Flask services on ports 3000 and 8080, respectively. To use other endpoints, set `PICTURES_SERVICE_URL` and `SONGS_SERVICE_URL` to the service base URLs.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

On Windows, activate the virtual environment with `.venv\Scripts\Activate.ps1`. Open [the local website](http://127.0.0.1:8000/). Use `python manage.py createsuperuser` to manage concerts at `/admin/`.

Run `python manage.py test` to check registration and authentication, concert RSVP, and integration with both catalog formats.

## Deploy

Build the image with `docker build -t djangoserver .`. For Kubernetes, configure the image reference, upstream service URLs, public hostname, and trusted HTTPS origin in `deployment.yml`. Provide `DJANGO_SECRET_KEY` through the referenced Kubernetes Secret. The manifest uses one Django replica with SQLite on a persistent volume.

Repository created from the [IBM Skills Network template](https://github.com/ibm-developer-skills-network/sfvih-Back-end-Development-Capstone).
