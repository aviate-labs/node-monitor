FROM python:3.11

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . /app

WORKDIR /app

CMD ["python3", "-m", "node_monitor"]