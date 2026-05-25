# Desafio Prático: Desenvolvimento Web Avançado com Python 🌐

Este repositório contém a resolução do Desafio Prático Web, totalmente reformulado utilizando o paradigma de **Programação Orientada a Objetos (POO)**. O projeto consiste em um sistema automatizado (Worker) com interface gráfica via terminal que consome dados de uma API pública e realiza mineração de dados (Web Scraping).

## 🚀 Recursos Implementados

- **Arquitetura POO:** Todo o sistema foi estruturado em classes e objetos para melhor encapsulamento e organização do código.
- **Tratamento de Dados:** Validação robusta de entrada do CEP via terminal, limpando caracteres especiais e tratando erros.
- **Interface Gráfica CLI:** Dashboard estilizado no terminal com tabelas e barras de progresso animadas utilizando a biblioteca *Rich*.
- **Automação (Worker):** Script configurado para rodar em segundo plano com um cronômetro regressivo, executando a varredura e atualização dos dados automaticamente.
- **Persistência em CSV:** Os dados minerados são estruturados e salvos diretamente em um arquivo `.csv` compatível com o Excel.

## 🛠️ Tecnologias e Bibliotecas

- **Python 3**
- **Requests:** Requisições HTTP para consumo da API ViaCEP e download do HTML do G1.
- **BeautifulSoup4:** Parsing e mineração das tags HTML das manchetes.
- **Rich:** Renderização do layout, tabelas coloridas e animações no terminal.
- **CSV (Nativo):** Manipulação e escrita do relatório de dados.

## 📦 Como Executar o Projeto

1. Certifique-se de ter as dependências instaladas:
   ```bash
   pip install -r requirements.txt

2. Execute o script principal:
    ```bash
   python main.py

3. Para encerrar o sistema: Pressione a tecla 'Q' no seu teclado a qualquer momento. O robô vai identificar o comando e fechar a aplicação de forma segura e elegante.
    ```bash
   q