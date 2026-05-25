total = 0
carrinho = []
produto = ""

# Agora a condição está correta: enquanto NÃO for 'fim'
while produto.lower().strip() != "fim":
    produto = input("Nome do produto (ou 'fim' para encerrar): ")
    
    # Conferimos de novo aqui para não pedir o preço do "fim"
    if produto.lower().strip() != "fim":
        preco = float(input(f"Preço de {produto}: R$ "))
        carrinho.append(produto)
        total += preco

print("\n--- RESUMO DA COMPRA ---")
if len(carrinho) > 0:
    for item in carrinho:
        print(f"- {item}")
    print("-" * 20)
    print(f"VALOR TOTAL: R$ {total:.2f}")
else:
    print("Nenhum produto foi comprado.")