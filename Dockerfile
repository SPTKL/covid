FROM python:3-slim as build

WORKDIR /app

COPY . .

RUN python3 -m venv venv

RUN pip3 install -r . 

CMD [ "./entrypoint.sh" ]