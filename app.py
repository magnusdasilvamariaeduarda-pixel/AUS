import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import datetime
from pathlib import Path

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
.stTextArea textarea,
.stNumberInput input{
    border-radius:10px;
}

/* Destaque vermelho discreto da MMG */
[data-testid="stNumberInput"] button,
[data-testid="stSelectbox"] div[data-baseweb="select"]{
    border-color:#730000;
}

.mmg-entrada {
    background: #730000;
    color: white;
    padding: 42px 34px;
    border-radius: 12px;
    margin: 10px 0 22px 0;
}
.mmg-entrada h1 { color: white; margin-bottom: 8px; }
.mmg-entrada p { color: #f5dddd; font-size: 17px; }
.mmg-legenda { color: #730000; font-weight: 600; letter-spacing: 1px; }

</style>
""", unsafe_allow_html=True)

# ==========================
# TELA DE ENTRADA MMG
# ==========================

if "mmg_iniciada" not in st.session_state:
    st.session_state.mmg_iniciada = False

if not st.session_state.mmg_iniciada:
    logo = Path("mmg (1).png")
    if logo.exists():
        st.image(str(logo), width=230)
    else:
        st.markdown("<div class='mmg-legenda'>MMG • ENGENHARIA E METROLOGIA</div>", unsafe_allow_html=True)

    st.markdown("""
    <div class="mmg-entrada">
        <div style="font-size:13px;letter-spacing:2px;">AUTOMATIC UNCERTAINTY SYSTEM · VERSÃO 1.0</div>
        <h1>MMG</h1>
        <h3 style="color:white;">Sistema de Cálculo de Incerteza de Medição</h3>
        <p>Organize suas medições, estime as incertezas e visualize a contribuição de cada componente em um só lugar.</p>
    </div>
    """, unsafe_allow_html=True)

    st.write("Uma ferramenta de apoio à rotina de metrologia e à análise de resultados de medição.")
    if st.button("▶  INICIAR MEDIÇÃO", use_container_width=True, type="primary"):
        st.session_state.mmg_iniciada = True
        st.rerun()
    st.caption("MMG · Engenharia Mecânica · Versão 1.0")
    st.stop()

# ==========================
# SIDEBAR
# ==========================

if Path("mmg (1).png").exists():
    st.sidebar.image("mmg (1).png", width=220)
else:
    st.sidebar.markdown("# MMG")

st.sidebar.markdown("---")

st.sidebar.header("MMG")

st.sidebar.write(
    "Automatic Uncertainty System"
)

st.sidebar.markdown("---")

st.sidebar.write("Versão 1.0")

if Path("mmg (1).png").exists():
    st.image("mmg (1).png", width=500)

st.link_button(
    "📄 Manual de Uso",
    "https://github.com/magnusdasilvamariaeduarda-pixel/AUS"
)
st.markdown("""
<h2 style='color:#730000'>
Sistema Automático de Cálculo de Incerteza
</h2>
""", unsafe_allow_html=True)
st.divider()

# ==========================
# CADASTRO TÉCNICO E MEDIÇÕES
# ==========================

# Resoluções e precisões transcritas dos documentos enviados.
# Precisão do fabricante é informativa e NÃO é tratada como incerteza de calibração.
CATALOGO = {
    "Paquímetro": {
        "grandezas": {"Comprimento": {"mm": {"faixas": {"Faixa não especificada": 0.02}, "precisao": "Não informada"}}},
        "observacao": "Resolução de 0,02 mm informada pela usuária. Confirmar no instrumento físico.",
    },
    "Micrômetro": {
        "grandezas": {"Comprimento": {"mm": {"faixas": {"Resolução não cadastrada": None}, "precisao": "Não informada"}}},
        "observacao": "Informe a resolução conforme o instrumento ou manual.",
    },
    "Alicate amperímetro / Multímetro": {
        "grandezas": {
            "Tensão DC": {"mV": {"600 mV": 0.1}, "V": {"6 V": 0.001, "60 V": 0.01, "600 V": 0.1}},
            "Tensão AC": {"V": {"6 V": 0.001, "60 V": 0.01, "600 V": 0.1}},
            "Corrente DC": {"A": {"60 A": 0.01, "600 A": 0.1}},
            "Corrente AC": {"A": {"6 A (ET-3166B)": 0.001, "60 A": 0.01, "600 A": 0.1}},
            "Resistência": {"Ω": {"600 Ω": 0.1}, "kΩ": {"6 kΩ": 0.001, "60 kΩ": 0.01, "600 kΩ": 0.1}, "MΩ": {"6 MΩ": 0.001, "60 MΩ": 0.01}},
            "Capacitância": {"nF": {"10 nF": 0.001, "100 nF": 0.01, "1000 nF": 0.1}, "µF": {"10 µF": 0.001, "100 µF": 0.01, "1000 µF": 0.1}, "mF": {"10 mF": 0.001, "100 mF": 0.01}},
            "Temperatura": {"°C": {"-20 a 0 °C": 1, "0 a 400 °C": 1, "400 a 1000 °C": 1}, "°F": {"-4 a 32 °F": 1, "32 a 752 °F": 1, "752 a 1832 °F": 1}},
            "Frequência": {"Hz": {"10 Hz": 0.001, "100 Hz": 0.01, "1000 Hz": 0.1}, "kHz": {"10 kHz": 0.001, "100 kHz": 0.01, "1000 kHz": 0.1}, "MHz": {"10 MHz": 0.001}, "%": {"Ciclo de trabalho 1–99%": 0.1}},
        },
        "precisoes": {
            "Tensão DC": "±(0,5% + 5 dígitos)", "Tensão AC": "±(0,8% + 5 dígitos)",
            "Corrente DC": "±(4,0% + 5 dígitos)", "Corrente AC": "±(4,0% + 5 dígitos) para 60/600 A; ±(4,5% + 5 dígitos) na faixa 6 A ET-3166B",
            "Resistência": "±(1,0% + 5 dígitos)", "Capacitância": "±(4,0% + 5 dígitos)",
            "Temperatura": "Conforme faixa: ±3 °C; ±1,0% ou ±2 °C; ±2% (ver documento)",
            "Frequência": "±(1,0% + 3 dígitos); ciclo de trabalho ±(3,0% + 3 dígitos)",
        },
        "observacao": "Fonte: PDF de especificações enviado. A precisão varia por função/faixa e não substitui certificado de calibração.",
    },
    "Megôhmetro": {
        "grandezas": {
            "Resistência de isolamento": {"MΩ": {"0 a 200 MΩ": 0.01, "200 a 1000 MΩ": 0.01}, "GΩ": {"1000 MΩ a 20 GΩ": 0.00001}},
            "Tensão AC": {"V": {"0 a 600 V": None}},
        },
        "precisoes": {"Resistência de isolamento": "0–200 MΩ: ±(3% + 2 dígitos); 200–1000 MΩ: ±(5% + 3 dígitos); 1000 MΩ–20 GΩ: ±(10% + 5 dígitos)", "Tensão AC": "±(1,5% da leitura + 5 dígitos)"},
        "observacao": "Tensão de teste: 500/1000/2500 V. Escala de isolamento: 0–20 GΩ. Divisão mínima: 0,01 MΩ.",
    },
    "Manifold digital WK-6889": {
        "grandezas": {
            "Pressão": {"kPa": {"0 a 4000 kPa": 1}, "bar": {"0 a 40 bar": 0.01}, "psi": {"0 a 580 psi": None}},
            "Vácuo": {"kPa": {"-101 a 0 kPa": 1}},
            "Temperatura": {"°C": {"-50 a 150 °C": 0.1}, "°F": {"Faixa conforme instrumento": 0.1}},
        },
        "precisoes": {"Pressão": "±0,5%", "Vácuo": "Não informada separadamente", "Temperatura": "±0,1 °C abaixo de 50 °C"},
        "observacao": "Fonte: PDF enviado. Pressão: 0–4 MPa; vácuo: −101 a 0 kPa; temperatura: −50 a 150 °C.",
    },
    "Termômetro": {"grandezas": {"Temperatura": {"°C": {"Resolução não cadastrada": None}, "°F": {"Resolução não cadastrada": None}}}, "observacao": "Informe a resolução conforme o instrumento/manual."},
    "Balança": {"grandezas": {"Massa": {"g": {"Resolução não cadastrada": None}, "kg": {"Resolução não cadastrada": None}}}, "observacao": "Informe a resolução conforme o instrumento/manual."},
    "Outro": {"grandezas": {"Outra grandeza": {"unidade personalizada": {"Faixa não especificada": None}}}, "observacao": "Cadastre os dados com base em documentação técnica."},
}

instrumento = st.selectbox("Instrumento", list(CATALOGO.keys()), key="instrumento_mmg")
catalogo_inst = CATALOGO[instrumento]
grandezas_disp = list(catalogo_inst["grandezas"].keys())
grandeza = st.selectbox("Grandeza / função de medição", grandezas_disp, key=f"grandeza_{instrumento}")
unidades_disp = list(catalogo_inst["grandezas"][grandeza].keys())
unidade = st.selectbox("Unidade de medida", unidades_disp, key=f"unidade_{instrumento}_{grandeza}")
faixas_disp = list(catalogo_inst["grandezas"][grandeza][unidade].keys())
faixa = st.selectbox("Faixa de medição", faixas_disp, key=f"faixa_{instrumento}_{grandeza}_{unidade}")
resolucao_doc = catalogo_inst["grandezas"][grandeza][unidade][faixa]

if resolucao_doc is None:
    st.warning("A resolução desta função/faixa não está cadastrada nos documentos disponíveis. Informe uma resolução confirmada no instrumento ou manual antes de calcular.")
else:
    st.info(f"Resolução documentada para esta seleção: {resolucao_doc:g} {unidade}.")

precisao = catalogo_inst.get("precisoes", {}).get(grandeza, "Não informada")
st.caption(f"Precisão do fabricante: {precisao}. Esta especificação é informativa e não será usada como incerteza de calibração.")
st.caption(catalogo_inst.get("observacao", ""))

col_a, col_b = st.columns(2)
with col_a:
    confianca = st.selectbox("Nível de confiança", ["90%", "95%", "99%"], index=1)
with col_b:
    identificacao = st.text_input("Identificação / patrimônio do instrumento (opcional)")

st.subheader("Medições")
quantidade = st.selectbox("Quantidade de medições", options=list(range(2, 21)), index=1, help="Escolha de 2 a 20 medições para esta análise.")
medicoes = []
cols = st.columns(3)
for i in range(quantidade):
    with cols[i % 3]:
        medicoes.append(st.number_input(f"Medição {i+1} ({unidade})", value=0.0, step=0.01, format="%.9g", key=f"medicao_{i}_{instrumento}_{grandeza}_{faixa}"))

st.subheader("Componentes de incerteza Tipo B")
st.caption("Os campos de calibração e deriva começam vazios/zerados porque não há valores documentados cadastrados. Não significa que a incerteza real seja zero.")
c1, c2, c3 = st.columns(3)
with c1:
    u_certificado = st.number_input(f"Incerteza padrão de calibração ({unidade})", min_value=0.0, value=0.0, step=0.001, format="%.9g", help="Informe u do certificado. Se o certificado der incerteza expandida U e fator k, calcule u = U/k.")
with c2:
    resolucao_in = st.number_input(f"Resolução do instrumento ({unidade})", min_value=0.0, value=float(resolucao_doc or 0.0), step=0.001, format="%.9g", help="Use a resolução confirmada para a função/faixa selecionada.")
with c3:
    u_deriva = st.number_input(f"Incerteza padrão associada à deriva ({unidade})", min_value=0.0, value=0.0, step=0.001, format="%.9g", help="Somente use estimativa documentada em histórico ou procedimento técnico.")

with st.expander("ℹ️ Como o MMG trata os dados técnicos"):
    st.markdown("""
    - **Tipo A:** calculada a partir da dispersão das medições repetidas.
    - **Resolução:** convertida em incerteza padrão como resolução / √12, assumindo distribuição retangular. Confirme se essa hipótese é adequada ao método.
    - **Calibração:** só entra quando houver valor fundamentado no certificado.
    - **Deriva:** só entra quando houver estimativa documentada. Campo sem informação não significa deriva real zero.
    - **Precisão do fabricante:** exibida como referência técnica; não é confundida automaticamente com incerteza de calibração.
    """)

parcial_tab, completo_tab = st.tabs(["Resultado parcial", "Resultado completo estimado"])

def calcular(vals, ucert, resol, deriva, conf):
    media = float(np.mean(vals))
    desvio = float(np.std(vals, ddof=1))
    ua = desvio / np.sqrt(len(vals))
    ures = resol / np.sqrt(12) if resol > 0 else 0.0
    ub = float(np.sqrt(ucert**2 + ures**2 + deriva**2))
    uc = float(np.sqrt(ua**2 + ub**2))
    k = {"90%": 1.645, "95%": 2.0, "99%": 2.576}[conf]
    U = k * uc
    return {"media":media, "desvio":desvio, "ua":ua, "ures":ures, "ub":ub, "uc":uc, "k":k, "U":U}

def mostrar_resultado(modo):
    faltantes = []
    if u_certificado <= 0: faltantes.append("incerteza do certificado de calibração não informada")
    if u_deriva <= 0: faltantes.append("deriva não informada")
    if resolucao_in <= 0: faltantes.append("resolução válida não informada")
    if not any(abs(v) > 0 for v in medicoes):
        st.error("Preencha as medições. Valores todos iguais a zero são tratados como não preenchidos.")
        return
    if resolucao_in <= 0:
        st.error("Informe uma resolução positiva e confirmada para esta função/faixa antes de calcular.")
        return
    r = calcular(medicoes, u_certificado, resolucao_in, u_deriva, confianca)
    if modo == "parcial":
        st.write("Resultado calculado somente com as medições e os componentes atualmente informados.")
    else:
        st.write("Estimativa com a resolução cadastrada/confirmada e os componentes disponíveis. Não inventa valores de calibração nem de deriva.")
    st.metric("Resultado", f"{r['media']:.9g} ± {r['U']:.6g} {unidade}")
    a,b,c,d = st.columns(4)
    a.metric("Média", f"{r['media']:.9g} {unidade}")
    b.metric("Incerteza Tipo A", f"{r['ua']:.6g} {unidade}")
    c.metric("Incerteza Tipo B", f"{r['ub']:.6g} {unidade}")
    d.metric("Incerteza combinada", f"{r['uc']:.6g} {unidade}")
    st.caption(f"Incerteza expandida U = {r['U']:.6g} {unidade}; fator de abrangência k = {r['k']}; confiança selecionada: {confianca}.")
    if faltantes:
        st.warning("Estimativa preliminar. Componentes ausentes: " + "; ".join(faltantes) + ". Isso não invalida automaticamente o instrumento, mas limita a completude deste cálculo.")
    else:
        st.success("Componentes informados para este cálculo. A validade metrológica ainda depende do método e da documentação aplicável.")

    total = r['ua']**2 + u_certificado**2 + r['ures']**2 + u_deriva**2
    if total > 0:
        fontes = ["Tipo A", "Calibração", "Resolução", "Deriva"]
        percentuais = [r['ua']**2/total*100, u_certificado**2/total*100, r['ures']**2/total*100, u_deriva**2/total*100]
        import plotly.graph_objects as go
        fig = go.Figure(go.Bar(x=fontes, y=percentuais, text=[f"{x:.1f}%" for x in percentuais], textposition="auto", marker_color=["#730000", "#C62828", "#F57C00", "#1565C0"]))
        fig.update_layout(title="Contribuição percentual das fontes de incerteza", yaxis_title="Contribuição (%)", yaxis_range=[0,100], paper_bgcolor="white", plot_bgcolor="white", height=360)
        st.plotly_chart(fig, use_container_width=True)
        st.write(f"**Maior contribuição:** {fontes[int(np.argmax(percentuais))]} ({max(percentuais):.2f}%).")

    registro = {"Data": datetime.datetime.now().strftime("%d/%m/%Y %H:%M"), "Instrumento": instrumento, "Identificação": identificacao or "Não informada", "Grandeza": grandeza, "Faixa": faixa, "Unidade": unidade, "Medições": ", ".join(f"{x:g}" for x in medicoes), "Resultado": f"{r['media']:.9g} ± {r['U']:.6g} {unidade}", "Status": "Estimativa preliminar" if faltantes else "Componentes informados"}
    if st.button("Salvar no histórico", key=f"salvar_{modo}", use_container_width=True):
        st.session_state.historico.append(registro)
        st.success("Resultado salvo no histórico desta sessão.")

with parcial_tab:
    st.write("Usa os dados atualmente fornecidos, identificando os componentes que estão ausentes.")
    if st.button("Calcular resultado parcial", key="calc_parcial", type="primary", use_container_width=True):
        mostrar_resultado("parcial")
with completo_tab:
    st.write("Usa a resolução documentada para a função/faixa selecionada quando disponível. Dados de calibração e deriva continuam pendentes se não foram fornecidos.")
    if st.button("Calcular estimativa completa", key="calc_completo", type="primary", use_container_width=True):
        mostrar_resultado("completo")

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
