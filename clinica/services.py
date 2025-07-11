#Injeção de Dependência

class NotificationService:
    def send_notification(self, user_email, message):
        print(f"--- SIMULANDO ENVIO DE NOTIFICAÇÃO ---")
        print(f"Para: {user_email}")
        print(f"Mensagem: {message}")
        print(f"------------------------------------")