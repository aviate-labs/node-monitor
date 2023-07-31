.PHONY: check test dev prod

check:
	mypy --strict node_monitor

test:
	pytest tests/

dev:
	python3 -m node_monitor

# We're forced to run this with only one worker because we're instantiating
# node_monitor in a thread from inside the app. If we had multiple workers,
# we would have multiple instances of node_monitor running, each sending
# emails. Because this is a low traffic app, I found it easier to just run
# one worker, rather than use something like Celery.
prod:
	gunicorn -w 1 -b 0.0.0.0:80 node_monitor.__main__:app
