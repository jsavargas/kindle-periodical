FROM python:3.10.2-alpine

WORKDIR /app

ENV TZ="America/Santiago"




#COPY requirements.txt requirements.txt
RUN pip install --upgrade pip
COPY .  .

RUN pip install .

COPY README.md /opt/
COPY Dockerfile /opt/


#WORKDIR /config

#ENTRYPOINT ["python", "/app/elmostrador.py"]
