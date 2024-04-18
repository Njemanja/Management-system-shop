FROM python:3

RUN mkdir -p /opt/src/prodavnica
WORKDIR /opt/src/prodavnica

COPY prodavnica/customer.py ./customer.py
COPY prodavnica/configuration.py ./configuration.py
COPY prodavnica/models.py ./models.py
COPY prodavnica/requirements.txt ./requirements.txt
COPY prodavnica/prodavnicaDecorator.py ./prodavnicaDecorator.py


RUN pip install -r ./requirements.txt
ENV PYTHONPATH="/opt/src/prodavnica"

ENTRYPOINT ["python", "./customer.py"]
