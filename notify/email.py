import smtplib
from email.mime.text import MIMEText

def enviar_email(destinatarios, assunto, corpo):

    msg = MIMEText(corpo)
    msg['Subject'] = assunto
    msg['From'] = "seu_email@empresa.com"
    msg['To'] = ", ".join(destinatarios)

    with smtplib.SMTP('smtp.office365.com', 587) as server:
        server.starttls()
        server.login("seu_email@empresa.com", "sua_senha")
        server.send_message(msg)


        