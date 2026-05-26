import requests
from bs4 import BeautifulSoup
import time
import os
import threading
import keyboard
import sqlite3  # Banco de dados relacional nativo
import re       # Expressões Regulares para tratar o formato do CEP
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
        self.nome_banco = "noticias.db"  # Mudamos de CSV para Banco de Dados SQL
        self.intervalo_segundos = 30
        self.rodando = True
        
        # Atributos para registrar a localização do operador do sistema
        self.cidade_usuario = ""
        self.estado_usuario = ""
        
        # Garante a criação da estrutura do banco logo na inicialização do objeto
        self.inicializar_banco_dados()

    def inicializar_banco_dados(self):
        """Cria o arquivo de banco de dados e a tabela se não existirem."""
        conexao = sqlite3.connect(self.nome_banco)
        cursor = conexao.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS dados_noticias (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                posicao TEXT NOT NULL,
                titulo TEXT NOT NULL,
                link TEXT NOT NULL,
                data_coleta TEXT NOT NULL
            )
        """)
        conexao.commit()
        conexao.close()

    def solicitar_e_validar_cep(self):
        """Pede e valida o CEP do usuário uma única vez antes de ligar o loop."""
        os.system('cls' if os.name == 'nt' else 'clear')
        console.print(Panel("[bold cyan]🚀 INICIALIZAÇÃO DO SISTEMA[/]\nPor favor, insira seus dados de localização para o monitoramento.", border_style="blue"))
        
        while True:
            cep_input = input("\nDigite seu CEP (apenas números ou com hífen): ").strip()
            
            # Sanitização: remove qualquer caractere que não seja número
            cep_limpo = re.sub(r'\D', '', cep_input)
            
            if len(cep_limpo) != 8:
                console.print("[bold red]❌ Erro: O CEP deve conter exatamente 8 algarismos. Tente novamente.[/]")
                continue
                
            console.print(f"[yellow]Consultando CEP {cep_limpo} na API ViaCEP...[/]")
            
            try:
                response = requests.get(f"https://viacep.com.br/ws/{cep_limpo}/json/")
                if response.status_code == 200:
                    dados = response.json()
                    
                    if "erro" in dados:
                        console.print("[bold red]❌ Erro: CEP inexistente na base de dados nacional. Tente novamente.[/]")
                        continue
                    
                    # Armazena os dados validados na instância
                    self.cidade_usuario = dados.get("localidade", "Desconhecida")
                    self.estado_usuario = dados.get("uf", "XX")
                    
                    console.print(f"[bold green]✔️ Localização Confirmada: {self.cidade_usuario} - {self.estado_usuario}[/]")
                    time.sleep(1.5)
                    break
                else:
                    console.print("[bold red]❌ Falha de comunicação com a API ViaCEP. Tentando novamente...[/]")
            except Exception as e:
                console.print(f"[bold red]❌ Erro ao conectar na API: {e}[/]")

    def cabecalho_interface(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        log_hora = datetime.now().strftime("%H:%M:%S")
        
        # Painel atualizado mostrando o Operador e o banco de dados ativo
        painel_conteudo = (
            f"[bold cyan]SISTEMA AUTOMATIZADO DE MONITORAMENTO - G1[/]\n"
            f"[📍 OPERADOR:] {self.cidade_usuario} - {self.estado_usuario} | [🗄️ BANCO SQL:] {self.nome_banco}\n"
            f"[⚙️ STATUS:] Worker Ativo | [🕒 ATUALIZAÇÃO:] {log_hora} | [⏳ INTERVALO:] {self.intervalo_segundos}s\n"
            f"[🛑 COMANDO:] Pressione a tecla [bold red]'q'[/bold red] a qualquer momento para encerrar."
        )
        console.print(Panel(painel_conteudo, border_style="bold blue", expand=True))

    def ejecutar_worker_scraping(self):
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
            tarefa = progress.add_task("[yellow]Minerando portal G1 e persistindo dados no Banco SQL...", total=100)
            
            try:
                response = requests.get(self.url_g1, headers=self.headers)
                progress.update(tarefa, advance=40)
                time.sleep(0.2)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    titulos = soup.find_all('a', class_='feed-post-link')
                    progress.update(tarefa, advance=30)
                    time.sleep(0.2)
                    
                    # --- OPERAÇÃO RELACIONAL SQL ---
                    conexao = sqlite3.connect(self.nome_banco)
                    cursor = conexao.cursor()
                    data_atual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                    
                    for i, titulo in enumerate(titulos[:5], 1):
                        cursor.execute("""
                            INSERT INTO dados_noticias (posicao, titulo, link, data_coleta)
                            VALUES (?, ?, ?, ?)
                        """, (f"#{i}", titulo.text.strip(), titulo.get('href'), data_atual))
                    
                    conexao.commit()
                    conexao.close()
                    
                    progress.update(tarefa, advance=30)
                    
                    # --- DASHBOARD VISUAL ---
                    tabela_visual = Table(title="📰 TOP 5 MANCHETES ARMAZENADAS NO SQLITE", title_style="bold magenta", expand=True)
                    tabela_visual.add_column("Posição", style="bold green", justify="center", width=10)
                    tabela_visual.add_column("Notícia Coletada em Tempo Real", style="white")
                    
                    for i, titulo in enumerate(titulos[:5], 1):
                        tabela_visual.add_row(f"🔥 #{i}", titulo.text.strip())
                    
                    print("\n")
                    console.print(tabela_visual)
                    console.print(f"\n[bold green]✔️ Novas linhas inseridas com sucesso no banco '{self.nome_banco}'![/]")
                    
                else:
                    console.print(f"[bold red]❌ Erro de conexão com o G1. Status: {response.status_code}[/]")
            except Exception as e:
                console.print(f"[bold red]❌ Falha crítica no Worker: {e}[/]")

    def monitorar_teclado(self):
        keyboard.wait('q')
        self.rodando = False
        print("\n\n[bold yellow]🛑 Comando de encerramento recebido! Finalizando processos...[/]")

    def iniciar_loop_automacao(self):
        # 1. Faz a verificação geográfica obrigatoriamente no início
        self.solicitar_e_validar_cep()

        # 2. Inicia o monitoramento paralelo da tecla 'q'
        thread_teclado = threading.Thread(target=self.monitorar_teclado, daemon=True)
        thread_teclado.start()

        # 3. Dispara a primeira execução do robô
        self.executar_worker_scraping()
        
        # 4. Mantém o ciclo eterno de 30s enquanto a flag for verdadeira
        while self.rodando:
            for restante in range(self.intervalo_segundos, 0, -1):
                if not self.rodando:
                    break
                print(f"🔄 Próxima varredura automática em: {restante} segundos...   ", end="\r")
                time.sleep(1)
                
            if self.rodando:
                self.executar_worker_scraping()

        console.print("\n[bold green]🚀 SISTEMA E BANCO DE DADOS ENCERRADOS COM SUCESSO![/]\n")

if __name__ == "__main__":
    app = DesafioWebAvancado()
    app.iniciar_loop_automacao()