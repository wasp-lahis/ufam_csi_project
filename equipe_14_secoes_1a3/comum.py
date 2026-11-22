"""
Funções comuns às seções 2 e 3: leitura/escrita de CSV, leitura dos TXT e cálculo de amplitudes.
"""
import csv

import numpy as np

from config import RAIZ_BASE, PASTA_RESULTADOS

N_CAMPOS = 129      # 1 coluna temporal + 64 pares (imaginária, real)


def ler_csv(nome):
    """Lê um CSV da pasta resultados/ como lista de dicionários."""
    with open(PASTA_RESULTADOS / nome, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def escrever_csv(nome, linhas, colunas):
    """Grava uma lista de dicionários como CSV na pasta resultados/."""
    PASTA_RESULTADOS.mkdir(parents=True, exist_ok=True)
    with open(PASTA_RESULTADOS / nome, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=colunas)
        w.writeheader()
        w.writerows(linhas)


def ler_txt_csi(caminho_txt):
    """
    Lê um TXT de CSI (caminho relativo à raiz) e devolve a matriz bruta (registros x 129).
    Linhas vazias são ignoradas. Interrompe se alguma linha não tiver 129 valores finitos
    (a seleção da seção 2 já exclui esses arquivos; a verificação aqui é uma salvaguarda).
    """
    linhas = []
    with open(RAIZ_BASE / caminho_txt, encoding="utf-8-sig") as f:
        for n, linha in enumerate(f, start=1):
            if not linha.strip():
                continue
            valores = [float(v) for v in linha.strip().split(",")]
            if len(valores) != N_CAMPOS or not np.all(np.isfinite(valores)):
                raise ValueError(f"{caminho_txt}, linha {n}: formato inválido")
            linhas.append(valores)
    return np.array(linhas, dtype=float)


def amplitudes(matriz_bruta):
    """
    Separa a coluna temporal e calcula |H| = sqrt(Re^2 + Im^2) para os 64 pares.
    Ordem das colunas no TXT: tempo, Im1, Re1, Im2, Re2, ..., Im64, Re64
    (mesma convenção de get_amps em Scripts/CSI.py). Retorna matriz registros x 64.
    """
    csi = matriz_bruta[:, 1:]          # remove a coluna temporal
    im = csi[:, 0::2]                  # colunas 2, 4, ..., 128 do TXT
    re = csi[:, 1::2]                  # colunas 3, 5, ..., 129 do TXT
    return np.sqrt(re ** 2 + im ** 2)
