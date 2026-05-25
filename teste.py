import pandas as pd # Biblioteca para manipular dados
import matplotlib.pyplot as plt # Biblioteca para gerar os gráficos
import numpy as np # Auxiliar para gerar dados aleatórios no exemplo

# Essa função precisa existir 
def gerar_dados_exemplo():
    data = {
        'Vendas': np.random.rand(10),
        'Preço': np.random.rand(10),
        'Estoque': np.random.rand(10),
        'Lucro': np.random.rand(10)
    }
    return pd.DataFrame(data)

def main(): # Define a função principal do script
    
    print("📊 Mapa de Calor de Correlação")# Exibe uma mensagem de título no console

    opcao = input("Deseja usar dados simulados? (s/n): ").lower()# Captura a entrada do usuário e padroniza para minúsculas com .lower()

    # Estrutura condicional para decidir a origem dos dados
    if opcao == 's':
        # Se 's', chama a função que gera dados fictícios para o exemplo
        df = gerar_dados_exemplo()
    else:
        # Se não for 's', solicita o caminho do arquivo CSV ao usuário
        caminho = input("Digite o caminho do arquivo CSV: ")
        try:
            # Tenta carregar o arquivo usando a biblioteca pandas (pd)
            df = pd.read_csv(caminho)
        except:
            # Caso ocorra um erro (ex: arquivo não encontrado), exibe erro e encerra a função
            print("❌ Erro ao carregar o arquivo.")
            return

    # Exibe no console uma confirmação e as primeiras 5 linhas da tabela (DataFrame)
    print("\n📌 Dados carregados:")
    print(df.head())

    # Calcula a matriz de correlação estatística entre as colunas numéricas
    correlacao = df.corr(numeric_only=True)

    # Imprime os valores numéricos da matriz de correlação no terminal
    print("\n📌 Matriz de Correlação:")
    print(correlacao)

    # Configura o tamanho da janela do gráfico (8 polegadas de largura por 6 de altura)
    plt.figure(figsize=(8, 6))
    # Gera a representação visual (imagem) da matriz de correlação
    plt.imshow(correlacao)

    # Define os nomes das colunas no eixo X e rotaciona em 45 graus para não embolar
    plt.xticks(range(len(correlacao.columns)), correlacao.columns, rotation=45)
    # Define os nomes das colunas no eixo Y
    plt.yticks(range(len(correlacao.columns)), correlacao.columns)

    # Inicia um loop (for) para percorrer as linhas da matriz
    for i in range(len(correlacao.columns)):
        # Inicia outro loop aninhado para percorrer as colunas da matriz
        for j in range(len(correlacao.columns)):
            # Escreve o valor numérico dentro de cada célula do gráfico, com 2 casas decimais
            plt.text(j, i, f"{correlacao.iloc[i, j]:.2f}",
                     ha="center", va="center") # Alinha o texto ao centro

    # Define o título principal que aparecerá em cima do gráfico
    plt.title("Mapa de Calor - Correlação entre Variáveis")
    # Adiciona a legenda lateral (barra de cores) que indica a intensidade dos valores
    plt.colorbar()
    # Ajusta automaticamente os elementos para que nada fique cortado na imagem
    plt.tight_layout()
    # Comando final que abre a janela e exibe o gráfico na tela
    plt.show()

# Verifica se o arquivo está sendo executado diretamente para chamar a função main
if __name__ == "__main__":
    main()