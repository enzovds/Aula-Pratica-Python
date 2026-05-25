import requests
from bs4 import BeautifulSoup
import csv  # Biblioteca nativa para manipulação de arquivos CSV (Excel)

def consumir_api():
    print("-" * 50)
    print("FASE 2: Consumindo Dados de uma API Pública")
    print("-" * 50)
    
    while True:
        entrada = input("Digite um CEP (8 números) ou aperte Enter para o padrão: ").strip()
        
        if not entrada:
            cep = "01001000"
            print(f"-> Usando CEP padrão: {cep}")
            break
            
        cep_limpo = entrada.replace("-", "").replace(".", "").replace(" ", "")
        
        if len(cep_limpo) == 8 and cep_limpo.isdigit():
            cep = cep_limpo
            break
        else:
            print("❌ CEP inválido! Certifique-se de digitar exatamente 8 números (Ex: 12239650).")
            print("Tente novamente...\n")
    
    url = f"https://viacep.com.br/ws/{cep}/json/"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            dados = response.json()
            
            if "erro" in dados:
                print("❌ CEP não encontrado na base de dados do ViaCEP.")
                return
                
            print(f"✔️ CEP Localizado: {dados.get('cep')}")
            print(f"📍 Logradouro: {dados.get('logradouro')}")
            print(f"🏙️ Cidade/UF: {dados.get('localidade')} - {dados.get('uf')}")
        else:
            print(f"❌ Erro ao acessar a API. Status: {response.status_code}")
    except Exception as e:
        print(f"❌ Ocorreu uma falha na requisição: {e}")

def executar_scraping():
    print("\n" + "-" * 50)
    print("FASE 3: Executando Web Scraping")
    print("-" * 50)
    
    url = "https://g1.globo.com/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            titulos = soup.find_all('a', class_='feed-post-link')
            
            print(f"✔️ Sucesso! Encontrados {len(titulos)} títulos na página principal.\n")
            print("📋 Exibindo resultados no terminal e estruturando a tabela CSV...")
            
            # --- MELHORIA OPÇÃO 2: SALVANDO EM CSV (EXCEL) ---
            nome_arquivo = "noticias_g1.csv"
            
            # Abrimos o arquivo configurando o encoding para não quebrar acentos no Windows
            with open(nome_arquivo, mode="w", newline="", encoding="utf-8-sig") as arquivo_csv:
                # Criamos o escritor do CSV
                escreve = csv.writer(arquivo_csv, delimiter=";")
                
                # Escreve o cabeçalho (as colunas da tabela)
                escreve.writerow(["Posição", "Título da Notícia", "Link da Matéria"])
                
                # Loop para listar e salvar as top 5 notícias
                for i, titulo in enumerate(titulos[:5], 1):
                    texto_limpo = titulo.text.strip()
                    link_materia = titulo.get('href') # Coleta o link real da notícia
                    
                    # Mostra no terminal para o usuário ver
                    print(f"  {i}. {texto_limpo}")
                    
                    # Escreve a linha correspondente na tabela
                    escreve.writerow([f"#{i}", texto_limpo, link_materia])
            
            print(f"\n📊 Tabela '{nome_arquivo}' gerada com sucesso para abertura no Excel!")
            
        else:
            print(f"❌ Não foi possível acessar o site. Status: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro durante o processo de scraping: {e}")

if __name__ == "__main__":
    print("🚀 INICIANDO O DESAFIO WEB\n")
    consumir_api()
    executar_scraping()  # Agora ela está perfeitamente definida aqui em cima!
    print("\n🚀 DESAFIO FINALIZADO")