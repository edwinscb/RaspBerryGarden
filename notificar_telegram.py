import requests
import datetime

# Tus credenciales de Telegram
TOKEN = "8117967778:AAERGuCoPy95XeMviSnZ1Jd_rSmW_j5wk5Q"
CHAT_ID = "6119961807"

def enviar_mensaje_telegram(mensaje):
    """
    Envía un mensaje a Telegram.
    """
    # Agregar la fecha y hora al final del mensaje
    mensaje += f"\n\n_Última comprobación: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_"
    
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {
        'chat_id': CHAT_ID,
        'text': mensaje,
        'parse_mode': 'Markdown'  # Para usar negritas y emojis
    }
    
    try:
        requests.post(url, data=data)
    except requests.exceptions.RequestException:
        pass

if __name__ == "__main__":
    # Si se ejecuta este script directamente, envía un mensaje de prueba
    enviar_mensaje_telegram("Este es un mensaje de prueba de la función de notificación.")
