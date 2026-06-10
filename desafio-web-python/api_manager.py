"""
Gerenciador de APIs externas.
Centraliza requisições HTTP com retry, timeout e tratamento de erros.
"""

import requests
from typing import Optional, Dict, Any
from time import sleep

from config import Config
from logger_config import logger


class APIManager:
    """Gerenciador centralizado de requisições HTTP."""
    
    # Configurações de retry
    MAX_RETRIES = 3
    BACKOFF_FACTOR = 2
    
    def __init__(self):
        """Inicializa o gerenciador de APIs."""
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": Config.USER_AGENT})
    
    def _fazer_requisicao_com_retry(
        self,
        url: str,
        metodo: str = "GET",
        timeout: int = 5,
        **kwargs
    ) -> Optional[requests.Response]:
        """
        Faz requisição com retry automático.
        
        Args:
            url: URL para requisição
            metodo: Método HTTP (GET, POST, etc)
            timeout: Timeout em segundos
            **kwargs: Argumentos adicionais para requests
            
        Returns:
            Response object ou None em caso de falha
        """
        for tentativa in range(self.MAX_RETRIES):
            try:
                logger.debug(f"Tentativa {tentativa + 1}/{self.MAX_RETRIES} para {url}")
                
                response = self.session.request(
                    metodo,
                    url,
                    timeout=timeout,
                    **kwargs
                )
                
                response.raise_for_status()
                logger.debug(f"Requisição bem-sucedida: {url}")
                return response
                
            except requests.exceptions.Timeout:
                logger.warning(
                    f"Timeout na tentativa {tentativa + 1}/{self.MAX_RETRIES} para {url}"
                )
            except requests.exceptions.ConnectionError:
                logger.warning(
                    f"Erro de conexão na tentativa {tentativa + 1}/{self.MAX_RETRIES} para {url}"
                )
            except requests.exceptions.HTTPError as e:
                logger.error(f"Erro HTTP {e.response.status_code} para {url}")
                return response if tentativa == self.MAX_RETRIES - 1 else None
            except Exception as e:
                logger.error(f"Erro inesperado na requisição: {e}")
            
            # Backoff exponencial entre tentativas
            if tentativa < self.MAX_RETRIES - 1:
                tempo_espera = self.BACKOFF_FACTOR ** tentativa
                logger.info(f"Aguardando {tempo_espera}s antes de retentativa...")
                sleep(tempo_espera)
        
        logger.error(f"Todas as {self.MAX_RETRIES} tentativas falharam para {url}")
        return None
    
    def validar_cep(self, cep: str) -> Optional[Dict[str, Any]]:
        """
        Valida CEP usando API ViaCEP.
        
        Args:
            cep: CEP com 8 dígitos
            
        Returns:
            Dicionário com dados do CEP ou None em caso de erro
        """
        url = f"{Config.VIACEP_API_URL}/{cep}/json/"
        
        response = self._fazer_requisicao_com_retry(
            url,
            timeout=Config.VIACEP_TIMEOUT
        )
        
        if not response:
            return None
        
        try:
            dados = response.json()
            
            if "erro" in dados:
                logger.warning(f"CEP inválido: {cep}")
                return None
            
            logger.info(f"CEP validado: {dados.get('localidade')} - {dados.get('uf')}")
            return dados
            
        except Exception as e:
            logger.error(f"Erro ao parsear resposta ViaCEP: {e}")
            return None
    
    def buscar_noticias_g1(self) -> Optional[requests.Response]:
        """
        Busca notícias do G1.
        
        Returns:
            Response object ou None em caso de erro
        """
        response = self._fazer_requisicao_com_retry(
            Config.G1_URL,
            timeout=Config.G1_TIMEOUT
        )
        
        if response:
            logger.info(f"Notícias do G1 obtidas com sucesso (tamanho: {len(response.text)} bytes)")
        
        return response
    
    def fechar(self) -> None:
        """Fecha a sessão HTTP."""
        self.session.close()
        logger.debug("Sessão HTTP fechada")
    
    def __enter__(self):
        """Context manager enter."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.fechar()
