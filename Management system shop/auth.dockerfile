FROM python:3

RUN mkdir -p /opt/src/auth
WORKDIR /opt/src/auth

COPY auth/application.py ./application.py
COPY auth/configuration.py ./configuration.py
COPY auth/models.py ./models.py
COPY auth/requirements.txt ./requirements.txt
COPY auth/authDecorator.py ./authDecorator.py

RUN pip install -r ./requirements.txt

ENV PYTHONPATH="/opt/src/auth"

ENTRYPOINT ["python", "./application.py"]
