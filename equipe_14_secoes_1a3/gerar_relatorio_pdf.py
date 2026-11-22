"""
Etapa opcional: converte relatorio.md em relatorio.pdf (com as figuras de resultados/figuras).

Requer:
  * pacote "markdown" (pip install markdown) - usado apenas aqui;
  * Microsoft Edge ou Google Chrome instalado (impressão em PDF em modo headless).
Uso (depois de executar_secoes_1a3.py):
  python gerar_relatorio_pdf.py
"""
import re
import shutil
import subprocess
from pathlib import Path

import markdown

PASTA = Path(__file__).resolve().parent
CANDIDATOS = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "msedge", "google-chrome", "chromium", "chrome",
]
CSS = """
@page { size: A4; margin: 16mm 14mm; }
body { font-family: 'Segoe UI', Arial, sans-serif; font-size: 10.5pt; line-height: 1.42; color: #111; }
h1 { font-size: 18pt; margin-bottom: 4px; } h2 { font-size: 14pt; border-bottom: 1px solid #999;
padding-bottom: 2px; margin-top: 22px; page-break-after: avoid; } h3 { font-size: 11.5pt; page-break-after: avoid; }
table { border-collapse: collapse; margin: 8px 0; font-size: 9pt; page-break-inside: avoid; }
th, td { border: 1px solid #bbb; padding: 2px 6px; } th { background: #eee; }
img { width: 100%; page-break-inside: avoid; margin: 6px 0; }
code { font-family: Consolas, monospace; font-size: 9pt; background: #f3f3f3; padding: 0 2px; }
hr { border: none; border-top: 1px solid #ccc; margin: 18px 0; }
"""


def navegador():
    for c in CANDIDATOS:
        if Path(c).is_file() or shutil.which(c):
            return c if Path(c).is_file() else shutil.which(c)
    raise SystemExit("Edge/Chrome não encontrado. Abra relatorio.html no navegador e use Imprimir > Salvar como PDF.")


def main():
    texto = (PASTA / "relatorio.md").read_text(encoding="utf-8")
    # O relatório usa recuo de 2 espaços em sub-listas (padrão GitHub); a biblioteca markdown exige 4.
    texto = re.sub(r"^( +)", lambda m: " " * (2 * len(m.group(1))), texto, flags=re.MULTILINE)
    corpo = markdown.markdown(texto, extensions=["tables", "sane_lists"])
    html = (f'<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">'
            f"<title>Relatório - Equipe 14</title><style>{CSS}</style></head><body>{corpo}</body></html>")
    arq_html = PASTA / "relatorio.html"
    arq_html.write_text(html, encoding="utf-8")
    arq_pdf = PASTA / "relatorio.pdf"
    subprocess.run([navegador(), "--headless", "--disable-gpu", "--no-pdf-header-footer",
                    f"--print-to-pdf={arq_pdf}", arq_html.as_uri()], check=True, timeout=120)
    print(f"Gerado: {arq_pdf}")


if __name__ == "__main__":
    main()
