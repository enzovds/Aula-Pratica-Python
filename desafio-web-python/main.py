import requests
from bs4 import BeautifulSoup
import csv

class DesafioWeb:
    """Classe responsável por gerenciar a integração com a API ViaCEP e o Web Scraping do G1."""
    
    def __init__(self):
        # Atributos/Propriedades da classe (dados encapsulados que o objeto usa)
        self.url_g1 = "https://g1.globo.com/"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.nome_arquivo_csv = "noticias_g1.csv"

    def obter_cep_valido(self) -> str:
        """Método para capturar, limpar e validar o CEP digitado pelo usuário."""
        while True:
            entrada = input("Digite um CEP (8 números) ou aperte Enter para o padrão: ").strip()
            
            if not entrada:
                return "01001000"  # Retorna o CEP padrão
                
            cep_limpo = entrada.replace("-", "").replace(".", "").replace(" ", "")
            
            if len(cep_limpo) == 8 and cep_limpo.isdigit():
                return cep_limpo
            else:
                print("❌ CEP inválido! Certifique-se de digitar exatamente 8 números.\n")

    def consumir_api(self):
        """Método que faz a requisição à API pública do ViaCEP."""
        print("-" * 50)
        print("FASE 2: Consumindo Dados de uma API Pública (POO)")
        print("-" * 50)
        
        # Chama o método interno de validação
        cep = self.obter_cep_valido()
        url_api = f"https://viacep.com.br/ws/{cep}/json/"
        
        try:
            response = requests.get(url_api)
            if response.status_code == 200:
                dados = response.json()
                if "erro" in dados:
                    print("❌ CEP não encontrado na base de dados.")
                    return
                    
                print(f"✔️ CEP Localizado: {dados.get('cep')}")
                print(f"📍 Logradouro: {dados.get('logradouro')}")
                print(f"🏙️ Cidade/UF: {dados.get('localidade')} - {dados.get('uf')}")
            else:
                print(f"❌ Erro na API. Status: {response.status_code}")
        except Exception as e:
            print(f"❌ Falha na requisição da API: {e}")

    def executar_scraping(self):
        """Método que realiza a raspagem de dados no portal G1 e salva em CSV."""
        print("\n" + "-" * 50)
        print("FASE 3: Executando Web Scraping (POO)")
        print("-" * 50)
        
        try:
            # Usa as propriedades da classe através do 'self'
            response = requests.get(self.url_g1, headers=self.headers)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                titulos = soup.find_all('a', class_='feed-post-link')
                
                print(f"✔️ Sucesso! Encontrados {len(titulos)} títulos no portal G1.\n")
                print("📋 Salvando dados estruturados na planilha...")
                
                with open(self.nome_arquivo_csv, mode="w", newline="", encoding="utf-8-sig") as arquivo_csv:
                    escreve = csv.writer(arquivo_csv, delimiter=";")
                    escreve.writerow(["Posição", "Título da Notícia", "Link da Matéria"])
                    
                    for i, titulo in enumerate(titulos[:5], 1):
                        texto_limpo = titulo.text.strip()
                        link_materia = titulo.get('href')
                        
                        print(f"  {i}. {texto_limpo}")
                        escreve.writerow([f"#{i}", texto_limpo, link_materia])
                
                print(f"\n📊 Tabela '{self.nome_arquivo_csv}' atualizada via objeto!")
            else:
                print(f"❌ Não foi possível acessar o site. Status: {response.status_code}")
        except Exception as e:
            print(f"❌ Erro durante o processo de scraping: {e}")


# Bloco de execução principal do Python
if __name__ == "__main__":
    print("🚀 INICIANDO O DESAFIO WEB EM PROGRAMAÇÃO ORIENTADA A OBJETOS\n")
    
    # 1. Instanciamos (criamos) o objeto baseado na nossa classe
    app = DesafioWeb()
    
    # 2. Executamos as ações através dos métodos do objeto
    app.consumir_api()
    app.executar_scraping()
    
    print("\n🚀 DESAFIO FINALIZADO COM SUCESSO")