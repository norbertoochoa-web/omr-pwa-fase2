import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

from app.config import settings
from app.services.txt_service import generate_delphi_txt, save_txt_to_file
from app.models import Session


async def send_session_email(session: Session, user_email: str) -> bool:
    txt_content = generate_delphi_txt(session)
    txt_path = save_txt_to_file(txt_content, settings.UPLOAD_DIR, str(session.id))
    session.result_txt_path = txt_path

    if not settings.SMTP_HOST or settings.SMTP_HOST == "":
        return False

    try:
        msg = MIMEMultipart()
        msg["Subject"] = f"Resultados OMR - Sesión {session.id}"
        msg["From"] = settings.SMTP_FROM
        msg["To"] = user_email

        body = MIMEText(
            f"Estimado(a) profesor(a),\n\n"
            f"Se han procesado {session.total_images} cartillas en la sesión {session.name}.\n"
            f"Resultados exitosos: {session.processed_images}\n\n"
            f"Se adjunta el archivo .txt con los resultados.\n\n"
            f"Saludos,\nSistema OMR PWA"
        )
        msg.attach(body)

        with open(txt_path, "rb") as f:
            attachment = MIMEApplication(f.read(), _subtype="txt")
            attachment.add_header("Content-Disposition", "attachment", filename=os.path.basename(txt_path))
            msg.attach(attachment)

        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            if settings.SMTP_TLS:
                server.starttls()
            if settings.SMTP_USER:
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(msg)

        session.email_sent = True
        return True

    except Exception as e:
        print(f"Email send error: {e}")
        return False
