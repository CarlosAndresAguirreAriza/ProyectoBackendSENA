FROM python:3.12-alpine3.20

ENV PYTHONUNBUFFERED 1
ENV ENVIRONMENT production

WORKDIR /usr/src/app

RUN pip install --upgrade pip && \
  pip install poetry

ENV PATH="/root/.local/bin:$PATH"

COPY ./api_pricut ./

COPY ./pyproject.toml ./

RUN rm -rf /usr/src/app/api_pricut/tests

RUN apk add --no-cache gcc musl-dev geos-dev

RUN poetry config virtualenvs.create false

RUN poetry install --only main --no-interaction --no-ansi

CMD sh -c "python3 manage.py migrate --settings=settings.environments.$ENVIRONMENT && \
  python3 manage.py configureusergroups --settings=settings.environments.$ENVIRONMENT && \
  python3 manage.py createadmin --settings=settings.environments.$ENVIRONMENT && \
  python3 manage.py loadstaticinfo --settings=settings.environments.$ENVIRONMENT && \
  python3 manage.py collectstatic --noinput --clear --settings=settings.environments.$ENVIRONMENT && \
  gunicorn settings.wsgi:application --env DJANGO_SETTINGS_MODULE=settings.environments.$ENVIRONMENT"
