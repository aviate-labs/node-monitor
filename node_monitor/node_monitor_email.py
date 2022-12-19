import email
from email.message import EmailMessage
from smtplib import SMTP
from imaplib import IMAP4_SSL
import time
import logging


from node_monitor.load_config import gmailUsername, gmailPassword


class NodeMonitorEmail(EmailMessage):
    def __init__(self, msg_content, msg_subject="Node Alert"):
        EmailMessage.__init__(self)
        self['Subject'] = msg_subject
        # self['To']      = "NA"
        self['From']    = "Node Monitor by Aviate Labs"
        self.set_content(msg_content)

    def send_to(self, recipient):
        self['To'] = recipient
        with SMTP("smtp.gmail.com", 587) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(gmailUsername, gmailPassword)
            server.send_message(self)
        del self['To']

    def send_recipients(self, recipients):
        for recipient in recipients:
            self.send_to(recipient)



def email_watcher(nodemon_obj):
    with IMAP4_SSL('imap.gmail.com') as M:
        M.login(gmailUsername, gmailPassword)
        logging.info("IMAP4 login successful")

        while True:
            status, [number_of_messages] = M.select('INBOX')

            if nodemon_obj.email_watcher_exit_event.is_set():
                break

            if int(number_of_messages) <= 0:
                time.sleep(0.5)
                continue

            # status, messages = M.search(None, '(UNSEEN)')
            _, messages_all = M.search(None, '(ALL)')
            _, messages_lower = M.search(None, "TEXT", "status")
            _, messages_upper = M.search(None, "TEXT", "STATUS")

            message_ids_all = messages_all[0].split()

            message_ids_status = set.union(
                set(messages_lower[0].split()),
                set(messages_upper[0].split())
            )

            # read and respond to emails
            for message_id in message_ids_status:
                status, data = M.fetch(message_id, '(RFC822)')
                msg = email.message_from_bytes(data[0][1])
                name, addr = email.utils.parseaddr(msg['From'])
                logging.info(f"Got a status request email from {addr}, responding")
                response_email = NodeMonitorEmail(
                    f"You requested a status update! \n\n"
                    + nodemon_obj.stats_message())
                response_email.send_to(addr)
                logging.info(f"Response successfullly Sent")

            # delete all messages to keep inbox clean
            for message_id in message_ids_all:
                M.store(message_id, '+FLAGS', '\\Deleted')
            M.expunge()
            logging.info("Deleted all messages from inbox")

    logging.info("IMAP4 logged out")
