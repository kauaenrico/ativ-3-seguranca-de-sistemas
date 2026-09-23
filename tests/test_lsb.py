import pytest
from PIL import Image

from src.esteganografia import lsb


@pytest.fixture
def imagem_base(tmp_path):
    caminho = tmp_path / "base.png"
    lsb._gerar_imagem_base(str(caminho), largura=64, altura=64)
    return str(caminho)


def test_esconder_e_extrair_mensagem(imagem_base, tmp_path):
    caminho_saida = str(tmp_path / "com_segredo.png")
    mensagem = "segredo de teste"

    lsb.esconder_mensagem(imagem_base, mensagem, caminho_saida)
    mensagem_extraida = lsb.extrair_mensagem(caminho_saida)

    assert mensagem_extraida == mensagem


def test_imagem_nao_alterada_visualmente(imagem_base, tmp_path):
    caminho_saida = str(tmp_path / "com_segredo.png")
    lsb.esconder_mensagem(imagem_base, "mensagem curta", caminho_saida)

    original = Image.open(imagem_base).convert("RGB")
    modificada = Image.open(caminho_saida).convert("RGB")

    diffs = [
        abs(p1 - p2)
        for (p1_pix, p2_pix) in zip(original.getdata(), modificada.getdata())
        for p1, p2 in zip(p1_pix, p2_pix)
    ]
    assert max(diffs) <= 1


def test_mensagem_maior_que_capacidade_gera_erro(imagem_base):
    capacidade = lsb.capacidade_maxima_bytes(imagem_base)
    mensagem_grande = "x" * (capacidade + 100)

    with pytest.raises(ValueError):
        lsb.esconder_mensagem(imagem_base, mensagem_grande, imagem_base + ".out.png")


def test_mensagem_com_acentos_e_unicode(imagem_base, tmp_path):
    caminho_saida = str(tmp_path / "com_segredo.png")
    mensagem = "Confidencial: reunião às 15h, não divulgar."

    lsb.esconder_mensagem(imagem_base, mensagem, caminho_saida)
    mensagem_extraida = lsb.extrair_mensagem(caminho_saida)

    assert mensagem_extraida == mensagem
