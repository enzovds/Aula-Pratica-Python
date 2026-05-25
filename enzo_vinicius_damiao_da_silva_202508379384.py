try:
    print(int (input()) / int(input()))
except ZeroDivisionError:
    print("Não dá pra dividir por zero, parça!")
finally:
    print("Operação finalizada.")