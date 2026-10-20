import streamlit as st
import numpy as np
import pandas as pd
import datetime
from pathlib import Path
import plotly.graph_objects as go

st.set_page_config(
    page_title="MMG",
    page_icon="⚙️",
    layout="wide"
)

if "historico" not in st.session_state:
    st.session_state.historico = []

if "mmg_iniciada" not in st.session_state:
    st.session_state.mmg_iniciada = False

if "quantidade_medicoes" not in st.session_state:
    st.session_state.quantidade_medicoes = 3

# ==========================
# ESTILO VISUAL MMG
# ==========================

st.markdown("""
<style>
.stApp {
    background-color: white;
}

section[data-testid="stSidebar"] {
    background-color: #111111;
}

section[data-testid="stSidebar"] * {
    color: white;
}

[data-testid="stMetric"] {
    background: white;
    padding: 15px;
    border-radius: 15px;
    border-left: 6px solid #730000;
    box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.10);
}

.stButton button {
    background-color: #730000;
    color: white;
    border: none;
    border-radius: 12px;
    min-height: 48px;
    font-weight: bold;
}

.stButton button:hover {
    background-color: #500000;
    color: white;
}

.stTextInput input,
.stNumberInput input {
    border-radius: 10px;
}

.mmg-entrada {
    background: #730000;
    color: white;
    padding: 42px 34px;
    border-radius: 12px;
    margin: 10px 0 22px 0;
}

.mmg-entrada h1 {
    color: white;
    margin-bottom: 8px;
}

.mmg-entrada h3 {
    color: white;
}

.mmg-entrada p {
    color: #f5dddd;
    font-size: 17px;
}

.mmg-legenda {
    color: #730000;
    font-weight: 600;
    letter-spacing: 1px;
}
</style>
""", unsafe_allow_html=True)

# ==========================
# TELA DE ENTRADA
# ==========================

if not st.session_state.mmg_iniciada:

    logo = Path("mmg (1).png")

    if logo.exists():
        st.image(str(logo), width=230)
    else:
        st.markdown(
            "<div class='mmg-legenda'>"
            "MMG • ENGENHARIA E METROLOGIA"
            "</div>",
            unsafe_allow_html=True
        )

    st.markdown("""
    <div class="mmg-entrada">
        <div style="font-size:13px;letter-spacing:2px;">
            AUTOMATIC UNCERTAINTY SYSTEM · VERSÃO 1.0
        </div>
        <h1>MMG</h1>
        <h3>Sistema de Cálculo de Incerteza de Medição</h3>
        <p>
            Organize suas medições, estime as incertezas
            e visualize a contribuição de cada componente
            em um só lugar.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.write(
        "Uma ferramenta de apoio à rotina de metrologia "
        "e à análise de resultados de medição."
    )

    if st.button(
        "▶ INICIAR MEDIÇÃO",
        use_container_width=True,
        type="primary"
    ):
        st.session_state.mmg_iniciada = True
        st.rerun()

    st.caption("MMG · Engenharia Mecânica · Versão 1.0")
    st.stop()

# ==========================
# SIDEBAR
# ==========================

logo = Path("mmg (1).png")

if logo.exists():
    st.sidebar.image(str(logo), width=220)
else:
    st.sidebar.markdown("# MMG")

st.sidebar.markdown("---")
st.sidebar.header("MMG")
st.sidebar.write("Automatic Uncertainty System")
st.sidebar.markdown("---")
st.sidebar.write("Versão 1.0")

if logo.exists():
    st.image(str(logo), width=300)

st.link_button(
    "📄 Manual de Uso",
    "https://github.com/magnusdasilvamariaeduarda-pixel/"
    "incertezalab/raw/main/Manual_MMG_IncertezaLab.pdf"
)

st.markdown("""
<h2 style="color:#730000">
Sistema Automático de Cálculo de Incerteza
</h2>
""", unsafe_allow_html=True)

st.divider()

# ==========================
# DADOS DA MEDIÇÃO
# ==========================

col1, col2, col3 = st.columns(3)

with col1:
    grandeza = st.selectbox(
        "Grandeza",
        [
            "Temperatura",
            "Pressão",
            "Comprimento",
            "Massa",
            "Tensão Elétrica",
            "Outro"
        ]
    )

with col2:
    unidade = st.text_input(
        "Unidade",
        placeholder="Ex.: mm, °C, kg, V"
    )

with col3:
    confianca = st.selectbox(
        "Nível de confiança",
        ["90%", "95%", "99%"],
        index=1
    )

# ==========================
# MEDIÇÕES
# ==========================

st.subheader("Medições")

quantidade = st.selectbox(
    "Quantidade de medições",
    options=list(range(2, 21)),
    index=min(
        max(st.session_state.quantidade_medicoes - 2, 0),
        18
    ),
    help="Escolha de 2 a 20 medições."
)

st.session_state.quantidade_medicoes = quantidade

medicoes = []

for i in range(quantidade):
    valor = st.number_input(
        f"Medição {i + 1}",
        value=0.0,
        step=0.01,
        format="%.6f",
        key=f"medicao_{i}"
    )

    medicoes.append(valor)

# ==========================
# INSTRUMENTO E TIPO B
# ==========================

st.subheader("Instrumento de medição")

instrumento = st.selectbox(
    "Instrumento",
    [
        "Paquímetro",
        "Micrômetro",
        "Multímetro",
        "Termômetro",
        "Balança",
        "Outro"
    ]
)

instrumentos = {
    "Paquímetro": {
        "certificado": 0.02,
        "resolucao": 0.05,
        "deriva": 0.01
    },
    "Micrômetro": {
        "certificado": 0.01,
        "resolucao": 0.01,
        "deriva": 0.005
    },
    "Multímetro": {
        "certificado": 0.05,
        "resolucao": 0.01,
        "deriva": 0.02
    },
    "Termômetro": {
        "certificado": 0.10,
        "resolucao": 0.10,
        "deriva": 0.05
    },
    "Balança": {
        "certificado": 0.02,
        "resolucao": 0.01,
        "deriva": 0.01
    }
}

if instrumento in instrumentos:
    valores_padrao = instrumentos[instrumento]
else:
    valores_padrao = {
        "certificado": 0.0,
        "resolucao": 0.0,
        "deriva": 0.0
    }

with st.expander("ℹ️ Entenda as fontes de incerteza"):

    st.write("""
    **Tipo A:** incerteza estimada a partir da repetição
    das medições. A variação dos resultados influencia
    seu valor.

    **Tipo B:** incerteza estimada a partir de outras
    informações disponíveis sobre a medição.

    **Certificado:** informação obtida no certificado
    de calibração do instrumento.

    **Resolução:** menor incremento indicado pelo
    instrumento.

    **Deriva:** alteração das características metrológicas
    do instrumento ao longo do tempo.
    """)

c1, c2, c3 = st.columns(3)

with c1:
    u_certificado = st.number_input(
        "Incerteza do certificado",
        min_value=0.0,
        value=float(valores_padrao["certificado"]),
        step=0.01,
        format="%.6f"
    )

with c2:
    u_resolucao = st.number_input(
        "Resolução",
        min_value=0.0,
        value=float(valores_padrao["resolucao"]),
        step=0.01,
        format="%.6f"
    )

with c3:
    u_deriva = st.number_input(
        "Deriva",
        min_value=0.0,
        value=float(valores_padrao["deriva"]),
        step=0.01,
        format="%.6f"
    )

# ==========================
# CÁLCULO DA INCERTEZA
# ==========================

if st.button(
    "🧮 CALCULAR INCERTEZA",
    use_container_width=True
):

    if not unidade.strip():
        st.error("Informe a unidade da grandeza medida.")

    elif not all(np.isfinite(x) for x in medicoes):
        st.error("Verifique os valores das medições.")

    elif len(medicoes) < 2:
        st.error("Informe pelo menos duas medições.")

    else:
        # Média aritmética
        media = float(np.mean(medicoes))

        # Desvio padrão amostral
        desvio = float(np.std(medicoes, ddof=1))

        # Incerteza padrão Tipo A
        u_a = desvio / np.sqrt(len(medicoes))

        # Incerteza padrão Tipo B combinada
        u_b = np.sqrt(
            u_certificado**2
            + u_resolucao**2
            + u_deriva**2
        )

        # Incerteza padrão combinada
        uc = np.sqrt(u_a**2 + u_b**2)

        # Fator de abrangência aproximado
        if confianca == "90%":
            k = 1.645
        elif confianca == "95%":
            k = 2.0
        else:
            k = 2.576

        # Incerteza expandida
        U = k * uc

        # ==========================
        # GUARDAR RESULTADO
        # ==========================

        resultado = {
            "Data": datetime.datetime.now().strftime(
                "%d/%m/%Y %H:%M"
            ),
            "Grandeza": grandeza,
            "Instrumento": instrumento,
            "Medições": len(medicoes),
            "Média": media,
            "Incerteza expandida": U,
            "Unidade": unidade
        }

        st.session_state.historico.append(resultado)

        # ==========================
        # RESULTADOS
        # ==========================

        st.divider()
        st.subheader("Resultados")

        r1, r2, r3, r4 = st.columns(4)

        with r1:
            st.metric(
                "Valor médio",
                f"{media:.6f} {unidade}"
            )

        with r2:
            st.metric(
                "Desvio padrão",
                f"{desvio:.6f} {unidade}"
            )

        with r3:
            st.metric(
                "Incerteza Tipo A",
                f"{u_a:.6f} {unidade}"
            )

        with r4:
            st.metric(
                "Incerteza Tipo B",
                f"{u_b:.6f} {unidade}"
            )

        c1, c2 = st.columns(2)

        with c1:
            st.metric(
                "Incerteza combinada (Uc)",
                f"{uc:.6f} {unidade}"
            )

        with c2:
            st.metric(
                "Incerteza expandida (U)",
                f"{U:.6f} {unidade}"
            )

        st.markdown(
            f"### Resultado final: "
            f"**({media:.6f} ± {U:.6f}) {unidade}**"
        )

        st.caption(
            f"Nível de confiança selecionado: {confianca} · "
            f"Fator de abrangência utilizado: k = {k}"
        )

        # ==========================
        # CONTRIBUIÇÕES
        # ==========================

        st.divider()
        st.subheader("Contribuição das fontes de incerteza")

        fontes = [
            "Tipo A",
            "Certificado",
            "Resolução",
            "Deriva"
        ]

        componentes = [
            u_a,
            u_certificado,
            u_resolucao,
            u_deriva
        ]

        variancias = [x**2 for x in componentes]
        total = sum(variancias)

        if total > 0:
            percentuais = [
                (v / total) * 100
                for v in variancias
            ]

            fig = go.Figure(
                data=[
                    go.Bar(
                        x=fontes,
                        y=percentuais,
                        marker_color=[
                            "#730000",
                            "#C62828",
                            "#F57C00",
                            "#1565C0"
                        ],
                        text=[
                            f"{p:.2f}%"
                            for p in percentuais
                        ],
                        textposition="auto"
                    )
                ]
            )

            fig.update_layout(
                title="Contribuição percentual para a variância",
                xaxis_title="Fonte de incerteza",
                yaxis_title="Contribuição (%)",
                yaxis=dict(range=[0, 100]),
                paper_bgcolor="white",
                plot_bgcolor="white",
                height=420
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

            indice_maior = int(np.argmax(percentuais))

            st.write(
                f"**Maior contribuição:** "
                f"{fontes[indice_maior]} "
                f"({percentuais[indice_maior]:.2f}%)."
            )

            st.write("### Detalhamento das contribuições")

            colunas = st.columns(4)

            for i, coluna in enumerate(colunas):
                with coluna:
                    st.metric(
                        fontes[i],
                        f"{percentuais[i]:.2f}%"
                    )

        else:
            st.warning(
                "Todas as fontes de incerteza estão zeradas. "
                "Não há contribuições para representar no gráfico."
            )

# ==========================
# HISTÓRICO
# ==========================

if st.session_state.historico:

    st.divider()
    st.subheader("Histórico de medições")

    historico_df = pd.DataFrame(
        st.session_state.historico
    )

    st.dataframe(
        historico_df,
        use_container_width=True,
        hide_index=True
    )

    csv = historico_df.to_csv(
        index=False
    ).encode("utf-8-sig")

    st.download_button(
        label="📥 Exportar histórico em CSV",
        data=csv,
        file_name="historico_mmg.csv",
        mime="text/csv"
    )

# ==========================
# RODAPÉ
# ==========================

st.markdown("""
<hr>
<div style="text-align:center;color:#666666;font-size:14px;">
MMG • Sistema de Cálculo de Incerteza de Medição<br>
Engenharia Mecânica<br>
Versão 1.0
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")
