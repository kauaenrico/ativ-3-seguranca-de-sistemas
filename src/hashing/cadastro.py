"""
Modulo de Hashing (Autenticacao Segura)

Simula o cadastro de usuarios sem jamais gravar a senha em texto puro.
Cada senha recebe um Salt criptografico aleatorio (16 bytes, via
`secrets.token_bytes`) que e injetado antes do processamento pelo
algoritmo PBKDF2-HMAC-SHA256 (200.000 iteracoes). O SHA-256 puro nao e
usado isoladamente porque e rapido demais e vulneravel a ataques de
forca bruta/rainbow table; o PBKDF2 aplica o SHA-256 repetidas vezes
para tornar cada tentativa de quebra computacionalmente cara.

O resultado (salt + hash) e gravado em um banco SQLite local, simulando
a tabela de usuarios de um sistema real.
"""

from __future__ import annotations

import hashlib
import os
import secrets
import sqlite3
from dataclasses import dataclass

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "usuarios.db")
ALGORITMO_HASH = "sha256"
ITERACOES = 200_000
TAMANHO_SALT_BYTES = 16


@dataclass
class ResultadoCadastro:
    sucesso: bool
    mensagem: str


def _conectar() -> sqlite3.Connection:
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT UNIQUE NOT NULL,
            salt_hex TEXT NOT NULL,
            hash_hex TEXT NOT NULL,
            algoritmo TEXT NOT NULL,
            iteracoes INTEGER NOT NULL
        )
        """
    )
    return conn


def gerar_hash(senha: str, salt: bytes | None = None) -> tuple[bytes, bytes]:
    """Injeta um salt aleatorio (se nao for informado) e deriva o hash da senha."""
    if salt is None:
        salt = secrets.token_bytes(TAMANHO_SALT_BYTES)
    hash_senha = hashlib.pbkdf2_hmac(
        ALGORITMO_HASH, senha.encode("utf-8"), salt, ITERACOES
    )
    return salt, hash_senha


def cadastrar_usuario(usuario: str, senha: str) -> ResultadoCadastro:
    salt, hash_senha = gerar_hash(senha)
    conn = _conectar()
    try:
        conn.execute(
            """
            INSERT INTO usuarios (usuario, salt_hex, hash_hex, algoritmo, iteracoes)
            VALUES (?, ?, ?, ?, ?)
            """,
            (usuario, salt.hex(), hash_senha.hex(), ALGORITMO_HASH, ITERACOES),
        )
        conn.commit()
        return ResultadoCadastro(True, f"Usuario '{usuario}' cadastrado com sucesso.")
    except sqlite3.IntegrityError:
        return ResultadoCadastro(False, f"Usuario '{usuario}' ja existe.")
    finally:
        conn.close()


def verificar_login(usuario: str, senha: str) -> bool:
    conn = _conectar()
    try:
        cur = conn.execute(
            "SELECT salt_hex, hash_hex FROM usuarios WHERE usuario = ?", (usuario,)
        )
        linha = cur.fetchone()
    finally:
        conn.close()

    if linha is None:
        return False

    salt = bytes.fromhex(linha[0])
    hash_armazenado = linha[1]
    _, hash_calculado = gerar_hash(senha, salt)
    return secrets.compare_digest(hash_calculado.hex(), hash_armazenado)


def listar_usuarios() -> list[tuple[str, str, str]]:
    """Retorna (usuario, salt_hex, hash_hex) apenas para fins de demonstracao/relatorio."""
    conn = _conectar()
    try:
        cur = conn.execute("SELECT usuario, salt_hex, hash_hex FROM usuarios")
        return cur.fetchall()
    finally:
        conn.close()


def _demo() -> None:
    print("=== Modulo de Hashing (Autenticacao Segura) ===")

    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    print(cadastrar_usuario("kaua", "SenhaForte#2024").mensagem)
    print(cadastrar_usuario("maria", "SenhaForte#2024").mensagem)  # mesma senha, salt diferente
    print(cadastrar_usuario("kaua", "OutraSenha").mensagem)  # usuario duplicado -> falha

    print("\nRegistros gravados no banco (nunca a senha em texto puro):")
    for usuario, salt_hex, hash_hex in listar_usuarios():
        print(f"  usuario={usuario!r} salt={salt_hex} hash={hash_hex}")

    print("\nProva de que o mesmo password gera hashes diferentes (salt aleatorio):")
    _, hash_kaua = gerar_hash("SenhaForte#2024", bytes.fromhex(listar_usuarios()[0][1]))
    _, hash_maria = gerar_hash("SenhaForte#2024", bytes.fromhex(listar_usuarios()[1][1]))
    print(f"  hash(kaua)  = {hash_kaua.hex()}")
    print(f"  hash(maria) = {hash_maria.hex()}")
    print(f"  hashes iguais? {hash_kaua == hash_maria}")

    print("\nTentativas de login:")
    print(f"  kaua / senha correta   -> {verificar_login('kaua', 'SenhaForte#2024')}")
    print(f"  kaua / senha errada    -> {verificar_login('kaua', 'senha-incorreta')}")
    print(f"  usuario inexistente    -> {verificar_login('inexistente', 'qualquer')}")


if __name__ == "__main__":
    _demo()
