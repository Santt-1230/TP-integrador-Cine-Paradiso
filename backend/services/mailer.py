import os
import smtplib
from email.message import EmailMessage


def enviar_mail(destino, asunto, texto):
    """Devuelve True si se envio. Con MAIL_MODO=consola solo imprime el mail (para desarrollar)."""
    if os.getenv("MAIL_MODO", "consola") == "consola":
        print(f"[MAIL a {destino}] {asunto}\n{texto}", flush=True)
        return True

    mensaje = EmailMessage()
    mensaje["From"] = os.getenv("MAIL_USUARIO")
    mensaje["To"] = destino
    mensaje["Subject"] = asunto
    mensaje.set_content(texto)
    try:
        with smtplib.SMTP_SSL(os.getenv("MAIL_SERVIDOR", "smtp.gmail.com"), 465, timeout=10) as servidor:
            servidor.login(os.getenv("MAIL_USUARIO"), os.getenv("MAIL_CLAVE"))
            servidor.send_message(mensaje)
    except (smtplib.SMTPException, OSError):
        return False
    return True