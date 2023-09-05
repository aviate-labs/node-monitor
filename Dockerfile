FROM python:3.11

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . /app

WORKDIR /app

EXPOSE 80

# Note: environment variables won't load until the container is run,
# so we can't do something like 'RUN make test' here. We have to put the command
# in the CMD section.

CMD bash -c "\
if [ \"$TEST\" = true ]; then \
    make check && make test; \
else \
    make prod; \
fi"
