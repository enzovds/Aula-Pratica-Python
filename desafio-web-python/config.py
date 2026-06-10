"""
Configuração centralizada da aplicação.
Carrega variáveis de ambiente do arquivo .env ou usa valores padrão.
"""

import os
from pathlib import Path
from typing import Optional

# Diretório base do projeto
BASE_DIR = Path(__file__).parent

# Arquivo de configuração
ENV_FILE = BASE_DIR / ".env"


class Config:
    """Classe de configuração centralizada."""
    
    # ViaCEP API
    VIACEP_API_URL: str = os.getenv("VIACEP_API_URL", "https://viacep.com.br/ws")
    VIACEP_TIMEOUT: int = int(os.getenv("VIACEP_TIMEOUT", "5"))
    
    # G1 Web Scraping
    G1_URL: str = os.getenv("G1_URL", "https://g1.globo.com/")
    G1_TIMEOUT: int = int(os.getenv("G1_TIMEOUT", "5"))
    G1_SELECTOR: str = os.getenv("G1_SELECTOR", "feed-post-link")
    G1_MAX_POSTS: int = int(os.getenv("G1_MAX_POSTS", "5"))
    
    # Banco de Dados
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "noticias.db")
    DATABASE_RETENTION_DAYS: int = int(os.getenv("DATABASE_RETENTION_DAYS", "7"))
    DATABASE_CHECK_INTERVAL: int = int(os.getenv("DATABASE_CHECK_INTERVAL", "86400"))
    
    # Sistema
    INTERVALO_VARREDURA: int = int(os.getenv("INTERVALO_VARREDURA", "30"))
    USER_AGENT: str = os.getenv(
        "USER_AGENT",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    )
    
    # Logging
    LOG_FILE: str = os.getenv("LOG_FILE", "sistema_monitoramento.log")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_MAX_BYTES: int = int(os.getenv("LOG_MAX_BYTES", "5242880"))  # 5MB
    LOG_BACKUP_COUNT: int = int(os.getenv("LOG_BACKUP_COUNT", "5"))
    
    # Debug
    DEBUG_MODE: bool = os.getenv("DEBUG_MODE", "False").lower() == "true"
    VERBOSE: bool = os.getenv("VERBOSE", "False").lower() == "true"
    
    @classmethod
    def load_from_env_file(cls) -> None:
        """Carrega variáveis do arquivo .env se existir."""
        if ENV_FILE.exists():
            with open(ENV_FILE) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        if "=" in line:
                            key, value = line.split("=", 1)
                            os.environ[key.strip()] = value.strip()
    
    @classmethod
    def validate(cls) -> None:
        """Valida as configurações."""
        assert cls.VIACEP_TIMEOUT > 0, "VIACEP_TIMEOUT deve ser maior que 0"
        assert cls.G1_TIMEOUT > 0, "G1_TIMEOUT deve ser maior que 0"
        assert cls.INTERVALO_VARREDURA > 0, "INTERVALO_VARREDURA deve ser maior que 0"
        assert cls.G1_MAX_POSTS > 0, "G1_MAX_POSTS deve ser maior que 0"
        assert cls.DATABASE_RETENTION_DAYS > 0, "DATABASE_RETENTION_DAYS deve ser maior que 0"


# Carregar configurações na importação
Config.load_from_env_file()
