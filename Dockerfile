FROM python:3.11

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . /app

WORKDIR /app

EXPOSE 80

# Note: environment variables won't load until the container is run,
# so we can't do something like 'RUN make test' here. We have to put the command
# in the CMD section.
# TODO: Should we put the check and test in a separate container?

CMD bash -c "make check && make test && make prod"