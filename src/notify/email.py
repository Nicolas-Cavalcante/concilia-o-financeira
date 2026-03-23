
import win32com.client as win32


def enviar_email(email_origem,destinatarios, assunto, corpo, anexos=None):
    outlook = win32.Dispatch("Outlook.Application")
    mail = outlook.CreateItem(0)
    conta_encontrada = False
        # Seleciona a conta correta
    for conta in outlook.Session.Accounts:
        if conta.SmtpAddress.lower() == email_origem.lower():
            mail._oleobj_.Invoke(*(64209, 0, 8, 0, conta))
            break
    if not conta_encontrada:
        raise ValueError(f"Conta {email_origem} não encontrada no Outlook")


    mail.To = ";".join(destinatarios)
    mail.Subject = assunto
    mail.HTMLBody = corpo
    if anexos:
        for caminho in anexos:
            mail.Attachments.Add(caminho)

    mail.Send()