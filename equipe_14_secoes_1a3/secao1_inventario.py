"""
Trabalho final - Parte 1 | Seção 1: Organizar e verificar as gravações de atividades
Equipe 14 - Stephany Castro da Silva; Lahis Gomes de Almeida
Participantes da base atribuídos à equipe: s19, s21 e s22 (usados a partir da seção 2)

Gera:
  resultados/inventario_gravacoes.csv      -> uma linha por TXT (seção 1.2)
  resultados/contagem_gravacoes.csv        -> participante x atividade, com totais (seção 1.3)
  resultados/resumo_secao1.txt             -> comparação com o artigo (1.647 gravações / 22 participantes)

Uso:
  python secao1_inventario.py                       (usa RAIZ_BASE de config.py)
  python secao1_inventario.py "C:/caminho/Embedded_WiFi_Sensing-main"

Somente biblioteca padrão do Python (>= 3.8); nenhum pacote externo é necessário.
"""

import csv
import math
import re
import sys
from collections import defaultdict
from pathlib import Path

# Configuração (caminho da base, ID da equipe, pastas) em config.py
from config import RAIZ_BASE, ID_EQUIPE, PASTA_RESULTADOS, ATIVIDADES

N_CAMPOS = 129                                # 1 temporal + 64 pares (imag, real)
PADRAO_TXT = re.compile(r"^csi_data_\d+\.txt$")

ARTIGO_GRAVACOES = 1647
ARTIGO_PARTICIPANTES = 22


def chave_participante(nome):
    """Ordena s1, s2, ..., s10 numericamente (e não s1, s10, s11, s2...)."""
    m = re.match(r"^s(\d+)$", nome)
    return (0, int(m.group(1))) if m else (1, nome)


def campo_numerico_finito(texto):
    """Retorna (ok, motivo). Aceita inteiros e reais; rejeita vazio, texto, nan e inf."""
    t = texto.strip()
    if t == "":
        return False, "valor vazio"
    try:
        v = float(t)
    except ValueError:
        return False, "valor não numérico"
    if not math.isfinite(v):
        return False, "valor não finito"
    return True, ""


def verificar_txt(caminho):
    """
    Lê um TXT de CSI e devolve (total_registros, registros_formato_valido, problemas_leitura).
      total_registros          = linhas não vazias, incluindo as com erro de formato
      registros_formato_valido = linhas com exatamente 129 valores numéricos finitos
      problemas_leitura        = 'nenhum' ou lista 'motivo: linhas ...'
    """
    try:
        # utf-8-sig remove um eventual BOM; errors="replace" evita abortar por byte inválido
        with open(caminho, "r", encoding="utf-8-sig", errors="replace", newline="") as f:
            linhas = f.read().splitlines()
    except OSError as e:
        return 0, 0, f"falha de leitura do arquivo ({type(e).__name__}: {e})"

    total = 0
    validos = 0
    erros = defaultdict(list)   # motivo -> [números das linhas no arquivo, contados a partir de 1]

    for n_linha, linha in enumerate(linhas, start=1):
        if linha.strip() == "":
            continue                      # linha vazia não é registro
        total += 1
        campos = linha.strip().split(",")
        if len(campos) != N_CAMPOS:
            erros[f"{len(campos)} valores (esperado {N_CAMPOS})"].append(n_linha)
            continue
        motivo_linha = ""
        for c in campos:
            ok, motivo = campo_numerico_finito(c)
            if not ok:
                motivo_linha = motivo
                break
        if motivo_linha:
            erros[motivo_linha].append(n_linha)
        else:
            validos += 1

    if total == 0:
        return 0, 0, "arquivo vazio (nenhuma linha com dados)"
    if not erros:
        return total, validos, "nenhum"

    partes = []
    for motivo, nums in erros.items():
        lista = ", ".join(map(str, nums[:10])) + (f" ... (+{len(nums) - 10})" if len(nums) > 10 else "")
        partes.append(f"linha(s) {lista}: {motivo}")
    return total, validos, "; ".join(partes)


def main():
    raiz = Path(sys.argv[1]) if len(sys.argv) > 1 else RAIZ_BASE
    pasta_activity = raiz / "Datasets" / "Activity"
    if not pasta_activity.is_dir():
        sys.exit(f"Pasta não encontrada: {pasta_activity}\nAjuste RAIZ_BASE ou passe o caminho como argumento.")
    PASTA_RESULTADOS.mkdir(parents=True, exist_ok=True)

    inventario = []
    contagem = defaultdict(lambda: defaultdict(int))     # participante -> atividade -> nº de TXT
    pastas_existentes = set()
    ignorados = []                                       # arquivos fora do padrão csi_data_*.txt

    for atividade in ATIVIDADES:
        pasta_ativ = pasta_activity / atividade
        if not pasta_ativ.is_dir():
            print(f"AVISO: pasta da atividade {atividade} não existe")
            continue
        for item in sorted(pasta_ativ.iterdir(), key=lambda p: chave_participante(p.name)):
            if not item.is_dir():
                ignorados.append(item.relative_to(raiz).as_posix())
                continue
            participante = item.name
            pastas_existentes.add(participante)
            contagem[participante][atividade] += 0          # garante a célula mesmo com 0 arquivos
            for arq in sorted(item.rglob("*")):             # rglob: inclui eventuais subpastas
                if not arq.is_file():
                    continue
                rel = arq.relative_to(raiz).as_posix()
                if not PADRAO_TXT.match(arq.name):
                    ignorados.append(rel)
                    continue
                total, validos, problemas = verificar_txt(arq)
                inventario.append({
                    "atividade": atividade,
                    "participante": participante,
                    "caminho_txt": rel,
                    "total_registros": total,
                    "registros_formato_valido": validos,
                    "problemas_leitura": problemas,
                })
                contagem[participante][atividade] += 1

    # ---------------- 1.2 inventário ----------------
    arq_inv = PASTA_RESULTADOS / "inventario_gravacoes.csv"
    with open(arq_inv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["atividade", "participante", "caminho_txt",
                                          "total_registros", "registros_formato_valido",
                                          "problemas_leitura"])
        w.writeheader()
        w.writerows(inventario)

    # ---------------- 1.3 contagem ----------------
    participantes = sorted(contagem, key=chave_participante)
    tot_ativ = {a: sum(contagem[p][a] for p in participantes) for a in ATIVIDADES}
    total_base = sum(tot_ativ.values())
    arq_cont = PASTA_RESULTADOS / "contagem_gravacoes.csv"
    with open(arq_cont, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["participante"] + ATIVIDADES + ["total"])
        for p in participantes:
            w.writerow([p] + [contagem[p][a] for a in ATIVIDADES] + [sum(contagem[p].values())])
        w.writerow(["Total"] + [tot_ativ[a] for a in ATIVIDADES] + [total_base])

    # ---------------- comparação com o artigo ----------------
    com_gravacao = [p for p in participantes if sum(contagem[p].values()) > 0]
    com_todas = [p for p in participantes if all(contagem[p][a] > 0 for a in ATIVIDADES)]
    nums = sorted(int(p[1:]) for p in pastas_existentes if re.match(r"^s\d+$", p))
    ausentes = [f"s{i}" for i in range(1, max(nums) + 1) if i not in nums] if nums else []
    com_problema = [r for r in inventario if r["problemas_leitura"] != "nenhum"]
    dif_15 = [(p, a, contagem[p][a]) for p in participantes for a in ATIVIDADES if contagem[p][a] != 15]

    linhas = [
        f"Equipe {ID_EQUIPE} - Seção 1",
        f"Raiz da base: {raiz}",
        "",
        f"Gravações (TXT) inventariadas ........: {len(inventario)}   (artigo: {ARTIGO_GRAVACOES})",
        f"Pastas de participantes existentes ...: {len(pastas_existentes)}",
        f"Participantes com >= 1 gravação ......: {len(com_gravacao)}   (artigo: {ARTIGO_PARTICIPANTES})",
        f"Participantes com as 5 atividades ....: {len(com_todas)}",
        f"Identificadores ausentes na sequência : {', '.join(ausentes) or 'nenhum'}",
        f"Arquivos ignorados (fora do padrão) ..: {len(ignorados)}",
        *[f"    {x}" for x in ignorados],
        f"TXT com problema de leitura/formato ..: {len(com_problema)}",
        *[f"    {r['caminho_txt']}: {r['problemas_leitura']}" for r in com_problema],
        f"Registros (linhas não vazias) totais .: {sum(r['total_registros'] for r in inventario)}",
        f"Registros com formato válido .........: {sum(r['registros_formato_valido'] for r in inventario)}",
        "",
        "Células participante x atividade diferentes de 15 gravações:",
        *[f"    {p} {a}: {n}" for p, a, n in dif_15],
    ]
    resumo = "\n".join(linhas)
    (PASTA_RESULTADOS / "resumo_secao1.txt").write_text(resumo + "\n", encoding="utf-8")

    print(resumo)
    print("\nTabela de contagens:")
    print(f"{'participante':<13}" + "".join(f"{a:>6}" for a in ATIVIDADES) + f"{'total':>7}")
    for p in participantes:
        print(f"{p:<13}" + "".join(f"{contagem[p][a]:>6}" for a in ATIVIDADES)
              + f"{sum(contagem[p].values()):>7}")
    print(f"{'Total':<13}" + "".join(f"{tot_ativ[a]:>6}" for a in ATIVIDADES) + f"{total_base:>7}")
    print(f"\nArquivos salvos em: {PASTA_RESULTADOS}")


if __name__ == "__main__":
    main()
