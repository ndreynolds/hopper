import smtplib
from hopper.errors import MailConfigError

class Mail(object):
    """
    The Mail class implements email using smtplib. It automatically uses
    TLS when given a password, so it should work with services like Gmail.
    """

    def __init__(self, sender, auth=None, server='localhost', port=25): 
        self.sender = sender
        self.auth = auth
        self.server = server
        self.port = port

    def send(self, recipients, subject, body):
        if type(recipients) is str:
            recipients = [recipients]
        msg = "From: %s\n" % self.sender + \
              "To: %s\n" % ', '.join(recipients) + \
              "Subject: %s\n\n" % subject + body
        srv = smtplib.SMTP(self.server, self.port)
        if self.auth is not None:
            srv.ehlo()
            srv.starttls()
            srv.ehlo()
            srv.login(self.sender, self.auth)
        srv.sendmail(self.sender, recipients, msg)
        srv.quit()
