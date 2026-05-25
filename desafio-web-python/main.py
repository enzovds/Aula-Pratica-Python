import requests
from bs4 import BeautifulSoup

def consumir_api():
    print("-" * 50)
    print("FASE 2: Consumindo Dados de uma API Pública")
    print("-" * 50)
    
    # Exemplo utilizando a API pública do ViaCEP
    cep = "01001000"  # CEP de exemplo
    url = f"https://viacep.com.br/ws/{cep}/json/"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            dados = response.json()
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
    
    # URL de um portal de notícias (exemplo com o G1)
    url = "https://g1.globo.com/"
    
    # Headers para simular um navegador real e evitar bloqueios
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Buscando os links/títulos principais do feed do G1
            titulos = soup.find_all('a', class_='feed-post-link')
            
            print(f"✔️ Sucesso! Encontrados {len(titulos)} títulos na página principal.\n")
            print("📋 Exibindo os 5 primeiros resultados coletados:")
            
            for i, titulo in enumerate(titulos[:5], 1):
                texto_limpo = titulo.text.strip()
                print(f"  {i}. {texto_limpo}")
        else:
            print(f"❌ Não foi possível acessar o site. Status: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro durante o processo de scraping: {e}")

if __name__ == "__main__":
    print("🚀 INICIANDO O DESAFIO WEB\n")
    consumir_api()
    executar_scraping()
    print("\n🚀 DESAFIO FINALIZADO")