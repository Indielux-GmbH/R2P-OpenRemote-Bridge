FROM python:3.11@sha256:354903e205598c82f91ab025139923fcde8ab6e0cd3bb0f5b753aeaaecb71923

WORKDIR /app/code/

COPY Docker/ /

RUN pip install --requirement requirements.txt

CMD [ "python3", "main.py" ]
