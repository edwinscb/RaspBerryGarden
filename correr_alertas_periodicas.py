from monitorear_sistema import check_for_alerts
from notificar_telegram import enviar_mensaje_telegram

# Llamar a la función de monitoreo
alerta_mensaje = check_for_alerts()

# Si se detectó una alerta, enviar el mensaje
if alerta_mensaje:
    enviar_mensaje_telegram(alerta_mensaje)
