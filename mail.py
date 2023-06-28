from smtplib import SMTP
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os, email.utils

def send_mail(to, subject, body):
    ID = 'k.hino.sys22@morijyobi.ac.jp'
    PASS = os.environ['MAIL_PASS']
    HOST = 'smtp.gmail.com'
    PORT = 587
    
    msg = MIMEMultipart()
    
    msg.attach(MIMEText(body, 'html'))
    
    msg['Subject'] = subject
    msg['From'] = email.utils.formataddr(('システム', ID))
    msg['To'] = email.utils.formataddr(('ユーザー様', to))
    
    server = SMTP(HOST, PORT)
    server.starttls()
    server.login(ID, PASS)
    server.send_message(msg)
    server.quit()