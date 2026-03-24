import win32com.client as win32


def enviar_email(email_origem,destinatarios, assunto, corpo, anexos=None):
    outlook = win32.Dispatch("Outlook.Application")
    mail = outlook.CreateItem(0)
    
    mail.To = ";".join(destinatarios)
    mail.Subject = assunto
    mail.HTMLBody = corpo

    mail.SentOnBehalfOfName = email_origem

    if anexos:
        for caminho in anexos:
            mail.Attachments.Add(caminho)

    mail.Send()