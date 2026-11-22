"""
Seção 2 - Selecionar as 30 gravações de análise.

Para cada participante da equipe (config.PARTICIPANTES) e cada atividade:
  1. pega no inventário (seção 1) os TXT daquela pasta;
  2. ordena os nomes em ordem crescente;
  3. seleciona os dois primeiros que possam ser lidos e cujas linhas não vazias tenham,
     todas, 129 valores numéricos finitos. Os demais casos são registrados como desconsiderados.

Gera:
  resultados/selecao_30_gravacoes.csv
  resultados/arquivos_desconsiderados.csv  (vazio, só cabeçalho, se nenhum arquivo for descartado)
Requer: resultados/inventario_gravacoes.csv (python secao1_inventario.py)
"""
from comum import ler_csv, escrever_csv
from config import ID_EQUIPE, PARTICIPANTES, ATIVIDADES


def arquivo_valido(r):
    total = int(r["total_registros"])
    return total > 0 and int(r["registros_formato_valido"]) == total and r["problemas_leitura"] == "nenhum"


def motivo_descarte(r):
    if int(r["total_registros"]) == 0:
        return "arquivo vazio ou falha de leitura: " + r["problemas_leitura"]
    return "linhas fora do formato: " + r["problemas_leitura"]


def main():
    inventario = ler_csv("inventario_gravacoes.csv")
    selecao, descartados = [], []

    for p in PARTICIPANTES:
        for a in ATIVIDADES:
            candidatos = sorted((r for r in inventario if r["participante"] == p and r["atividade"] == a),
                                key=lambda r: r["caminho_txt"].rsplit("/", 1)[-1])
            escolhidos, pendentes = [], []     # pendentes: descartados à espera do substituto
            for r in candidatos:
                if len(escolhidos) == 2:
                    break
                if arquivo_valido(r):
                    escolhidos.append(r)
                    for d in pendentes:        # o próximo TXT válido substitui os descartados anteriores
                        descartados.append({"participante": p, "atividade": a,
                                            "caminho_txt": d["caminho_txt"], "motivo": motivo_descarte(d),
                                            "substituto": r["caminho_txt"]})
                    pendentes = []
                else:
                    pendentes.append(r)
            if len(escolhidos) < 2:
                raise SystemExit(f"{p}/{a}: menos de 2 TXT válidos disponíveis")
            for ordem, r in enumerate(escolhidos, start=1):
                selecao.append({"participante": p, "atividade": a, "caminho_txt": r["caminho_txt"],
                                "ordem_selecao": ordem, "n_registros": int(r["total_registros"])})

    escrever_csv("selecao_30_gravacoes.csv", selecao,
                 ["participante", "atividade", "caminho_txt", "ordem_selecao", "n_registros"])
    escrever_csv("arquivos_desconsiderados.csv", descartados,
                 ["participante", "atividade", "caminho_txt", "motivo", "substituto"])

    print(f"Equipe {ID_EQUIPE} - participantes {', '.join(PARTICIPANTES)}")
    print(f"Gravações selecionadas: {len(selecao)}")
    print(f"Arquivos desconsiderados: {len(descartados)}")
    for d in descartados:
        print(f"  {d['caminho_txt']}: {d['motivo']} -> substituto {d['substituto']}")
    for s in selecao:
        print(f"  {s['participante']} {s['atividade']} {s['ordem_selecao']} {s['caminho_txt']} ({s['n_registros']})")


if __name__ == "__main__":
    main()
