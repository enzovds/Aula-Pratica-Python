import requests
from bs4 import BeautifulSoup
import csv
import time
import os
import threading  # Biblioteca nativa para rodar processos em paralelo
import keyboard   # Biblioteca para escutar as teclas em tempo real
from datetime import datetime

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn

console = Console()

class DesafioWebAvancado:
    def __init__(self):
        self.url_g1 = "https://g1.globo.com/"
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        self.nome_arquivo_csv = "noticias_g1.csv"
        self.intervalo_segundos = 30
        self.rodando = True  # Flag que controla se o sistema deve continuar ativo

    def cabecalho_interface(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        log_hora = datetime.now().strftime("%H:%M:%S")
        
        painel_conteudo = (
            f"[bold cyan]SISTEMA AUTOMATIZADO DE MONITORAMENTO - G1[/]\n"
            f"[⚙️ STATUS:] Worker Ativo | [🕒 ÚLTIMA ATUALIZAÇÃO:] {log_hora} | [⏳ INTERVALO:] {self.intervalo_segundos}s\n"
            f"[🛑 COMANDO:] Pressione a tecla [bold red]'q'[/bold red] a qualquer momento para encerrar o sistema."
        )
        console.print(Panel(painel_conteudo, border_style="bold blue", expand=True))

    def executar_worker_scraping(self):
        if not self.rodando:
            return
            
        self.cabecalho_interface()
        print("\n")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console
        ) as progress:
            tarefa = progress.add_task("[yellow]Conectando ao portal G1 e minerando dados...", total=100)
            
            try:
                response = requests.get(self.url_g1, headers=self.headers)
                progress.update(tarefa, advance=40)
                time.sleep(0.2)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    titulos = soup.find_all('a', class_='feed-post-link')
                    progress.update(tarefa, advance=40)
                    time.sleep(0.2)
                    
                    with open(self.nome_arquivo_csv, mode="w", newline="", encoding="utf-8-sig") as arquivo_csv:
                        escreve = csv.writer(arquivo_csv, delimiter=";")
                        escreve.writerow(["Posição", "Título", "Link"])
                        for i, titulo in enumerate(titulos[:5], 1):
                            escreve.writerow([f"#{i}", titulo.text.strip(), titulo.get('href')])
                    
                    progress.update(tarefa, advance=20)
                    
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

    def monitorar_teclado(self):
        """Thread paralela: Fica escutando o teclado sem travar o relógio principal."""
        # Aguarda até que a tecla 'q' seja pressionada
        keyboard.wait('q')
        self.rodando = False # Desliga o motor do sistema
        print("\n\n[bold yellow]🛑 Comando de encerramento recebido! Finalizando processos...[/]")

    def iniciar_loop_automacao(self):
        # 1. Dispara a Thread do teclado antes de começar o loop
        # Isso joga a função 'monitorar_teclado' para rodar em paralelo em segundo plano
        thread_teclado = threading.Thread(target=self.monitorar_teclado, daemon=True)
        thread_teclado.start()

        # Executa a primeira varredura
        self.executar_worker_scraping()
        
        # Loop principal controlado pela nossa variável self.rodando
        while self.rodando:
            for restante in range(self.intervalo_segundos, 0, -1):
                # Se o usuário apertar 'q' no meio da contagem, interrompe na hora
                if not self.rodando:
                    break
                print(f"🔄 Próxima varredura automática em: {restante} segundos...   ", end="\r")
                time.sleep(1)
                
            if self.rodando:
                self.executar_worker_scraping()

        # Mensagem de saída limpa quando o 'while' quebra
        console.print("\n[bold green]🚀 SISTEMA ENCERRADO COM SUCESSO. ATÉ A PRÓXIMA![/]\n")

if __name__ == "__main__":
    app = DesafioWebAvancado()
    app.iniciar_loop_automacao()