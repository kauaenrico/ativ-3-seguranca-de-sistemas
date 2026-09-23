"""
Modulo de Criptografia (Cifra de Dados)

Cifra e decifra dados financeiros hipoteticos usando criptografia
simetrica AES-256 no modo GCM (Galois/Counter Mode), que fornece:

  - Confidencialidade: os dados ficam ilegiveis sem a chave correta.
  - Autenticidade/Integridade: qualquer alteracao no texto cifrado ou
    o uso de uma chave errada faz a decifragem falhar (InvalidTag),
    ao contrario de modos como o CBC puro.

A mesma chave de 256 bits e usada para cifrar e decifrar (simetrica).
Um nonce (numero usado uma unica vez) de 96 bits e gerado
aleatoriamente a cada operacao de cifragem, como recomendado para o AES-GCM.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

TAMANHO_NONCE_BYTES = 12  # 96 bits, recomendado para AES-GCM


@dataclass
class DadosCifrados:
    nonce: bytes
    texto_cifrado: bytes

    def para_hex(self) -> str:
        return (self.nonce + self.texto_cifrado).hex()


def gerar_chave() -> bytes:
    """Gera uma chave simetrica AES-256 (32 bytes) criptograficamente segura."""
    return AESGCM.generate_key(bit_length=256)


def cifrar(texto_claro: str, chave: bytes) -> DadosCifrados:
    aesgcm = AESGCM(chave)
    nonce = os.urandom(TAMANHO_NONCE_BYTES)
    texto_cifrado = aesgcm.encrypt(nonce, texto_claro.encode("utf-8"), None)
    return DadosCifrados(nonce=nonce, texto_cifrado=texto_cifrado)


def decifrar(dados: DadosCifrados, chave: bytes) -> str:
    aesgcm = AESGCM(chave)
    texto_claro = aesgcm.decrypt(dados.nonce, dados.texto_cifrado, None)
    return texto_claro.decode("utf-8")


def _demo() -> None:
    print("=== Modulo de Criptografia (Cifra de Dados - AES-256-GCM) ===")

    dado_financeiro = (
        "Cartao: 4111 1111 1111 1111 | Validade: 09/29 | CVV: 321 | "
        "Saldo em conta: R$ 15.320,50 | Chave PIX: kaua.financeiro@banco.com"
    )
    print(f"\nTexto original:\n  {dado_financeiro}")

    chave = gerar_chave()
    print(f"\nChave simetrica AES-256 (hex, NUNCA compartilhar em producao):\n  {chave.hex()}")

    dados_cifrados = cifrar(dado_financeiro, chave)
    print(f"\nTexto cifrado (nonce + ciphertext, hex):\n  {dados_cifrados.para_hex()}")

    texto_decifrado = decifrar(dados_cifrados, chave)
    print(f"\nTexto decifrado com a chave correta:\n  {texto_decifrado}")
    print(f"\nDecifragem confere com o original? {texto_decifrado == dado_financeiro}")

    print("\nTentando decifrar com uma chave incorreta (deve falhar)...")
    chave_errada = gerar_chave()
    try:
        decifrar(dados_cifrados, chave_errada)
        print("  ERRO: nao deveria ter conseguido decifrar!")
    except InvalidTag:
        print("  Falhou como esperado (InvalidTag) -> integridade/autenticidade garantidas.")


if __name__ == "__main__":
    _demo()
