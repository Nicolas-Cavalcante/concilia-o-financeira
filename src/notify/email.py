import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

def enviar_email(destinatarios, assunto, corpo, anexos=None):

    msg = MIMEText(corpo)
    msg['Subject'] = assunto
    msg['From'] = "nicolas.cavalcante@flytour.com.br"
    msg['To'] = ", ".join(destinatarios)

    msg.attach(MIMEText(corpo, 'plain'))

        # anexos
    if anexos:
        for caminho in anexos:
            with open(caminho, 'rb') as f:
                parte = MIMEApplication(f.read(), Name=caminho)
                parte['Content-Disposition'] = f'attachment; filename="{caminho}"'
                msg.attach(parte)

    with smtplib.SMTP('smtp.office365.com', 587) as server:
        server.starttls()
        server.login("seu_email@empresa.com", "sua_senha")
        server.send_message(msg)