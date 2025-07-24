import smtplib, ssl
import os
from config import config
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_mail(message, subject, receiver_email, html=False, postfix=None):

    #Login Data for smtp Server
    smtp_server = os.environ.get("EMAIL_HOST")
    login = os.environ.get("EMAIL_USR")
    password = os.environ.get("EMAIL_PWD")
    sender_email = os.environ.get("EMAIL_SENDER")
    if postfix is None:
        postfix = os.environ.get("EMAIL_POSTFIX")

    receiver = receiver_email


    if config.email_enabled == False:
        print(message)
    else:
        try:
            #Bauen der eigentlichen Email
            _message = MIMEMultipart("alternative")
            _message["Subject"] = subject
            _message["From"] = sender_email
            _message["To"] = receiver_email

            if html:
                content = MIMEText(message + "\n\n" + postfix, "html")
                _message.attach(content)
            else:
                content = MIMEText(message + "\n\n" + postfix, "plain")
                _message.attach(content)

            server = smtplib.SMTP(smtp_server)
            server.set_debuglevel(1)
            #server.esmtp_features['auth'] = 'LOGIN DIGEST-MD5 PLAIN'
            #server.login(login, password)
            server.sendmail(
                sender_email, receiver, _message.as_string()
            )

        except Exception as e:
            print(e)
            raise e
