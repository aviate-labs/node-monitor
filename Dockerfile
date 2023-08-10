FROM python:3.11

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . /app

WORKDIR /app

EXPOSE 80

RUN python3 node_monitor/load_config.py

# TODO: Should we put the check and test in a separate container?
RUN make check
RUN make test

CMD ["make", "prod"]