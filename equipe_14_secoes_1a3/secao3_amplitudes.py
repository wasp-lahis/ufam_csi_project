"""
Seção 3 - Calcular e visualizar as amplitudes de CSI.

  * calcula as matrizes de amplitude (registros x 64) dos 30 TXT selecionados (seção 2);
  * tabela de verificação do par 20 (uma linha) -> resultados/verificacao_amplitude.txt;
  * 5 painéis (um por atividade), cada um com 3 séries temporais do par 20 e 3 mapas de calor
    dos 64 pares, usando as 15 gravações com ordem_selecao = 1 -> resultados/figuras/secao3_painel_XX.png;
  * estatísticas de apoio à interpretação -> resultados/estatisticas_secao3.txt.

Requer: resultados/selecao_30_gravacoes.csv (python secao2_selecao.py)
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from comum import ler_csv, ler_txt_csi, amplitudes
from config import ATIVIDADES, NOMES_ATIVIDADES, PARTICIPANTES, PAR_ANALISADO, PASTA_RESULTADOS, PASTA_FIGURAS

JANELA = 100   # registros por janela, para localizar trechos de maior/menor variação


def nome_txt(caminho):
    return caminho.rsplit("/", 1)[-1]


def main():
    PASTA_FIGURAS.mkdir(parents=True, exist_ok=True)
    selecao = ler_csv("selecao_30_gravacoes.csv")

    # ---------- 3.2 amplitudes dos 30 TXT ----------
    brutos, amps = {}, {}
    for s in selecao:
        m = ler_txt_csi(s["caminho_txt"])
        brutos[s["caminho_txt"]] = m
        amps[s["caminho_txt"]] = amplitudes(m)
        assert amps[s["caminho_txt"]].shape == (int(s["n_registros"]), 64)
    print(f"Matrizes de amplitude calculadas: {len(amps)} (registros x 64)")

    graf = {(s["participante"], s["atividade"]): s for s in selecao if s["ordem_selecao"] == "1"}

    # ---------- 3.3 verificação de uma amplitude ----------
    ref = graf[(PARTICIPANTES[0], ATIVIDADES[0])]
    linha = 1
    im = brutos[ref["caminho_txt"]][linha - 1, 2 * PAR_ANALISADO - 1]   # coluna 40 do TXT (base 1)
    re = brutos[ref["caminho_txt"]][linha - 1, 2 * PAR_ANALISADO]       # coluna 41 do TXT (base 1)
    amp = amps[ref["caminho_txt"]][linha - 1, PAR_ANALISADO - 1]        # coluna 20 da matriz
    assert np.isclose(amp, np.hypot(re, im))
    tabela = ("TXT | Linha | Par | Imaginária | Real | Amplitude\n"
              f"{nome_txt(ref['caminho_txt'])} | {linha} | {PAR_ANALISADO} | {im:g} | {re:g} | "
              + f"{amp:.2f}".replace(".", ",") + "\n"
              f"(participante {ref['participante']}, atividade {ref['atividade']}, ordem_selecao=1; "
              f"Imaginária = coluna {2 * PAR_ANALISADO} do TXT, Real = coluna {2 * PAR_ANALISADO + 1}, "
              f"Amplitude = coluna {PAR_ANALISADO} da matriz)\n")
    (PASTA_RESULTADOS / "verificacao_amplitude.txt").write_text(tabela, encoding="utf-8")
    print("\nVerificação:\n" + tabela)

    # ---------- escalas comuns ----------
    mats = {k: amps[s["caminho_txt"]] for k, s in graf.items()}
    y_max = max(m[:, PAR_ANALISADO - 1].max() for m in mats.values())
    y_lim = (0, np.ceil(y_max * 1.05))
    # Par 1 (~115, quase constante) dominaria a escala; a escala comum vai até o percentil 99,9
    # dos demais pares e valores acima aparecem saturados (seta na barra de cores).
    todos = np.vstack([m[:, 1:] for m in mats.values()])
    c_max = float(np.ceil(np.percentile(todos, 99.9)))
    print(f"Limites comuns: séries 0-{y_lim[1]:.0f}; mapas de calor 0-{c_max:.0f}")

    # ---------- 3.4/3.5 painéis ----------
    for n_fig, a in enumerate(ATIVIDADES, start=1):
        fig, ax = plt.subplots(2, 3, figsize=(17, 8.5), constrained_layout=True)
        for j, p in enumerate(PARTICIPANTES):
            s = graf[(p, a)]
            m = mats[(p, a)]
            idx = np.arange(1, m.shape[0] + 1)
            t = ax[0, j]
            t.plot(idx, m[:, PAR_ANALISADO - 1], lw=0.8, color=f"C{j}", label=nome_txt(s["caminho_txt"]))
            t.set_ylim(*y_lim)
            t.set_xlim(1, m.shape[0])
            t.set_title(f"{p} | {a} ({NOMES_ATIVIDADES[a]}) | par {PAR_ANALISADO}")
            t.set_xlabel("Índice do registro")
            t.set_ylabel(f"Amplitude do par {PAR_ANALISADO} (u.r.)")
            t.legend(loc="upper right", fontsize=8)
            t.grid(alpha=0.3)

            h = ax[1, j]
            im_ = h.imshow(m.T, aspect="auto", origin="lower", cmap="viridis", vmin=0, vmax=c_max,
                           extent=[0.5, m.shape[0] + 0.5, 0.5, 64.5], interpolation="nearest")
            h.set_title(f"{p} | {a} ({NOMES_ATIVIDADES[a]})\n{nome_txt(s['caminho_txt'])}", fontsize=10)
            h.set_xlabel("Índice do registro")
            h.set_ylabel("Par de CSI (1-64)")
            h.set_yticks([1, 10, 20, 28, 38, 50, 64])
        fig.colorbar(im_, ax=ax[1, :], label="Amplitude (u.r.)", extend="max", shrink=0.9)
        fig.suptitle(f"Figura 3.{n_fig} - Atividade {a} ({NOMES_ATIVIDADES[a]}): amplitude do par "
                     f"{PAR_ANALISADO} (acima) e dos 64 pares (abaixo), gravações com ordem_selecao=1",
                     fontsize=13)
        saida = PASTA_FIGURAS / f"secao3_painel_{n_fig}_{a}.png"
        fig.savefig(saida, dpi=130)
        plt.close(fig)
        print(f"Salvo: {saida.name}")

    # ---------- estatísticas de apoio à interpretação ----------
    linhas = [f"Janelas de {JANELA} registros; variação = desvio padrão do par {PAR_ANALISADO} na janela.", ""]
    for a in ATIVIDADES:
        for p in PARTICIPANTES:
            m = mats[(p, a)]
            x = m[:, PAR_ANALISADO - 1]
            n_j = len(x) // JANELA
            dp = np.array([x[i * JANELA:(i + 1) * JANELA].std() for i in range(n_j)])
            imax, imin = int(dp.argmax()), int(dp.argmin())
            linhas.append(
                f"{p} {a}: média {x.mean():6.2f}  dp {x.std():5.2f}  min {x.min():5.2f}  max {x.max():5.2f} | "
                f"maior variação: registros {imax * JANELA + 1}-{(imax + 1) * JANELA} (dp {dp[imax]:.2f}); "
                f"menor: {imin * JANELA + 1}-{(imin + 1) * JANELA} (dp {dp[imin]:.2f})")
    linhas.append("")
    tudo = np.vstack(list(mats.values()))
    media, dp = tudo.mean(axis=0), tudo.std(axis=0)
    linhas.append("Pares (15 gravações juntas): média e desvio padrão")
    for i in range(64):
        linhas.append(f"  par {i + 1:2d}: média {media[i]:7.2f}  dp {dp[i]:6.2f}")
    linhas.append("")
    linhas.append("Pares com média < 1 (próximos de zero): "
                  + ", ".join(str(i + 1) for i in range(64) if media[i] < 1))
    cv = dp / np.where(media > 0, media, np.nan)
    linhas.append("Pares com coeficiente de variação < 0,05 (quase constantes): "
                  + ", ".join(str(i + 1) for i in range(64) if cv[i] < 0.05))
    (PASTA_RESULTADOS / "estatisticas_secao3.txt").write_text("\n".join(linhas) + "\n", encoding="utf-8")
    print("Salvo: estatisticas_secao3.txt")


if __name__ == "__main__":
    main()
