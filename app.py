import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import datetime

st.set_page_config(
    page_title="MMG",
    page_icon="⚙️",
    layout="wide"
)
if "historico" not in st.session_state:
    st.session_state.historico = []

# ==========================
# ESTILO VISUAL MMG
# ==========================

st.markdown("""
<style>

/* Fundo */
.stApp{
    background-color:white;
}

/* Sidebar */
section[data-testid="stSidebar"]{
    background-color:#111111;
}

/* Texto da Sidebar */
section[data-testid="stSidebar"] *{
    color:white;
}

/* Cards */
[data-testid="stMetric"]{
    background:white;
    padding:15px;
    border-radius:15px;
    border-left:6px solid #730000;
    box-shadow:0px 4px 10px rgba(0,0,0,0.10);
}

/* Botões */
.stButton button{
    background-color:#730000;
    color:white;
    border:none;
    border-radius:12px;
    height:55px;
    font-weight:bold;
}

.stButton button:hover{
    background-color:#500000;
}

/* Inputs */
.stTextInput input,
.stTextArea textarea{
    border-radius:10px;
}

</style>
""", unsafe_allow_html=True)

# ==========================
# SIDEBAR
# ==========================

st.sidebar.image("mmg (1).png", width=220)

st.sidebar.markdown("---")

st.sidebar.header("MMG")

st.sidebar.write(
    "Automatic Uncertainty System"
)

st.sidebar.markdown("---")

st.sidebar.write("Versão 1.0")

st.image(
    "mmg (1).png",
    width=500
)

st.link_button(
    "📄 Manual de Uso",
    "https://github.com/magnusdasilvamariaeduarda-pixel/incertezalab/raw/main/Manual_MMG_IncertezaLab.pdf"
)
st.markdown("""
<h2 style='color:#730000'>
Sistema Automático de Cálculo de Incerteza
</h2>
""", unsafe_allow_html=True)
st.divider()

# ==========================
# DADOS
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
        ""
    )

with col3:
    confianca = st.selectbox(
        "Nível de confiança",
        [
            "90%",
            "95%",
            "99%"
        ],
        index=1
    )

st.subheader("Medições")

if "quantidade_medicoes" not in st.session_state:
    st.session_state.quantidade_medicoes = 3

medicoes = []

for i in range(st.session_state.quantidade_medicoes):

    valor = st.number_input(
        f"Medição {i + 1}",
        min_value=0.0,
        value=0.0,
        step=0.01,
        format="%.2f",
        key=f"medicao_{i}"
    )

    if valor != 0:
        medicoes.append(valor)

if st.button("➕ Adicionar medição"):
    st.session_state.quantidade_medicoes += 1
    st.rerun()
# ==========================
# TIPO B
# ==========================

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
    valor_certificado = instrumentos[instrumento]["certificado"]
    valor_resolucao = instrumentos[instrumento]["resolucao"]
    valor_deriva = instrumentos[instrumento]["deriva"]
else:
    valor_certificado = 0.00
    valor_resolucao = 0.00
    valor_deriva = 0.00

st.subheader("  ")

with st.expander("ℹ️ Informações; "):

    st.write("""
O que signfica: Certificado, Resolução e Deriva; E Inct. Tipo A e B

📊 Tipo A: incerteza obtida a partir da repetição das medições. Quanto maior a variação entre os valores medidos, maior será a incerteza Tipo A.

📐 Tipo B: incerteza calculada a partir das características do instrumento, como certificado, resolução e deriva.

📄 Certificado: valor informado pelo certificado de calibração.

📏 Resolução: menor variação que o instrumento consegue mostrar.

⏳ Deriva: alteração do instrumento causada pelo tempo e uso.
""")

c1, c2, c3 = st.columns(3)

with c1:
    u_certificado = st.number_input(
        "Certificado",
        min_value=0.0,
        value=float(valor_certificado),
        step=0.01
    )

with c2:
    u_resolucao = st.number_input(
        "Resolução",
        min_value=0.0,
        value=float(valor_resolucao),
        step=0.01
    )

with c3:
    u_deriva = st.number_input(
        "Deriva",
        min_value=0.0,
        value=float(valor_deriva),
        step=0.01
    )

# ==========================
# BOTÃO
# ==========================

if st.button(
    "🧮 Calcular Incerteza",
    use_container_width=True
):

    try:

        if len(medicoes) < 2:

            st.error(
                "Informe pelo menos duas medições."
            )

        else:

            media = np.mean(medicoes)

            desvio = np.std(
                medicoes,
                ddof=1
            )

            u_a = desvio / np.sqrt(
                len(medicoes)
            )

            u_b = np.sqrt(
                u_certificado**2 +
                u_resolucao**2 +
                u_deriva**2
            )

            uc = np.sqrt(
                u_a**2 +
                u_b**2
            )

            if confianca == "90%":
                k = 1.645

            elif confianca == "95%":
                k = 2.0

            else:
                k = 2.576

            U = k * uc

            # ==========================
            # HISTÓRICO
            # ==========================

            st.session_state.historico.append({
                "Data": datetime.datetime.now().strftime(
                    "%d/%m/%Y %H:%M"
                ),
                "Instrumento": instrumento,
                "Resultado": (
                    f"{media:.6f} ± "
                    f"{U:.6f} {unidade}"
                )
            })

            # ==========================
            # RESULTADOS
            # ==========================

            st.subheader("Resultados")

            r1, r2, r3, r4 = st.columns(4)

            with r1:

                st.metric(
                    "Valor Médio",
                    f"{media:.6f}"
                )

            with r2:

                st.metric(
                    "Desvio Padrão",
                    f"{desvio:.6f}"
                )

            with r3:

                st.metric(
                    "Tipo A",
                    f"{u_a:.6f}"
                )

            with r4:

                st.metric(
                    "Tipo B",
                    f"{u_b:.6f}"
                )

            st.divider()

            c1, c2 = st.columns(2)

            with c1:

                st.metric(
                    "Incerteza Combinada (Uc)",
                    f"{uc:.6f}"
                )

            with c2:

                st.metric(
                    "Incerteza Expandida (U)",
                    f"{U:.6f} {unidade}"
                )

            # ==========================
            # DADOS DO GRÁFICO
            # ==========================

            st.divider()

            total = (
                u_a**2 +
                u_certificado**2 +
                u_resolucao**2 +
                u_deriva**2
            )

            if total > 0:

                fontes = [
                    "Tipo A",
                    "Certificado",
                    "Resolução",
                    "Deriva"
                ]

                percentuais = [
                    (u_a**2 / total) * 100,
                    (u_certificado**2 / total) * 100,
                    (u_resolucao**2 / total) * 100,
                    (u_deriva**2 / total) * 100
                ]

                cores = [
                    "#730000",
                    "#C62828",
                    "#F57C00",
                    "#1565C0"
                ]

                # ==========================
                # ONDA SENOIDAL
                # ==========================

                import plotly.graph_objects as go

                espacamento = 2 * np.pi

                pontos_por_trecho = 250

                fig = go.Figure()

                for i, fonte in enumerate(fontes):

                    inicio = i * espacamento

                    fim = (
                        (i + 1) *
                        espacamento
                    )

                    x_trecho = np.linspace(
                        inicio,
                        fim,
                        pontos_por_trecho
                    )

                    if max(percentuais) > 0:

                        amplitude = (
                            percentuais[i] /
                            max(percentuais)
                        ) * 2

                    else:

                        amplitude = 0

                    y_trecho = (
                        amplitude *
                        np.sin(
                            x_trecho - inicio
                        )
                    )

                    fig.add_trace(
                        go.Scatter(
                            x=x_trecho,
                            y=y_trecho,
                            mode="lines",
                            name=(
                                f"{fonte} — "
                                f"{percentuais[i]:.2f}%"
                            ),
                            line=dict(
                                color=cores[i],
                                width=5,
                                shape="spline"
                            )
                        )
                    )

                    if i < len(fontes) - 1:

                        fig.add_vline(
                            x=fim,
                            line_width=1,
                            line_dash="dot",
                            line_color="#CCCCCC"
                        )

                # ==========================
                # CONFIGURAÇÃO DO GRÁFICO
                # ==========================

                fig.update_layout(

                    title=dict(
                        text=(
                            "Contribuição das "
                            "Fontes de Incerteza"
                        ),
                        font=dict(
                            size=22,
                            color="#730000"
                        ),
                        x=0.5
                    ),

                    xaxis=dict(

                        title=(
                            "Fontes de Incerteza"
                        ),

                        tickmode="array",

                        tickvals=[
                            espacamento * 0.5,
                            espacamento * 1.5,
                            espacamento * 2.5,
                            espacamento * 3.5
                        ],

                        ticktext=fontes,

                        showgrid=False,

                        zeroline=False
                    ),

                    yaxis=dict(

                        title="Amplitude relativa",

                        showgrid=True,

                        gridcolor="#E5E5E5",

                        zeroline=True,

                        zerolinecolor="#999999"
                    ),

                    paper_bgcolor="white",

                    plot_bgcolor="white",

                    height=500,

                    margin=dict(
                        l=70,
                        r=40,
                        t=80,
                        b=100
                    ),

                    legend=dict(

                        orientation="h",

                        yanchor="bottom",

                        y=-0.25,

                        xanchor="center",

                        x=0.5
                    )
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

                # ==========================
                # LEITURA DO GRÁFICO
                # ==========================

                st.subheader(
                    "📖 Leitura do Gráfico"
                )

                st.write(
                    "O gráfico mostra a contribuição percentual "
                    "de cada componente para a incerteza "
                    "combinada. Quanto maior o percentual, "
                    "maior é sua influência no resultado final."
                )

                indice_maior = np.argmax(
                    percentuais
                )

                maior_fonte = fontes[
                    indice_maior
                ]

                maior_percentual = percentuais[
                    indice_maior
                ]

                st.write(
                    f"**Maior contribuição:** "
                    f"{maior_fonte} "
                    f"({maior_percentual:.2f}%)"
                )

                st.write(
                    "A componente com maior percentual é a que "
                    "mais influencia a incerteza combinada."
                )

                # ==========================
                # CONTRIBUIÇÃO INDIVIDUAL
                # ==========================

                st.write(
                    "### 📊 Contribuição de cada componente"
                )

                c1, c2, c3, c4 = st.columns(4)

                with c1:

                    st.markdown(
                        """
                        <div style="
                            height: 6px;
                            background-color: #730000;
                            border-radius: 10px 10px 0 0;
                            margin-bottom: -1px;
                        "></div>
                        """,
                        unsafe_allow_html=True
                    )

                    st.metric(
                        "Tipo A",
                        f"{percentuais[0]:.2f}%"
                    )

                with c2:

                    st.markdown(
                        """
                        <div style="
                            height: 6px;
                            background-color: #C62828;
                            border-radius: 10px 10px 0 0;
                            margin-bottom: -1px;
                        "></div>
                        """,
                        unsafe_allow_html=True
                    )

                    st.metric(
                        "Certificado",
                        f"{percentuais[1]:.2f}%"
                    )

                with c3:

                    st.markdown(
                        """
                        <div style="
                            height: 6px;
                            background-color: #F57C00;
                            border-radius: 10px 10px 0 0;
                            margin-bottom: -1px;
                        "></div>
                        """,
                        unsafe_allow_html=True
                    )

                    st.metric(
                        "Resolução",
                        f"{percentuais[2]:.2f}%"
                    )

                with c4:

                    st.markdown(
                        """
                        <div style="
                            height: 6px;
                            background-color: #1565C0;
                            border-radius: 10px 10px 0 0;
                            margin-bottom: -1px;
                        "></div>
                        """,
                        unsafe_allow_html=True
                    )

                    st.metric(
                        "Deriva",
                        f"{percentuais[3]:.2f}%"
                    )

            else:

                st.warning(
                    "Não foi possível gerar o gráfico "
                    "porque as fontes de incerteza "
                    "possuem contribuição zero."
                )

    except ValueError:

        st.error(
            "Verifique os valores informados."
        )


# ==========================
# HISTÓRICO
# ==========================

if st.session_state.historico:

    st.divider()

    st.subheader(
        "Histórico de Medições"
    )

    historico_df = pd.DataFrame(
        st.session_state.historico
    )

    st.dataframe(
        historico_df,
        use_container_width=True
    )

st.markdown("""
<hr>
<div style="text-align:center;color:#666666;font-size:14px;">
MMG • Sistema de Cálculo de Incerteza de Medição<br>
Engenharia Mecânica<br>
Versão 1.0
</div>
""", unsafe_allow_html=True)
st.sidebar.markdown("---")
