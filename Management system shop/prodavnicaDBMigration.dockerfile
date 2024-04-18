FROM python:3

RUN mkdir -p /opt/src/prodavnica
WORKDIR /opt/src/prodavnica

COPY prodavnica/migrate.py ./migrate.py
COPY prodavnica/configuration.py ./configuration.py
COPY prodavnica/models.py ./models.py
COPY prodavnica/requirements.txt ./requirements.txt

RUN pip install -r ./requirements.txt

ENV PYTHONPATH="/opt/src/prodavnica"

ENTRYPOINT ["python", "./migrate.py"]

