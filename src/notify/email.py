import win32com.client as win32

#Esse arquivo é responsável pela estruturação do e-mail,
# utilizando a biblioteca win32com como fonte principal.
#==============================================
# 📑 ENVIO DE E-MAILS
#==============================================


def enviar_email(email_origem,destinatarios, assunto, corpo, anexos=None, cc=None, bcc=None):
    outlook = win32.Dispatch("Outlook.Application")
    mail = outlook.CreateItem(0)
    
    mail.To = ";".join(destinatarios)

    if cc:
        mail.cc = ";".join(cc)
    if bcc:
        mail.BCC = ";".join(bcc)
    mail.Subject = assunto
    mail.HTMLBody = corpo

    mail.SentOnBehalfOfName = email_origem

    if anexos:
        for caminho in anexos:
            mail.Attachments.Add(caminho)

    mail.Send()