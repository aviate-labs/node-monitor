from flask import Flask
import threading
import time

app = Flask(__name__)

@app.route('/')
def root():
    d = {
        "status": "ok",
        "message": "Hello World!"
    }
    return d

emails_are_being_sent = False

def send_emails():
    global emails_are_being_sent
    emails_are_being_sent = True
    while True:
        print("Sending emails")
        time.sleep(8)


# Must be ran as a daemon thread so that it stops when the main thread stops
thread = threading.Thread(target=send_emails, daemon=True)
thread.start()


## Runs only during development

if __name__ == "__main__":
    # debug=True will run two instances of the thread
    app.run(debug=False)

