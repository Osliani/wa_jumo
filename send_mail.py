import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_email(lead_details):
    """
    Envía un correo electrónico con los detalles del prospecto.

    Args:
        lead_details (dict): Diccionario con los detalles del prospecto, incluyendo 'name', 'email' y 'message'.

    Returns:
        None
    """
    # Configura las credenciales y los detalles del servidor SMTP
    smtp_server = "smtp.example.com"
    smtp_port = 587
    smtp_username = "tu_correo@example.com"
    smtp_password = "tu_contraseña"

    # Configura los detalles del correo electrónico
    from_email = "tu_correo@example.com"
    to_email = lead_details['email']
    subject = f"Nuevo prospecto: {lead_details['name']}"
    body = f"""
    Hola {lead_details['name']},

    Gracias por contactarnos. Hemos recibido el siguiente mensaje de su parte:

    {lead_details['message']}

    Nos pondremos en contacto con usted pronto.

    Saludos,
    Tu equipo
    """

    # Crear el mensaje de correo electrónico
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        # Conectar al servidor SMTP y enviar el correo electrónico
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.sendmail(from_email, to_email, msg.as_string())
        server.quit()

        print("Correo electrónico enviado con éxito.")
    except Exception as e:
        print(f"Error al enviar el correo electrónico: {e}")

# Ejemplo de uso
lead_details = {
    "name": "John Doe",
    "email": "john.doe@example.com",
    "message": "Estoy interesado en sus servicios."
}

send_email(lead_details)
