"""Calculadora interativa simples."""

def obter_numero(prompt: str) -> float:
    """Solicita um número ao usuário e trata entradas inválidas."""
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("Entrada inválida. Digite um número válido.")

def menu() -> None:
    """Exibe o menu de opções da calculadora."""
    print("1. Somar")
    print("2. Subtrair")
    print("3. Multiplicar")
    print("4. Dividir")
    print("5. Sair")

def main() -> None:
    """Função principal que executa o loop da calculadora."""
    while True:
        menu()
        escolha = input("Escolha uma opção: ")
        if escolha == "1":
            a = obter_numero("Digite o primeiro número: ")
            b = obter_numero("Digite o segundo número: ")
            print(f"Resultado: {a + b}")
        elif escolha == "2":
            a = obter_numero("Digite o primeiro número: ")
            b = obter_numero("Digite o segundo número: ")
            print(f"Resultado: {a - b}")
        elif escolha == "3":
            a = obter_numero("Digite o primeiro número: ")
            b = obter_numero("Digite o segundo número: ")
            print(f"Resultado: {a * b}")
        elif escolha == "4":
            a = obter_numero("Digite o primeiro número: ")
            b = obter_numero("Digite o segundo número: ")
            try:
                print(f"Resultado: {a / b}")
            except ZeroDivisionError:
                print("Erro: divisão por zero não é permitida.")
        elif escolha == "5":
            print("Saindo...")
            break
        else:
            print("Opção inválida. Tente novamente.")

if __name__ == "__main__":
    main()
