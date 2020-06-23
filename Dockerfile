FROM tiangolo/uwsgi-nginx-flask:python3.8

ADD pyproject.toml /

RUN pip3 install poetry
RUN poetry config virtualenvs.create false
RUN poetry install --no-dev

COPY ./app /app
