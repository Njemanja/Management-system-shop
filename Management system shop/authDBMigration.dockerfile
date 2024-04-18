FROM python:3

RUN mkdir -p /opt/src/auth
WORKDIR /opt/src/auth

COPY auth/migrate.py ./migrate.py
COPY auth/configuration.py ./configuration.py
COPY auth/models.py ./models.py
COPY auth/requirements.txt ./requirements.txt

RUN pip install -r ./requirements.txt

ENV PYTHONPATH="/opt/src/auth"

ENTRYPOINT ["python", "./migrate.py"]

