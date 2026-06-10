"""
Gerenciador de banco de dados SQLite.
Centraliza todas as operações com o banco de dados.
"""

import sqlite3
from datetime import datetime, timedelta
from typing import List, Tuple, Optional
from contextlib import contextmanager

from config import Config
from logger_config import logger


class DatabaseManager:
    """Gerenciador centralizado de banco de dados."""
    
    def __init__(self, db_name: str = Config.DATABASE_NAME):
        """
        Inicializa o gerenciador de banco de dados.
        
        Args:
            db_name: Nome do arquivo do banco de dados
        """
        self.db_name = db_name
        self.inicializar()
        logger.info(f"Banco de dados inicializado: {db_name}")
    
    @contextmanager
    def _conexao(self):
        """Context manager para conexões com banco de dados."""
        conexao = sqlite3.connect(self.db_name)
        conexao.row_factory = sqlite3.Row
        try:
            yield conexao
        finally:
            conexao.close()
    
    def inicializar(self) -> None:
        """Cria as tabelas se não existirem."""
        try:
            with self._conexao() as conexao:
                cursor = conexao.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS dados_noticias (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        posicao TEXT NOT NULL,
                        titulo TEXT NOT NULL,
                        link TEXT NOT NULL,
                        data_coleta TEXT NOT NULL,
                        criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Criar índices para melhor performance
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_data_coleta 
                    ON dados_noticias(data_coleta)
                """)
                
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_criado_em 
                    ON dados_noticias(criado_em)
                """)
                
                conexao.commit()
                logger.info("Tabelas do banco de dados criadas/verificadas com sucesso")
        except sqlite3.Error as e:
            logger.error(f"Erro ao inicializar banco de dados: {e}")
            raise
    
    def inserir_noticias(
        self,
        noticias: List[Tuple[str, str, str]]
    ) -> int:
        """
        Insere múltiplas notícias no banco.
        
        Args:
            noticias: Lista de tuplas (posicao, titulo, link)
            
        Returns:
            Número de notícias inseridas
        """
        count = 0
        data_atual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        try:
            with self._conexao() as conexao:
                cursor = conexao.cursor()
                
                for posicao, titulo, link in noticias:
                    try:
                        cursor.execute("""
                            INSERT INTO dados_noticias 
                            (posicao, titulo, link, data_coleta)
                            VALUES (?, ?, ?, ?)
                        """, (posicao, titulo, link, data_atual))
                        count += 1
                    except sqlite3.Error as e:
                        logger.warning(f"Erro ao inserir notícia '{titulo[:50]}...': {e}")
                
                conexao.commit()
                logger.info(f"{count} notícias inseridas com sucesso")
        except sqlite3.Error as e:
            logger.error(f"Erro ao inserir notícias: {e}")
        
        return count
    
    def obter_ultimas_noticias(self, limite: int = 10) -> List[dict]:
        """
        Obtém as últimas notícias inseridas.
        
        Args:
            limite: Número máximo de notícias a retornar
            
        Returns:
            Lista de dicionários com dados das notícias
        """
        try:
            with self._conexao() as conexao:
                cursor = conexao.cursor()
                cursor.execute("""
                    SELECT id, posicao, titulo, link, data_coleta
                    FROM dados_noticias
                    ORDER BY criado_em DESC
                    LIMIT ?
                """, (limite,))
                
                return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Erro ao obter últimas notícias: {e}")
            return []
    
    def limpar_dados_antigos(self, dias: int = Config.DATABASE_RETENTION_DAYS) -> int:
        """
        Remove notícias mais antigas que o período de retenção.
        
        Args:
            dias: Número de dias a manter
            
        Returns:
            Número de registros deletados
        """
        try:
            data_limite = (datetime.now() - timedelta(days=dias)).strftime("%Y-%m-%d")
            
            with self._conexao() as conexao:
                cursor = conexao.cursor()
                cursor.execute("""
                    DELETE FROM dados_noticias
                    WHERE DATE(criado_em) < DATE(?)
                """, (data_limite,))
                
                conexao.commit()
                deletados = cursor.rowcount
                
                if deletados > 0:
                    logger.info(f"{deletados} registros antigos removidos (> {dias} dias)")
                
                return deletados
        except sqlite3.Error as e:
            logger.error(f"Erro ao limpar dados antigos: {e}")
            return 0
    
    def obter_total_registros(self) -> int:
        """
        Obtém o total de registros no banco.
        
        Returns:
            Número total de registros
        """
        try:
            with self._conexao() as conexao:
                cursor = conexao.cursor()
                cursor.execute("SELECT COUNT(*) FROM dados_noticias")
                return cursor.fetchone()[0]
        except sqlite3.Error as e:
            logger.error(f"Erro ao contar registros: {e}")
            return 0
    
    def obter_estatisticas(self) -> dict:
        """
        Obtém estatísticas do banco de dados.
        
        Returns:
            Dicionário com estatísticas
        """
        try:
            with self._conexao() as conexao:
                cursor = conexao.cursor()
                
                cursor.execute("SELECT COUNT(*) FROM dados_noticias")
                total = cursor.fetchone()[0]
                
                cursor.execute("""
                    SELECT COUNT(DISTINCT DATE(data_coleta)) as dias
                    FROM dados_noticias
                """)
                dias = cursor.fetchone()[0]
                
                cursor.execute("""
                    SELECT MIN(criado_em), MAX(criado_em)
                    FROM dados_noticias
                """)
                resultado = cursor.fetchone()
                primeira_coleta = resultado[0] if resultado[0] else "N/A"
                ultima_coleta = resultado[1] if resultado[1] else "N/A"
                
                return {
                    "total_registros": total,
                    "dias_com_dados": dias,
                    "primeira_coleta": primeira_coleta,
                    "ultima_coleta": ultima_coleta
                }
        except sqlite3.Error as e:
            logger.error(f"Erro ao obter estatísticas: {e}")
            return {}
