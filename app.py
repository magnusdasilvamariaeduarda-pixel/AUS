import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import datetime
import io
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as PDFImage
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

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
st.caption("Os campos de medição e de incerteza aceitam somente valores numéricos. Use os controles numéricos para inserir os dados; textos ficam restritos à identificação opcional do instrumento.")
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


def calcular_e_registrar(modo):
    faltantes = []
    if u_certificado <= 0:
        faltantes.append("incerteza padrão de calibração não informada")
    if u_deriva <= 0:
        faltantes.append("componente de deriva não informado")
    if resolucao_in <= 0:
        faltantes.append("resolução válida não informada")
    if len(medicoes) < 2:
        st.error("Informe pelo menos duas medições numéricas.")
        return
    if resolucao_in <= 0:
        st.error("Informe uma resolução positiva e confirmada para esta função/faixa antes de calcular.")
        return

    r = calcular(medicoes, u_certificado, resolucao_in, u_deriva, confianca)
    registro = {
        "Data": datetime.datetime.now().strftime("%d/%m/%Y %H:%M"),
        "Instrumento": instrumento,
        "Identificação": identificacao or "Não informada",
        "Grandeza": grandeza,
        "Faixa": faixa,
        "Unidade": unidade,
        "Medições": ", ".join(f"{x:g}" for x in medicoes),
        "Resultado": f"{r['media']:.2f} ± {r['U']:.6g} {unidade}",
        "Status": "Estimativa preliminar" if faltantes else "Componentes informados",
    }
    st.session_state["mmg_resultado_atual"] = {
        **r,
        "modo": modo,
        "medicoes": list(medicoes),
        "unidade": unidade,
        "instrumento": instrumento,
        "grandeza": grandeza,
        "faixa": faixa,
        "identificacao": identificacao or "Não informada",
        "confianca": confianca,
        "faltantes": faltantes,
        "registro": registro,
        "u_certificado": u_certificado,
        "u_deriva": u_deriva,
        "resolucao": resolucao_in,
    }



def gerar_pdf_analise(resultado):
    """Gera um relatório PDF com os dados e o gráfico da análise metrológica."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=18*mm, leftMargin=18*mm,
        topMargin=16*mm, bottomMargin=16*mm,
        title="Análise metrológica - MMG",
        author="MMG - Sistema de Cálculo de Incerteza de Medição",
    )
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="MMGTitle", parent=styles["Title"], textColor=colors.HexColor("#730000"), spaceAfter=8))
    styles.add(ParagraphStyle(name="MMGSection", parent=styles["Heading2"], textColor=colors.HexColor("#730000"), spaceBefore=10, spaceAfter=5))
    story = [
        Paragraph("MMG — Análise metrológica", styles["MMGTitle"]),
        Paragraph("Relatório gerado a partir dos dados registrados no sistema.", styles["Normal"]),
        Spacer(1, 8),
        Paragraph("Identificação da medição", styles["MMGSection"]),
    ]
    meta = [
        ["Data do relatório", datetime.datetime.now().strftime("%d/%m/%Y %H:%M")],
        ["Instrumento", str(resultado.get("instrumento", "Não informado"))],
        ["Identificação", str(resultado.get("identificacao", "Não informada"))],
        ["Grandeza / função", str(resultado.get("grandeza", "Não informada"))],
        ["Faixa", str(resultado.get("faixa", "Não informada"))],
        ["Unidade", str(resultado.get("unidade", ""))],
        ["Nível selecionado", str(resultado.get("confianca", "Não informado"))],
        ["Status", "Estimativa preliminar" if resultado.get("faltantes") else "Componentes informados; validar adequação ao uso"],
    ]
    table = Table(meta, colWidths=[45*mm, 115*mm], hAlign="LEFT")
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (0,-1), colors.HexColor("#F3E8E8")),
        ("TEXTCOLOR", (0,0), (0,-1), colors.HexColor("#730000")),
        ("GRID", (0,0), (-1,-1), 0.4, colors.HexColor("#D8D8D8")),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("FONTNAME", (0,0), (0,-1), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,-1), 8.5),
        ("LEFTPADDING", (0,0), (-1,-1), 6),
        ("RIGHTPADDING", (0,0), (-1,-1), 6),
        ("TOPPADDING", (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
    ]))
    story.extend([table, Spacer(1, 8), Paragraph("Resultados", styles["MMGSection"])])
    unit = resultado.get("unidade", "")
    res = [
        ["Parâmetro", "Resultado", "Unidade"],
        ["Valor médio", f"{resultado['media']:.2f}", unit],
        ["Desvio-padrão amostral", f"{resultado['desvio']:.6g}", unit],
        ["Incerteza Tipo A", f"{resultado['ua']:.6g}", unit],
        ["Incerteza Tipo B combinada", f"{resultado['ub']:.6g}", unit],
        ["Incerteza combinada", f"{resultado['uc']:.6g}", unit],
        ["Fator de abrangência (k)", f"{resultado['k']:.3f}", ""],
        ["Incerteza expandida (U)", f"± {resultado['U']:.6g}", unit],
    ]
    t2 = Table(res, colWidths=[70*mm, 50*mm, 40*mm], repeatRows=1, hAlign="LEFT")
    t2.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#730000")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("GRID", (0,0), (-1,-1), 0.4, colors.HexColor("#D8D8D8")),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#FAF6F6")]),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,-1), 8.5),
        ("ALIGN", (1,1), (-1,-1), "LEFT"),
        ("TOPPADDING", (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
    ]))
    story.extend([t2, Spacer(1, 8), Paragraph("Medições individuais", styles["MMGSection"])])
    vals = resultado.get("medicoes", [])
    readings = [["Nº da medição", "Valor", "Unidade"]] + [[str(i), f"{v:.9g}", unit] for i, v in enumerate(vals, start=1)]
    tr = Table(readings, colWidths=[45*mm, 65*mm, 50*mm], repeatRows=1, hAlign="LEFT")
    tr.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#730000")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("GRID", (0,0), (-1,-1), 0.4, colors.HexColor("#D8D8D8")),
        ("FONTSIZE", (0,0), (-1,-1), 8.5),
        ("TOPPADDING", (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
    ]))
    story.extend([tr, Spacer(1, 10), Paragraph("Gráfico de variação e incerteza expandida", styles["MMGSection"])])

    # Cria o gráfico no PDF com os mesmos dados do cálculo.
    fig, ax = plt.subplots(figsize=(8.0, 3.3))
    x = list(range(1, len(vals) + 1))
    media, U = resultado["media"], resultado["U"]
    ax.axhspan(media-U, media+U, color="#F2B134", alpha=0.25, label="Faixa x̄ ± U")
    ax.axhline(media, color="#730000", linewidth=1.8, linestyle="--", label=f"Média = {media:.6g} {unit}")
    ax.plot(x, vals, color="#176B70", marker="o", linewidth=1.8, label="Medições")
    ax.set_xlabel("Ordem da medição")
    ax.set_ylabel(f"Valor medido ({unit})")
    ax.set_xticks(x)
    ax.grid(True, alpha=0.2)
    ax.legend(loc="best", fontsize=8)
    fig.tight_layout()
    img_buf = io.BytesIO()
    fig.savefig(img_buf, format="png", dpi=160, bbox_inches="tight")
    plt.close(fig)
    img_buf.seek(0)
    story.append(PDFImage(img_buf, width=165*mm, height=68*mm))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "A faixa colorida representa a média ± incerteza expandida. Os pontos correspondem às leituras informadas. "
        "O nível de confiança e o fator k devem ser interpretados conforme o método de avaliação adotado.",
        styles["BodyText"]
    ))
    if resultado.get("faltantes"):
        story.extend([Spacer(1, 8), Paragraph("Atenção: análise preliminar", styles["MMGSection"]),
                      Paragraph("Componentes não informados: " + "; ".join(resultado["faltantes"]) + ". A ausência de informação não significa que o componente real seja zero.", styles["BodyText"])])
    story.extend([Spacer(1, 8), Paragraph("Relatório de apoio à análise metrológica. Verifique a adequação do método, dos dados e dos critérios aplicáveis antes de usar o resultado para decisões de conformidade.", styles["Italic"])])
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


def mostrar_resultado_principal(resultado):
    if resultado.get("faltantes"):
        st.warning("Estimativa preliminar. Componentes ausentes: " + "; ".join(resultado["faltantes"]) + ". Isso não invalida automaticamente o instrumento, mas limita a completude deste cálculo.")
    else:
        st.success("Componentes informados para este cálculo. A validade metrológica ainda depende do método e da documentação aplicável.")
    c1, c2 = st.columns(2)
    c1.metric("Valor médio", f"{resultado['media']:.2f} {resultado['unidade']}")
    c2.metric("Incerteza expandida", f"± {resultado['U']:.6g} {resultado['unidade']}")
    st.caption("A média é exibida com duas casas decimais. A incerteza mantém precisão adicional para evitar ocultar informação relevante.")
    if st.button("Salvar no histórico", key=f"salvar_{resultado['modo']}", use_container_width=True):
        st.session_state.historico.append(resultado["registro"])
        st.success("Resultado salvo no histórico desta sessão.")


st.markdown("### Resultados da medição")
resultado_tab, analise_tab = st.tabs(["Resultado principal", "Análise metrológica"])
with resultado_tab:
    parcial_tab, completo_tab = st.tabs(["Resultado parcial", "Resultado completo estimado"])
    with parcial_tab:
        st.write("Calcula com os dados fornecidos e identifica os componentes que ainda não foram informados.")
        if st.button("Calcular resultado parcial", key="calc_parcial", type="primary", use_container_width=True):
            calcular_e_registrar("parcial")
        resultado = st.session_state.get("mmg_resultado_atual")
        if resultado and resultado.get("modo") == "parcial":
            mostrar_resultado_principal(resultado)
    with completo_tab:
        st.write("Usa a resolução documentada para a função/faixa selecionada, quando disponível. Valores de calibração e deriva não são inventados.")
        if st.button("Calcular estimativa completa", key="calc_completo", type="primary", use_container_width=True):
            calcular_e_registrar("completo")
        resultado = st.session_state.get("mmg_resultado_atual")
        if resultado and resultado.get("modo") == "completo":
            mostrar_resultado_principal(resultado)

with analise_tab:
    resultado = st.session_state.get("mmg_resultado_atual")
    if not resultado:
        st.info("Calcule primeiro um resultado parcial ou uma estimativa completa. Os detalhes e o gráfico aparecerão aqui.")
    else:
        st.caption(f"{resultado['instrumento']} · {resultado['grandeza']} · Faixa: {resultado['faixa']} · Unidade: {resultado['unidade']}")
        st.subheader("Componentes de incerteza")
        a, b, c = st.columns(3)
        a.metric("Incerteza Tipo A", f"{resultado['ua']:.6g} {resultado['unidade']}")
        b.metric("Incerteza Tipo B", f"{resultado['ub']:.6g} {resultado['unidade']}")
        c.metric("Incerteza combinada", f"{resultado['uc']:.6g} {resultado['unidade']}")
        st.caption(f"Incerteza expandida U = {resultado['U']:.6g} {resultado['unidade']} · k = {resultado['k']:.3f} · nível selecionado: {resultado['confianca']}.")
        st.markdown("#### Gráfico de variação das medições e incerteza expandida")
        import plotly.graph_objects as go
        leituras = resultado["medicoes"]
        media = resultado["media"]
        U = resultado["U"]
        fig = go.Figure()
        fig.add_hrect(y0=media-U, y1=media+U, fillcolor="#F2B134", opacity=0.22,
                      line_width=0, annotation_text="Faixa x̄ ± U", annotation_position="top left")
        fig.add_hline(y=media, line_color="#730000", line_width=2,
                      annotation_text=f"Média = {media:.6g} {resultado['unidade']}", annotation_position="bottom right")
        fig.add_trace(go.Scatter(
            x=list(range(1, len(leituras)+1)), y=leituras, mode="lines+markers",
            name="Medições", line=dict(color="#176B70", width=2),
            marker=dict(size=9),
            hovertemplate="Medição %{x}: %{y:.9g} " + resultado["unidade"] + "<extra></extra>"
        ))
        fig.update_layout(
            height=430, paper_bgcolor="white", plot_bgcolor="white",
            font_color="#222222", margin=dict(l=20, r=20, t=55, b=25),
            xaxis_title="Ordem da medição", yaxis_title=f"Valor medido ({resultado['unidade']})",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            yaxis=dict(gridcolor="#E8EDF2"), xaxis=dict(dtick=1, gridcolor="#F2F2F2")
        )
        st.plotly_chart(fig, use_container_width=True)
        st.caption("A faixa colorida representa média ± incerteza expandida. Os pontos mostram as leituras reais; a linha entre eles apenas indica a ordem de aquisição, não uma onda contínua.")
        st.markdown("#### Dados usados no cálculo")
        detalhes = pd.DataFrame({"Componente": ["Tipo A (incerteza-padrão da média)", "Calibração", "Resolução (u = resolução/√12)", "Deriva", "Tipo B combinado", "Incerteza combinada", "Incerteza expandida"],
                                 "Valor": [resultado["ua"], resultado["u_certificado"], resultado["ures"], resultado["u_deriva"], resultado["ub"], resultado["uc"], resultado["U"]],
                                 "Unidade": [resultado["unidade"]]*7})
        st.dataframe(detalhes, use_container_width=True, hide_index=True)
        if resultado.get("faltantes"):
            st.warning("Esta análise é preliminar. Dados ausentes: " + "; ".join(resultado["faltantes"]) + ". Consulte a documentação aplicável antes de usar o resultado para decisões de conformidade.")

        st.download_button(
            label="📄 Baixar análise metrológica em PDF",
            data=gerar_pdf_analise(resultado),
            file_name=f"analise_metrologica_MMG_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            mime="application/pdf",
            type="primary",
            use_container_width=True,
            help="Exporta resultados, componentes de incerteza, medições e gráfico para PDF."
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

