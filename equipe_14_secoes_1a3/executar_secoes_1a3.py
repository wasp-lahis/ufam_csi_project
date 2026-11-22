"""
Executa as seções 1, 2 e 3 em ordem e confere os entregáveis.
Uso: python executar_secoes_1a3.py
"""
import csv
import time

import secao1_inventario
import secao2_selecao
import secao3_amplitudes
from config import PASTA_RESULTADOS, PASTA_FIGURAS, ID_EQUIPE, PARTICIPANTES, RAIZ_BASE


def n_linhas(nome):
    """Linhas de dados de um CSV (sem o cabeçalho)."""
    with open(PASTA_RESULTADOS / nome, newline="", encoding="utf-8") as f:
        return sum(1 for _ in csv.DictReader(f))


def main():
    if not (RAIZ_BASE / "Datasets" / "Activity").is_dir():
        raise SystemExit(f"Base não encontrada em {RAIZ_BASE}\n"
                         "Ajuste RAIZ_BASE em config.py ou defina a variável de ambiente RAIZ_BASE_CSI.")
    t0 = time.time()
    for titulo, modulo in [("Seção 1 - inventário e contagens", secao1_inventario),
                           ("Seção 2 - seleção das 30 gravações", secao2_selecao),
                           ("Seção 3 - amplitudes, verificação e painéis", secao3_amplitudes)]:
        print(f"\n{'=' * 70}\n{titulo}\n{'=' * 70}")
        modulo.main()

    checagens = [
        ("inventario_gravacoes.csv com 1647 linhas de dados", n_linhas("inventario_gravacoes.csv") == 1647),
        ("contagem_gravacoes.csv com 22 participantes + linha Total", n_linhas("contagem_gravacoes.csv") == 23),
        ("selecao_30_gravacoes.csv com 30 linhas de dados", n_linhas("selecao_30_gravacoes.csv") == 30),
        ("verificacao_amplitude.txt gerado", (PASTA_RESULTADOS / "verificacao_amplitude.txt").is_file()),
        ("5 painéis da seção 3 (30 gráficos)", len(list(PASTA_FIGURAS.glob("secao3_painel_*.png"))) == 5),
    ]
    print(f"\n{'=' * 70}\nConferência dos entregáveis - equipe {ID_EQUIPE}, participantes {', '.join(PARTICIPANTES)}")
    for desc, ok in checagens:
        print(f"  [{'OK' if ok else 'FALHOU'}] {desc}")
    print(f"Tempo total: {time.time() - t0:.0f} s. Resultados em: {PASTA_RESULTADOS}")


if __name__ == "__main__":
    main()
