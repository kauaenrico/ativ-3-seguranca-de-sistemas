# Atividade 3 — Segurança de Sistemas

Trabalho da disciplina **Confiabilidade, Segurança de Sistemas e Ergonomia** (Engenharia de Computação).

## Integrantes do grupo

| RA | Nome |
|---|---|
| 220020281 | Lucas Gabriel Bento Correa |
| 220020517 | Leonardo Fernandes Fanhani |
| 220019627 | Kauã Enrico Pasti Altran |
| 220020592 | Henrique Pignato |
| 220020097 | Luke Gabriel dos Santos Belatine |

Implementação de três rotinas matemáticas de proteção e ocultação de dados, em Python:

1. **Hashing** — cadastro de usuário com senha protegida por *salt* aleatório + PBKDF2-HMAC-SHA256, persistido em SQLite.
2. **Criptografia** — cifra simétrica AES-256-GCM de uma string com dados financeiros hipotéticos, com prova de decifragem.
3. **Esteganografia** — ocultação de uma frase confidencial nos bits menos significativos (LSB) de uma imagem PNG, com extração posterior.

## Estrutura do projeto

```
.
├── demo.py                        # roda a demonstração dos 3 módulos em sequência
├── requirements.txt
├── src/
│   ├── hashing/cadastro.py        # Módulo 1 — hashing + salt + SQLite
│   ├── criptografia/cifra_aes.py  # Módulo 2 — AES-256-GCM
│   └── esteganografia/lsb.py      # Módulo 3 — esteganografia LSB
├── tests/                         # testes automatizados (pytest) dos 3 módulos
├── assets/                        # imagem base e imagem com mensagem oculta (gerados)
└── data/                          # banco SQLite gerado em tempo de execução (git-ignored)
```

## Como executar

```bash
pip install -r requirements.txt
python demo.py
```

Para rodar os testes automatizados:

```bash
python -m pytest tests/ -v
```

## Resumo técnico de cada módulo

### 1. Hashing (`src/hashing/cadastro.py`)

- Nenhuma senha é gravada em texto puro.
- A cada cadastro, um *salt* aleatório de 16 bytes é gerado com `secrets.token_bytes` e injetado **antes** do processamento.
- A senha é derivada com **PBKDF2-HMAC-SHA256** (200.000 iterações) em vez de um único SHA-256, para dificultar ataques de força bruta e *rainbow tables*.
- `salt` e hash resultante são gravados em uma tabela SQLite (`data/usuarios.db`), simulando a persistência de um sistema real.
- A verificação de login recalcula o hash com o salt armazenado e compara com `secrets.compare_digest` (comparação em tempo constante).

### 2. Criptografia (`src/criptografia/cifra_aes.py`)

- Cifra simétrica **AES-256 no modo GCM**: além de confidencialidade, garante autenticidade/integridade (qualquer alteração no texto cifrado ou uso de chave errada faz a decifragem falhar com `InvalidTag`).
- Uma chave de 256 bits e um nonce de 96 bits (gerado aleatoriamente a cada cifragem) são usados conforme a prática recomendada para AES-GCM.
- O script cifra uma string com dados financeiros fictícios (cartão, saldo, chave PIX) e decifra de volta, comprovando que o texto recuperado é idêntico ao original.

### 3. Esteganografia (`src/esteganografia/lsb.py`)

- A mensagem é convertida em bytes, prefixada por um cabeçalho de 4 bytes com o tamanho, e cada bit é injetado no bit menos significativo dos canais R, G e B dos pixels da imagem.
- Isso altera cada byte de cor em no máximo ±1, o que é imperceptível a olho nu.
- O script gera uma imagem base (gradiente) caso não exista, esconde a mensagem, salva a imagem resultante e depois varre a imagem para extrair a mensagem, comprovando que ela é recuperada integralmente.

## Testes automatizados

15 testes em `tests/` cobrem os três módulos (cadastro/login, cifra/decifra com chave correta e errada, ocultação/extração LSB, mensagens com acentuação e limite de capacidade da imagem).
