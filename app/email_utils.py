from flask_mail import Message
from app.config import Config

def send_confirmation_email(user, confirm_url):
    from app import mail  # 🔹 Importa dentro da função para evitar erro de importação circular

    msg = Message(
        'Confirme sua reserva',
        sender='noreply@giftlist.com',
        recipients=[user.email]
    )
    msg.body = f'Olá, {user.name}!\n\nClique no link abaixo para confirmar a reserva do presente:\n{confirm_url}\n\nSe não foi você, ignore este e-mail.'

    mail.send(msg)
