.PHONY: check test testall dev prod

check:
	mypy --strict node_monitor

test:
	pytest tests/

testall:
	pytest -s --send_emails --db --send_slack tests/

# This runs it with the development WSGI Server
dev:
	python3 -m node_monitor

# Run this with the production gunicorn WSGI Server
prod:
	gunicorn -w 1 -b 0.0.0.0:80 --access-logfile gunicornlog.txt -k eventlet node_monitor.__main__:app
# We're forced to run this with only one worker because we're instantiating
# node_monitor in a thread from inside the app. If we had multiple workers,
# we would have multiple instances of node_monitor running, each sending
# emails. Because this is a low traffic app, I found it easier to just run
# one worker, rather than use something like Celery.

# We're using eventlet because otherwise we get timeouts in the default
# sync worker, which causes gunicorn to timeout and restart the app, 
# resetting any internal state. See:
# https://docs.gunicorn.org/en/stable/design.html
# https://github.com/benoitc/gunicorn/issues/1801#issuecomment-585886471
# https://stackoverflow.com/questions/15463067/gunicorn-worker-timeout
