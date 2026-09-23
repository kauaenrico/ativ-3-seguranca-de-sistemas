import pytest
from cryptography.exceptions import InvalidTag

from src.criptografia import cifra_aes


def test_cifrar_e_decifrar_retorna_texto_original():
    chave = cifra_aes.gerar_chave()
    texto_original = "Cartao: 4111 1111 1111 1111 | Saldo: R$ 15.320,50"

    dados_cifrados = cifra_aes.cifrar(texto_original, chave)
    texto_decifrado = cifra_aes.decifrar(dados_cifrados, chave)

    assert texto_decifrado == texto_original


def test_texto_cifrado_nao_contem_dados_em_claro():
    chave = cifra_aes.gerar_chave()
    texto_original = "informacao-financeira-sigilosa"

    dados_cifrados = cifra_aes.cifrar(texto_original, chave)

    assert texto_original.encode("utf-8") not in dados_cifrados.texto_cifrado


def test_decifrar_com_chave_errada_falha():
    chave = cifra_aes.gerar_chave()
    chave_errada = cifra_aes.gerar_chave()
    dados_cifrados = cifra_aes.cifrar("dado sigiloso", chave)

    with pytest.raises(InvalidTag):
        cifra_aes.decifrar(dados_cifrados, chave_errada)


def test_nonce_diferente_a_cada_chamada():
    chave = cifra_aes.gerar_chave()
    dados1 = cifra_aes.cifrar("mesma mensagem", chave)
    dados2 = cifra_aes.cifrar("mesma mensagem", chave)

    assert dados1.nonce != dados2.nonce
    assert dados1.texto_cifrado != dados2.texto_cifrado
