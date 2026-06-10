"""
Sistema de logging centralizado.
Registra eventos importantes do sistema em arquivo e console.
"""

import logging
from logging.handlers import RotatingFileHandler
from typing import Optional

from config import Config


class LoggerConfig:
    """Configuração centralizada de logging."""
    
    _instance: Optional[logging.Logger] = None
    
    @classmethod
    def get_logger(cls) -> logging.Logger:
        """
        Obtém ou cria a instância do logger.
        
        Returns:
            logging.Logger: Instance do logger configurado
        """
        if cls._instance is None:
            cls._instance = cls._criar_logger()
        return cls._instance
    
    @classmethod
    def _criar_logger(cls) -> logging.Logger:
        """Cria e configura o logger."""
        logger = logging.getLogger("DesafioWebAvancado")
        logger.setLevel(getattr(logging, Config.LOG_LEVEL))
        
        # Formato de log
        formato = logging.Formatter(
            '[%(asctime)s] %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Handler para arquivo com rotação
        arquivo_handler = RotatingFileHandler(
            Config.LOG_FILE,
            maxBytes=Config.LOG_MAX_BYTES,
            backupCount=Config.LOG_BACKUP_COUNT
        )
        arquivo_handler.setLevel(getattr(logging, Config.LOG_LEVEL))
        arquivo_handler.setFormatter(formato)
        
        # Handler para console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)  # Apenas warnings no console
        console_handler.setFormatter(formato)
        
        logger.addHandler(arquivo_handler)
        if Config.VERBOSE:
            logger.addHandler(console_handler)
        
        return logger


# Exportar instância global
logger = LoggerConfig.get_logger()
