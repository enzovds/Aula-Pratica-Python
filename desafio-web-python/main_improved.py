"""
Arquivo principal refatorado com arquitetura modular.
Integra todos os módulos para funcionamento completo do sistema.
"""

import time
from typing import Optional

from config import Config
from logger_config import logger
from database_manager import DatabaseManager
from api_manager import APIManager
from ui_manager import UIManager
from scraper_manager import ScraperManager
from validators import ValidadorCEP
from input_manager import InputManager, MonitorTeclado


class DesafioWebAvancado:
    """Sistema automatizado de monitoramento de notícias do G1."""
    
    def __init__(self):
        """Inicializa o sistema com todos os módulos."""
        logger.info("Inicializando sistema de monitoramento...")
        
        # Componentes
        self.ui = UIManager()
        self.db = DatabaseManager()
        self.api = APIManager()
        self.scraper = ScraperManager()
        self.input_manager = InputManager(self.ui)
        
        # Estado
        self.rodando = True
        self.cidade_usuario = ""
        self.estado_usuario = ""
        self.monitor_teclado: Optional[MonitorTeclado] = None
        
        # Validar configurações
        try:
            Config.validate()
            logger.info("Configurações validadas com sucesso")
        except AssertionError as e:
            logger.error(f"Erro na validação de configurações: {e}")
            raise
    
    def _parar_sistema(self) -> None:
        """Callback para parar o sistema."""
        self.rodando = False
    
    def solicitar_localizacao(self) -> bool:
        """
        Solicita e valida localização do usuário via CEP.
        
        Returns:
            True se validado, False em caso de erro
        """
        logger.info("Iniciando validação de CEP...")
        
        cep = self.input_manager.solicitar_cep()
        if not cep:
            logger.error("CEP não fornecido")
            return False
        
        self.ui.mostrar_mensagem(f"Consultando CEP {cep}...", tipo="info")
        
        dados = self.api.validar_cep(cep)
        if not dados:
            self.ui.mostrar_mensagem(
                "CEP inválido ou erro de conexão com ViaCEP",
                tipo="error"
            )
            logger.error(f"Falha ao validar CEP: {cep}")
            return False
        
        self.cidade_usuario = dados.get("localidade", "Desconhecida")
        self.estado_usuario = dados.get("uf", "XX")
        
        self.ui.mostrar_mensagem(
            f"Localização confirmada: {self.cidade_usuario} - {self.estado_usuario}",
            tipo="success"
        )
        logger.info(f"Localização validada: {self.cidade_usuario} - {self.estado_usuario}")
        
        time.sleep(1.5)
        return True
    
    def executar_scraping(self) -> None:
        """Executa ciclo completo de scraping e persistência de dados."""
        if not self.rodando:
            return
        
        logger.info("Iniciando ciclo de scraping...")
        self.ui.mostrar_cabecalho(
            self.cidade_usuario,
            self.estado_usuario,
            Config.DATABASE_NAME,
            Config.INTERVALO_VARREDURA
        )
        print("\n")
        
        def executar_com_progresso(progress, tarefa):
            """Callback para executar scraping com barra de progresso."""
            try:
                # Buscar notícias do G1
                logger.debug("Buscando notícias do G1...")
                response = self.api.buscar_noticias_g1()
                progress.update(tarefa, advance=40)
                time.sleep(0.2)
                
                if not response:
                    self.ui.mostrar_mensagem(
                        "Erro ao conectar ao G1",
                        tipo="error"
                    )
                    progress.update(tarefa, advance=60)
                    return
                
                # Extrair notícias do HTML
                logger.debug("Extraindo notícias do HTML...")
                noticias = self.scraper.extrair_noticias(response.text)
                progress.update(tarefa, advance=30)
                time.sleep(0.2)
                
                if not noticias:
                    self.ui.mostrar_mensagem(
                        "Nenhuma notícia encontrada. O seletor CSS pode ter mudado.",
                        tipo="warning"
                    )
                    self.ui.mostrar_mensagem(
                        "Dica: Verifique a estrutura HTML do G1 e atualize o seletor",
                        tipo="info"
                    )
                    progress.update(tarefa, advance=30)
                    return
                
                # Inserir no banco de dados
                logger.debug(f"Inserindo {len(noticias)} notícias no banco...")
                inseridas = self.db.inserir_noticias(noticias)
                progress.update(tarefa, advance=30)
                
                # Mostrar tabela visual
                self.ui.mostrar_tabela_noticias(noticias)
                self.ui.mostrar_mensagem(
                    f"✨ {inseridas} notícia(s) inserida(s) com sucesso",
                    tipo="success"
                )
                
                # Estatísticas
                stats = self.db.obter_estatisticas()
                if stats:
                    logger.info(
                        f"Estatísticas do banco: {stats['total_registros']} registros, "
                        f"{stats['dias_com_dados']} dias com dados"
                    )
                
                # Limpar dados antigos
                logger.debug("Verificando dados antigos...")
                deletados = self.db.limpar_dados_antigos()
                if deletados > 0:
                    logger.info(f"Removidos {deletados} registros antigos")
                    
            except Exception as e:
                logger.error(f"Erro durante scraping: {e}", exc_info=True)
                self.ui.mostrar_mensagem(
                    f"Erro durante scraping: {str(e)[:50]}...",
                    tipo="error"
                )
        
        # Executar com barra de progresso
        self.ui.mostrar_progresso_scraping(executar_com_progresso)
    
    def loop_automacao(self) -> None:
        """Loop principal de automação com intervalo configurável."""
        logger.info(f"Iniciando loop de automação com intervalo de {Config.INTERVALO_VARREDURA}s")
        
        # Executar primeira vez imediatamente
        self.executar_scraping()
        
        # Loop contínuo
        while self.rodando:
            for restante in range(Config.INTERVALO_VARREDURA, 0, -1):
                if not self.rodando:
                    break
                
                self.ui.mostrar_countdown(restante)
                time.sleep(1)
            
            if self.rodando:
                self.executar_scraping()
    
    def executar(self) -> None:
        """Executa o fluxo principal do sistema."""
        try:
            logger.info("="*60)
            logger.info("SISTEMA DE MONITORAMENTO DE NOTÍCIAS G1 INICIADO")
            logger.info("="*60)
            
            # Fase 1: Solicitar localização
            if not self.solicitar_localizacao():
                logger.error("Sistema abortado: falha na validação de localização")
                return
            
            # Fase 2: Iniciar monitor de teclado
            self.monitor_teclado = MonitorTeclado(self._parar_sistema)
            self.monitor_teclado.iniciar()
            
            # Fase 3: Iniciar loop de automação
            self.loop_automacao()
            
        except KeyboardInterrupt:
            logger.warning("Sistema interrompido por Ctrl+C")
            self.rodando = False
        except Exception as e:
            logger.error(f"Erro crítico no sistema: {e}", exc_info=True)
            self.rodando = False
        finally:
            self.finalizar()
    
    def finalizar(self) -> None:
        """Finaliza o sistema de forma segura."""
        logger.info("Finalizando sistema...")
        
        # Parar monitor de teclado
        if self.monitor_teclado:
            self.monitor_teclado.parar()
        
        # Fechar API
        self.api.fechar()
        
        # Exibir mensagem de encerramento
        self.ui.mostrar_encerramento()
        
        # Estatísticas finais
        stats = self.db.obter_estatisticas()
        if stats:
            logger.info(
                f"Resumo final - Total de registros: {stats['total_registros']}, "
                f"Dias com dados: {stats['dias_com_dados']}, "
                f"Primeira coleta: {stats['primeira_coleta']}, "
                f"Última coleta: {stats['ultima_coleta']}"
            )
        
        logger.info("="*60)
        logger.info("SISTEMA ENCERRADO COM SUCESSO")
        logger.info("="*60)


if __name__ == "__main__":
    try:
        app = DesafioWebAvancado()
        app.executar()
    except Exception as e:
        logger.critical(f"Erro fatal ao iniciar aplicação: {e}", exc_info=True)
        print(f"\n❌ Erro fatal: {e}")
        print("Verifique o arquivo de log para mais detalhes.")
        exit(1)
