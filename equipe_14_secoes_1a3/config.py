"""
Configuração comum às seções 1, 2 e 3 - Trabalho final, Parte 1.
Edite apenas RAIZ_BASE e ID_EQUIPE.
"""
import os
from pathlib import Path

# Caminho da pasta raiz Embedded_WiFi_Sensing-main (a que contém Datasets/ e Scripts/).
# Também pode ser informado pela variável de ambiente RAIZ_BASE_CSI, sem editar este arquivo.
RAIZ_BASE = Path(os.environ.get(
    "RAIZ_BASE_CSI",
    r"C:\Users\Willi\Downloads\ufam\Embedded_WiFi_Sensing-main\Embedded_WiFi_Sensing-main"))

# ID da equipe na tabela da seção 2.2 do enunciado.
ID_EQUIPE = 14

# Participantes da base atribuídos a cada equipe (tabela 2.2 do enunciado; equipe 9 cancelada).
PARTICIPANTES_POR_EQUIPE = {
    1: ["s1", "s2", "s3"],    2: ["s4", "s5", "s6"],    3: ["s7", "s8", "s9"],
    4: ["s10", "s11", "s12"], 5: ["s13", "s14", "s15"], 6: ["s16", "s17", "s19"],
    7: ["s21", "s22", "s23"], 8: ["s24", "s1", "s2"],   10: ["s6", "s7", "s8"],
    11: ["s9", "s10", "s11"], 12: ["s12", "s13", "s14"], 13: ["s15", "s16", "s17"],
    14: ["s19", "s21", "s22"], 15: ["s23", "s24", "s1"], 16: ["s2", "s3", "s4"],
    17: ["s5", "s6", "s7"],
}
PARTICIPANTES = PARTICIPANTES_POR_EQUIPE[ID_EQUIPE]

ATIVIDADES = ["FA", "GU", "LD", "SD", "WA"]
NOMES_ATIVIDADES = {"FA": "queda", "GU": "levantar-se", "LD": "deitar-se",
                    "SD": "sentar-se", "WA": "caminhar"}

PAR_ANALISADO = 20          # par de CSI (contado a partir de 1) usado na seção 3

PASTA_PROJETO = Path(__file__).resolve().parent
PASTA_RESULTADOS = PASTA_PROJETO / "resultados"
PASTA_FIGURAS = PASTA_RESULTADOS / "figuras"
