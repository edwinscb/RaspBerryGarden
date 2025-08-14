import logging

# Configuración de logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

def escape_markdown(text: str) -> str:
    """Escapa caracteres especiales para MarkdownV2."""
    special_chars = r'_*[]()~`>#+-=|{}.!'
    return ''.join(f'\\{c}' if c in special_chars else c for c in text)
