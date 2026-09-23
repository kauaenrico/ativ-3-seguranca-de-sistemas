"""
Executa a demonstracao completa dos tres modulos de seguranca:

    1. Hashing (cadastro de usuario com salt + PBKDF2-SHA256, gravado em SQLite)
    2. Criptografia (cifra AES-256-GCM de dados financeiros hipoteticos)
    3. Esteganografia (ocultacao de mensagem nos bits menos significativos de uma imagem)

Uso:
    python demo.py
"""

from src.criptografia import cifra_aes
from src.esteganografia import lsb
from src.hashing import cadastro


def main() -> None:
    cadastro._demo()
    print("\n" + "=" * 70 + "\n")
    cifra_aes._demo()
    print("\n" + "=" * 70 + "\n")
    lsb._demo()


if __name__ == "__main__":
    main()
