from flask import Flask
import threading
import time

app = Flask(__name__)

emails = 0

@app.route('/')
def root():
    d = {
        "status": "ok",
        "message": "Hello World!",
        "emails": emails
    }
    return d


def send_emails():
    global emails
    while True:
        print("Sending email")
        time.sleep(1)
        emails += 1


# Must be ran as a daemon thread so that it stops when the main thread stops
thread = threading.Thread(target=send_emails, daemon=True)
thread.start()


## Runs only during development

if __name__ == "__main__":
    # debug=True will run two instances of the thread
    app.run(debug=False)

