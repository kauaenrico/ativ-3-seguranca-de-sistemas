"""
Modulo de Esteganografia (Ocultacao LSB)

Esconde uma mensagem de texto nos bits menos significativos (Least
Significant Bit) dos canais R, G e B de uma imagem PNG/BMP, sem alterar
visualmente a imagem: cada byte de cor pode variar no maximo +-1 em sua
intensidade, o que e imperceptivel ao olho humano.

Formato do payload embutido: 4 bytes de cabecalho (big-endian) com o
tamanho em bytes da mensagem, seguidos pelos bytes da mensagem (UTF-8).
Isso permite extrair exatamente a mensagem original sem depender de um
delimitador especial no meio dos dados.
"""

from __future__ import annotations

from typing import Iterator

from PIL import Image

BITS_POR_BYTE = 8
BYTES_CABECALHO = 4  # tamanho da mensagem, big-endian


def _mensagem_para_payload(mensagem: str) -> bytes:
    dados = mensagem.encode("utf-8")
    cabecalho = len(dados).to_bytes(BYTES_CABECALHO, "big")
    return cabecalho + dados


def _payload_para_bits(payload: bytes) -> str:
    return "".join(f"{byte:08b}" for byte in payload)


def capacidade_maxima_bytes(caminho_imagem: str) -> int:
    """Numero maximo de bytes de mensagem que a imagem consegue esconder."""
    with Image.open(caminho_imagem) as img:
        largura, altura = img.size
    bits_disponiveis = largura * altura * 3
    return max(0, bits_disponiveis // BITS_POR_BYTE - BYTES_CABECALHO)


def esconder_mensagem(caminho_entrada: str, mensagem: str, caminho_saida: str) -> None:
    img = Image.open(caminho_entrada).convert("RGB")
    largura, altura = img.size
    pixels = img.load()

    payload = _mensagem_para_payload(mensagem)
    bits = _payload_para_bits(payload)

    capacidade_bits = largura * altura * 3
    if len(bits) > capacidade_bits:
        raise ValueError(
            f"Mensagem muito grande para esta imagem: precisa de {len(bits)} bits, "
            f"capacidade disponivel e {capacidade_bits} bits."
        )

    indice = 0
    total_bits = len(bits)
    for y in range(altura):
        for x in range(largura):
            if indice >= total_bits:
                break
            r, g, b = pixels[x, y]
            canais = [r, g, b]
            for c in range(3):
                if indice < total_bits:
                    bit = int(bits[indice])
                    canais[c] = (canais[c] & ~1) | bit
                    indice += 1
            pixels[x, y] = (canais[0], canais[1], canais[2])
        if indice >= total_bits:
            break

    img.save(caminho_saida)


def _gerador_bits(pixels, largura: int, altura: int) -> Iterator[int]:
    for y in range(altura):
        for x in range(largura):
            r, g, b = pixels[x, y]
            yield r & 1
            yield g & 1
            yield b & 1


def extrair_mensagem(caminho_imagem: str) -> str:
    img = Image.open(caminho_imagem).convert("RGB")
    largura, altura = img.size
    pixels = img.load()
    gerador = _gerador_bits(pixels, largura, altura)

    def ler_bytes(quantidade: int) -> bytes:
        resultado = bytearray()
        for _ in range(quantidade):
            valor = 0
            for _ in range(BITS_POR_BYTE):
                valor = (valor << 1) | next(gerador)
            resultado.append(valor)
        return bytes(resultado)

    tamanho_mensagem = int.from_bytes(ler_bytes(BYTES_CABECALHO), "big")
    dados = ler_bytes(tamanho_mensagem)
    return dados.decode("utf-8")


def _gerar_imagem_base(caminho: str, largura: int = 320, altura: int = 240) -> None:
    """Gera uma imagem de exemplo (gradiente) para nao depender de arquivos externos."""
    img = Image.new("RGB", (largura, altura))
    pixels = img.load()
    for y in range(altura):
        for x in range(largura):
            pixels[x, y] = (
                int(255 * x / largura),
                int(255 * y / altura),
                int(255 * ((x + y) % (largura + altura)) / (largura + altura)),
            )
    img.save(caminho)


def _demo() -> None:
    import os

    print("=== Modulo de Esteganografia (Ocultacao LSB) ===")

    pasta_assets = os.path.join(os.path.dirname(__file__), "..", "..", "assets")
    os.makedirs(pasta_assets, exist_ok=True)
    caminho_base = os.path.join(pasta_assets, "imagem_base.png")
    caminho_com_segredo = os.path.join(pasta_assets, "imagem_com_segredo.png")

    if not os.path.exists(caminho_base):
        _gerar_imagem_base(caminho_base)
        print(f"Imagem base gerada em: {caminho_base}")

    mensagem_secreta = "Mensagem confidencial: reuniao as 15h no cofre 42."
    print(f"\nCapacidade maxima da imagem: {capacidade_maxima_bytes(caminho_base)} bytes")
    print(f"Mensagem a esconder ({len(mensagem_secreta.encode('utf-8'))} bytes):\n  {mensagem_secreta!r}")

    esconder_mensagem(caminho_base, mensagem_secreta, caminho_com_segredo)
    print(f"\nImagem com mensagem oculta salva em: {caminho_com_segredo}")

    tamanho_base = os.path.getsize(caminho_base)
    tamanho_secreta = os.path.getsize(caminho_com_segredo)
    print(f"Tamanho do arquivo original: {tamanho_base} bytes")
    print(f"Tamanho do arquivo com mensagem: {tamanho_secreta} bytes")

    from PIL import ImageChops

    img_original = Image.open(caminho_base).convert("RGB")
    img_modificada = Image.open(caminho_com_segredo).convert("RGB")
    diferenca = ImageChops.difference(img_original, img_modificada)
    maior_diferenca = max(maximo for _, maximo in diferenca.getextrema())
    print(f"Maior diferenca de intensidade em qualquer canal: {maior_diferenca} (imperceptivel ao olho humano)")

    mensagem_extraida = extrair_mensagem(caminho_com_segredo)
    print(f"\nMensagem extraida:\n  {mensagem_extraida!r}")
    print(f"Extracao confere com o original? {mensagem_extraida == mensagem_secreta}")


if __name__ == "__main__":
    _demo()
