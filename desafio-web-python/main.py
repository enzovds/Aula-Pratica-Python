import requests
from bs4 import BeautifulSoup
import csv
import time
import os
from datetime import datetime

# Importações da biblioteca Rich para a Interface Gráfica
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn

# Cria o controlador da tela
console = Console()

class DesafioWebAvancado:
    def __init__(self):
        self.url_g1 = "https://g1.globo.com/"
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        self.nome_arquivo_csv = "noticias_g1.csv"
        self.intervalo_segundos = 30  # Tempo do Worker (30 segundos para podermos testar)

    def cabecalho_interface(self):
        """Gera o painel de título estilizado no topo do terminal."""
        os.system('cls' if os.name == 'nt' else 'clear') # Limpa a tela para parecer um painel fixo
        log_hora = datetime.now().strftime("%H:%M:%S")
        
        painel_conteudo = (
            f"[bold cyan]SISTEMA AUTOMATIZADO DE MONITORAMENTO - G1[/]\n"
            f"[⚙️ STATUS:] Worker Ativo | [🕒 ÚLTIMA ATUALIZAÇÃO:] {log_hora} | [⏳ INTERVALO:] {self.intervalo_segundos}s"
        )
        console.print(Panel(painel_conteudo, border_style="bold blue", expand=True))

    def executar_worker_scraping(self):
        """Método que faz o scraping com barra de progresso gráfica e exibe a tabela estilizada."""
        self.cabecalho_interface()
        
        # --- 1. BARRA DE PROGRESSO GRÁFICA ---
        print("\n")
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console
        ) as progress:
            tarefa = progress.add_task("[yellow]Conectando ao portal G1 e minerando dados...", total=100)
            
            # Simula visualmente o carregamento enquanto faz a requisição real
            try:
                response = requests.get(self.url_g1, headers=self.headers)
                progress.update(tarefa, advance=40)
                time.sleep(0.3)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    titulos = soup.find_all('a', class_='feed-post-link')
                    progress.update(tarefa, advance=40)
                    time.sleep(0.3)
                    
                    # Salva no arquivo CSV por baixo dos panos
                    with open(self.nome_arquivo_csv, mode="w", newline="", encoding="utf-8-sig") as arquivo_csv:
                        escreve = csv.writer(arquivo_csv, delimiter=";")
                        escreve.writerow(["Posição", "Título", "Link"])
                        for i, titulo in enumerate(titulos[:5], 1):
                            escreve.writerow([f"#{i}", titulo.text.strip(), titulo.get('href')])
                    
                    progress.update(tarefa, advance=20) # Concluído
                    
                    # --- 2. TABELA GRÁFICA INTERATIVA ---
                    # Criamos uma tabela visual linda para o terminal
                    tabela_visual = Table(title="📰 TOP 5 MANCHETES EM DESTAQUE", title_style="bold magenta", expand=True)
                    tabela_visual.add_column("Posição", style="bold green", justify="center", width=10)
                    tabela_visual.add_column("Notícia Coletada em Tempo Real", style="white")
                    
                    for i, titulo in enumerate(titulos[:5], 1):
                        tabela_visual.add_row(f"🔥 #{i}", titulo.text.strip())
                    
                    print("\n")
                    console.print(tabela_visual)
                    console.print(f"\n[bold green]✔️ Dados gravados com sucesso em '{self.nome_arquivo_csv}'![/]")
                    
                else:
                    console.print(f"[bold red]❌ Erro de conexão com o G1. Status: {response.status_code}[/]")
            except Exception as e:
                console.print(f"[bold red]❌ Falha crítica no Worker: {e}[/]")

    def iniciar_loop_automacao(self):
        """O coração do Worker: mantém o sistema rodando sozinho no tempo determinado."""
        # Roda a primeira vez logo ao iniciar
        self.executar_worker_scraping()
        
        while True:
            # Faz a contagem regressiva no terminal de forma elegante
            for restante in range(self.intervalo_segundos, 0, -1):
                # O '\r' faz o texto atualizar na mesma linha do terminal
                print(f"🔄 Próxima varredura automática em: {restante} segundos...   ", end="\r")
                time.sleep(1)
                
            # Quando estoura o tempo, ele chama o scraping de novo automaticamente
            self.executar_worker_scraping()

if __name__ == "__main__":
    # Instancia o aplicativo e liga o motor do Worker com interface
    app = DesafioWebAvancado()
    app.iniciar_loop_automacao()