import os

import pytest

from src.hashing import cadastro


@pytest.fixture(autouse=True)
def banco_temporario(tmp_path, monkeypatch):
    caminho_db = tmp_path / "usuarios_teste.db"
    monkeypatch.setattr(cadastro, "DB_PATH", str(caminho_db))
    yield
    if os.path.exists(caminho_db):
        os.remove(caminho_db)


def test_cadastro_bem_sucedido():
    resultado = cadastro.cadastrar_usuario("kaua", "SenhaForte#2024")
    assert resultado.sucesso


def test_nao_permite_usuario_duplicado():
    cadastro.cadastrar_usuario("kaua", "SenhaForte#2024")
    resultado = cadastro.cadastrar_usuario("kaua", "OutraSenha")
    assert not resultado.sucesso


def test_senha_nunca_gravada_em_texto_puro():
    cadastro.cadastrar_usuario("kaua", "SenhaForte#2024")
    _, _, hash_hex = cadastro.listar_usuarios()[0]
    assert "SenhaForte#2024" not in hash_hex


def test_mesma_senha_gera_hashes_diferentes_por_salt():
    cadastro.cadastrar_usuario("kaua", "SenhaForte#2024")
    cadastro.cadastrar_usuario("maria", "SenhaForte#2024")
    registros = cadastro.listar_usuarios()
    hashes = {usuario: hash_hex for usuario, _, hash_hex in registros}
    assert hashes["kaua"] != hashes["maria"]


def test_login_com_senha_correta():
    cadastro.cadastrar_usuario("kaua", "SenhaForte#2024")
    assert cadastro.verificar_login("kaua", "SenhaForte#2024") is True


def test_login_com_senha_incorreta():
    cadastro.cadastrar_usuario("kaua", "SenhaForte#2024")
    assert cadastro.verificar_login("kaua", "senha-errada") is False


def test_login_usuario_inexistente():
    assert cadastro.verificar_login("fantasma", "qualquer") is False
