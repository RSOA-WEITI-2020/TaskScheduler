FROM tiangolo/uwsgi-nginx-flask:python3.8

RUN git config --global http.sslverify false

ARG PUBLIC_KEY=./keys/jwtRS256.key.pub

ADD pyproject.toml /

COPY $PUBLIC_KEY ${WORKSPACE}/keys/jwtRS256.key.pub

RUN pip3 install poetry
RUN poetry config virtualenvs.create false
RUN poetry install --no-dev

COPY ./app /app
