import streamlit as st
import numpy as np
import pandas as pd
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
    background-color:#61000D;
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
.mmg-legenda { color: #730000; font-weight: 700; letter-spacing: 1px; }
.mmg-brand { display:flex; align-items:center; gap:14px; font-size:44px; font-weight:800; line-height:1.1; }
.mmg-brand .gear { font-size:48px; }
.mmg-subbrand { font-size:15px; letter-spacing:.4px; margin-left:4px; color:#f5dddd; }
.mmg-hero-title { font-size:22px; font-weight:700; margin-top:14px; }
.mmg-topbar { background:#61000D; color:white; padding:14px 20px; border-radius:10px; margin-bottom:18px; }

</style>
""", unsafe_allow_html=True)

# ==========================
# TELA DE ENTRADA MMG
# ==========================

if "mmg_iniciada" not in st.session_state:
    st.session_state.mmg_iniciada = False

if not st.session_state.mmg_iniciada:
    st.markdown("""
    <div class="mmg-entrada">
        <div class="mmg-brand"><span class="gear">⚙</span><span>MMG</span></div>
        <div class="mmg-subbrand">Medição - Metrologia - Gestão</div>
        <div class="mmg-hero-title">Sistema de análise de incerteza de medição</div>
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

st.sidebar.markdown("## ⚙ MMG")
st.sidebar.caption("Medição - Metrologia - Gestão")
st.sidebar.markdown("Sistema de análise de incerteza de medição")
st.sidebar.markdown("---")
st.sidebar.markdown("**NAVEGAÇÃO**")
st.sidebar.caption("Entrada de dados · Resultados · Histórico")

st.sidebar.markdown("---")

st.sidebar.write("Versão 1.0")

st.link_button(
    "📄 Repositório e documentação do MMG",
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
    "Outro": {
        "grandezas": {},
        "precisoes": {},
        "observacao": "Instrumento personalizado. Informe grandeza, unidade, faixa e resolução com base na identificação e na documentação técnica do instrumento.",
    },
}


def formatar_decimal(valor, casas=6):
    """Formata número com vírgula decimal para a interface em português."""
    return f"{valor:.{casas}f}".replace(".", ",")

def formatar_significativo(valor, algarismos=6):
    """Formata número com algarismos significativos e vírgula decimal."""
    return f"{valor:.{algarismos}g}".replace(".", ",")

def calcular(vals, ucert, resol, deriva, conf):
    media = float(np.mean(vals))
    desvio = float(np.std(vals, ddof=1))
    ua = float(desvio / np.sqrt(len(vals)))
    # Um componente só contribui numericamente quando há valor informado.
    # A ausência é registrada separadamente e não deve ser interpretada como zero real.
    ures = float(resol / np.sqrt(12)) if resol > 0 else 0.0
    ub = float(np.sqrt(ucert**2 + ures**2 + deriva**2))
    uc = float(np.sqrt(ua**2 + ub**2))
    # Fatores de referência aproximados. A validade do k deve ser verificada para o método usado.
    k = {"90%": 1.645, "95%": 2.0, "99%": 2.576}[conf]
    U = float(k * uc)
    return {
        "media": media, "desvio": desvio, "ua": ua, "ures": ures,
        "ub": ub, "uc": uc, "k": k, "U": U,
        "limite_inferior": media - U,
        "limite_superior": media + U,
    }


def criar_chave_entrada():
    """Identifica os dados usados para evitar mostrar resultado antigo após editar campos."""
    return (
        instrumento, grandeza, unidade, faixa, tuple(float(x) for x in medicoes),
        float(u_certificado), float(resolucao_in), origem_resolucao,
        float(u_deriva), confianca
    )




def restaurar_campos_para_edicao(resultado):
    """Restaura as entradas anteriores ao voltar da tela de resultados."""
    instrumento_salvo = resultado["instrumento"]
    grandeza_salva = resultado["grandeza"]
    unidade_salva = resultado["unidade"]
    faixa_salva = resultado["faixa"]

    st.session_state["instrumento_mmg"] = instrumento_salvo
    if instrumento_salvo == "Outro":
        st.session_state["grandeza_outro"] = grandeza_salva
        st.session_state["unidade_outro"] = unidade_salva
        st.session_state["faixa_outro"] = faixa_salva
    else:
        st.session_state[f"grandeza_{instrumento_salvo}"] = grandeza_salva
        st.session_state[f"unidade_{instrumento_salvo}_{grandeza_salva}"] = unidade_salva
        st.session_state[f"faixa_{instrumento_salvo}_{grandeza_salva}_{unidade_salva}"] = faixa_salva

    st.session_state["confianca_mmg"] = resultado["confianca"]
    st.session_state["quantidade_medicoes_mmg"] = len(resultado["medicoes"])

    chave_base = f"{instrumento_salvo}_{grandeza_salva}_{unidade_salva}_{faixa_salva}"
    for i, valor in enumerate(resultado["medicoes"]):
        st.session_state[f"medicao_{i}_{instrumento_salvo}_{grandeza_salva}_{unidade_salva}_{faixa_salva}"] = float(valor)

    st.session_state[f"u_certificado_{chave_base}"] = float(resultado["u_certificado"])
    st.session_state[f"u_deriva_{chave_base}"] = float(resultado["u_deriva"])
    usar_catalogo = resultado.get("origem_resolucao") == "Catálogo técnico"
    st.session_state[f"usar_res_doc_{chave_base}"] = usar_catalogo
    st.session_state[f"resolucao_manual_{chave_base}"] = 0.0 if usar_catalogo else float(resultado["resolucao"])


def calcular_e_registrar(modo):
    faltantes = []
    if instrumento == "Outro" and not (grandeza.strip() and unidade.strip() and faixa.strip()):
        st.error("Para usar 'Outro', preencha a grandeza, a unidade e a faixa de medição.")
        return
    if len(medicoes) < 2:
        st.error("Informe pelo menos duas medições numéricas.")
        return

    if u_certificado <= 0:
        faltantes.append("incerteza padrão de calibração não informada")
    if u_deriva <= 0:
        faltantes.append("incerteza associada à deriva não informada")
    if resolucao_in <= 0:
        faltantes.append("resolução não informada ou não confirmada")

    # O parcial pode ser calculado com os componentes disponíveis, mas sinaliza as lacunas.
    # A estimativa completa exige ao menos uma resolução positiva documentada ou confirmada.
    if modo == "completo" and resolucao_in <= 0:
        st.error(
            "Para calcular a estimativa completa, informe uma resolução positiva confirmada "
            "ou selecione uma resolução documentada disponível no catálogo. "
            "O resultado parcial continua disponível com as limitações identificadas."
        )
        return

    r = calcular(medicoes, u_certificado, resolucao_in, u_deriva, confianca)
    registro = {
        "Data": datetime.datetime.now().strftime("%d/%m/%Y %H:%M"),
        "Instrumento": instrumento,
        "Grandeza": grandeza,
        "Faixa": faixa,
        "Unidade": unidade,
        "Medições": ", ".join(f"{x:g}" for x in medicoes),
        "Resultado": f"{formatar_decimal(r['media'], 2)} ± {formatar_significativo(r['U'])} {unidade}",
        "Status": "Estimativa preliminar" if faltantes else "Componentes informados; validar método",
    }
    st.session_state["mmg_resultado_atual"] = {
        **r,
        "modo": modo,
        "medicoes": list(medicoes),
        "unidade": unidade,
        "instrumento": instrumento,
        "grandeza": grandeza,
        "faixa": faixa,
        "confianca": confianca,
        "faltantes": faltantes,
        "registro": registro,
        "u_certificado": float(u_certificado),
        "u_deriva": float(u_deriva),
        "resolucao": float(resolucao_in),
        "origem_resolucao": origem_resolucao,
        "chave_entrada": chave_entrada_atual,
        "observacao_k": "Fator k de referência aproximado; validar graus de liberdade efetivos e método aplicável.",
    }
    # Gera o PDF uma vez por cálculo, evitando recriá-lo a cada rerun da tela de resultados.
    st.session_state["mmg_pdf_atual"] = gerar_pdf_analise(st.session_state["mmg_resultado_atual"])
    st.session_state["mmg_pagina"] = "resultados"
    st.rerun()



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
        Paragraph("Dados da medição", styles["MMGSection"]),
    ]
    meta = [
        ["Data do relatório", datetime.datetime.now().strftime("%d/%m/%Y %H:%M")],
        ["Instrumento", str(resultado.get("instrumento", "Não informado"))],
        ["Grandeza / função", str(resultado.get("grandeza", "Não informada"))],
        ["Faixa", str(resultado.get("faixa", "Não informada"))],
        ["Unidade", str(resultado.get("unidade", ""))],
        ["Nível selecionado", str(resultado.get("confianca", "Não informado"))],
        ["Status", "Estimativa preliminar" if resultado.get("faltantes") else "Componentes informados; validar adequação ao uso"],
        ["Modo de cálculo", "Resultado parcial" if resultado.get("modo") == "parcial" else "Resultado completo estimado"],
        ["Origem da resolução", str(resultado.get("origem_resolucao", "Não informada"))],
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
        ["Limite inferior (média − U)", f"{resultado['limite_inferior']:.9g}", unit],
        ["Limite superior (média + U)", f"{resultado['limite_superior']:.9g}", unit],
        ["Resolução considerada", f"{resultado['resolucao']:.9g}", unit],
        ["Incerteza padrão de calibração informada", f"{resultado['u_certificado']:.9g}", unit],
        ["Incerteza padrão de deriva informada", f"{resultado['u_deriva']:.9g}", unit],
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
    limite_inferior = resultado["limite_inferior"]
    limite_superior = resultado["limite_superior"]
    ax.axhspan(limite_inferior, limite_superior, color="#F2B134", alpha=0.25, label="Faixa média ± U")
    ax.axhline(media, color="#730000", linewidth=1.8, linestyle="--", label=f"Média = {media:.6g} {unit}")
    ax.axhline(limite_inferior, color="#94601D", linewidth=1.0, linestyle=":", label=f"Limite inferior = {limite_inferior:.6g} {unit}")
    ax.axhline(limite_superior, color="#94601D", linewidth=1.0, linestyle=":", label=f"Limite superior = {limite_superior:.6g} {unit}")
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
        f"Limite inferior: {limite_inferior:.9g} {unit}; limite superior: {limite_superior:.9g} {unit}. "
        "Os fatores k são valores de referência aproximados; valide os graus de liberdade e o método aplicável.",
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
        st.warning(
            "Estimativa preliminar. Componentes ausentes: "
            + "; ".join(resultado["faltantes"])
            + ". Isso limita a completude deste cálculo e não significa que os componentes reais sejam zero."
        )
    else:
        st.success(
            "Componentes informados para este cálculo. A validade metrológica ainda depende do método e da documentação aplicável."
        )

    c1, c2 = st.columns(2)
    c1.metric("Valor médio", f"{formatar_decimal(resultado['media'], 2)} {resultado['unidade']}")
    c2.metric("Incerteza expandida", f"± {formatar_significativo(resultado['U'])} {resultado['unidade']}")
    st.caption(
        "A média é exibida com duas casas decimais. A incerteza mantém algarismos significativos adicionais. "
        "A adequação do arredondamento final depende do procedimento metrológico adotado."
    )
    st.caption(
        f"Intervalo associado: {formatar_significativo(resultado['limite_inferior'])} a "
        f"{formatar_significativo(resultado['limite_superior'])} {resultado['unidade']}."
    )
    st.caption(
        f"Modo: {'Resultado parcial' if resultado['modo'] == 'parcial' else 'Resultado completo estimado'} · "
        f"Confiança selecionada: {resultado['confianca']} · k = {resultado['k']:.3f} (aproximado)."
    )

    pdf_atual = st.session_state.get("mmg_pdf_atual")
    if pdf_atual is None:
        pdf_atual = gerar_pdf_analise(resultado)
        st.session_state["mmg_pdf_atual"] = pdf_atual

    pdf_col, save_col = st.columns(2)
    with pdf_col:
        st.download_button(
            label="📄 Baixar relatório em PDF",
            data=pdf_atual,
            file_name=f"relatorio_MMG_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            mime="application/pdf",
            type="primary",
            use_container_width=True,
            key=f"baixar_pdf_{resultado['modo']}",
            help="Baixa o relatório com resultados, dados de entrada, componentes de incerteza e gráfico."
        )
    with save_col:
        if st.button("Salvar no histórico", key=f"salvar_{resultado['modo']}", use_container_width=True):
            st.session_state.historico.append(resultado["registro"])
            st.success("Resultado salvo no histórico desta sessão.")


# ==========================
# NAVEGAÇÃO ENTRE ENTRADA E RESULTADOS
# ==========================

if "mmg_pagina" not in st.session_state:
    st.session_state["mmg_pagina"] = "entrada"

if st.session_state["mmg_pagina"] == "entrada":
    if st.session_state.get("mmg_restaurar_entrada"):
        resultado_salvo = st.session_state.get("mmg_resultado_atual")
        if resultado_salvo:
            restaurar_campos_para_edicao(resultado_salvo)
        st.session_state["mmg_restaurar_entrada"] = False
    st.markdown("### Entrada de dados")
    st.caption("Preencha o instrumento, as medições e os componentes de incerteza. Depois, escolha o tipo de resultado.")
    instrumento = st.selectbox("Instrumento", list(CATALOGO.keys()), key="instrumento_mmg")
    catalogo_inst = CATALOGO[instrumento]
    if instrumento == "Outro":
        grandeza = st.text_input("Grandeza / função de medição", placeholder="Ex.: força, vazão, torque", key="grandeza_outro")
        unidade = st.text_input("Unidade de medida", placeholder="Ex.: N, L/min, N·m", key="unidade_outro")
        faixa = st.text_input("Faixa de medição", placeholder="Ex.: 0 a 100 N", key="faixa_outro")
        resolucao_doc = None
    else:
        grandezas_disp = list(catalogo_inst["grandezas"].keys())
        grandeza = st.selectbox("Grandeza / função de medição", grandezas_disp, key=f"grandeza_{instrumento}")
        unidades_disp = list(catalogo_inst["grandezas"][grandeza].keys())
        unidade = st.selectbox("Unidade de medida", unidades_disp, key=f"unidade_{instrumento}_{grandeza}")
        faixas_disp = list(catalogo_inst["grandezas"][grandeza][unidade].keys())
        faixa = st.selectbox("Faixa de medição", faixas_disp, key=f"faixa_{instrumento}_{grandeza}_{unidade}")
        resolucao_doc = catalogo_inst["grandezas"][grandeza][unidade][faixa]

    precisao = catalogo_inst.get("precisoes", {}).get(grandeza, "Não informada")
    st.caption(f"Precisão do fabricante: {precisao}. Esta especificação é informativa e não será usada como incerteza de calibração.")
    st.caption(catalogo_inst.get("observacao", ""))

    if "confianca_mmg" not in st.session_state:
        st.session_state["confianca_mmg"] = "95%"
    confianca = st.selectbox("Nível de confiança", ["90%", "95%", "99%"], key="confianca_mmg")

    st.subheader("Medições")
    st.caption("Os campos de medição e de incerteza aceitam valores numéricos. Selecione o instrumento, a grandeza e a faixa antes de inserir as leituras.")
    if "quantidade_medicoes_mmg" not in st.session_state:
        st.session_state["quantidade_medicoes_mmg"] = 3
    quantidade = st.selectbox("Quantidade de medições", options=list(range(2, 21)), key="quantidade_medicoes_mmg", help="Escolha de 2 a 20 medições para esta análise.")
    medicoes = []
    cols = st.columns(3)
    for i in range(quantidade):
        with cols[i % 3]:
            medicoes.append(st.number_input(f"Medição {i+1} ({unidade})", step=0.01, format="%.9g", key=f"medicao_{i}_{instrumento}_{grandeza}_{unidade}_{faixa}"))

    st.subheader("Componentes de incerteza Tipo B")
    st.caption("Os campos de calibração e deriva começam vazios/zerados porque não há valores documentados cadastrados. Não significa que a incerteza real seja zero.")
    c1, c2, c3 = st.columns(3)
    with c1:
        u_certificado = st.number_input(
            f"Incerteza padrão de calibração ({unidade})",
            min_value=0.0, step=0.001, format="%.9g",
            key=f"u_certificado_{instrumento}_{grandeza}_{unidade}_{faixa}",
            help="Informe u do certificado. Se o certificado fornecer incerteza expandida U e fator k, calcule u = U/k. Zero indica que o valor não foi informado."
        )
    with c2:
        resolucao_catalogo_valida = (
            isinstance(resolucao_doc, (int, float))
            and not isinstance(resolucao_doc, bool)
            and resolucao_doc > 0
        )
        chave_resolucao_catalogo = f"usar_res_doc_{instrumento}_{grandeza}_{unidade}_{faixa}"
        if chave_resolucao_catalogo not in st.session_state:
            st.session_state[chave_resolucao_catalogo] = resolucao_catalogo_valida
        usar_resolucao_catalogo = st.checkbox(
            "Usar resolução documentada no catálogo",
            key=chave_resolucao_catalogo,
            disabled=not resolucao_catalogo_valida,
            help="Use esta opção somente quando a resolução cadastrada estiver confirmada para o instrumento e a faixa selecionados."
        )
        if usar_resolucao_catalogo and resolucao_catalogo_valida:
            resolucao_in = float(resolucao_doc)
            st.info(f"Resolução de referência: {resolucao_in:g} {unidade}")
            origem_resolucao = "Catálogo técnico"
        else:
            resolucao_in = st.number_input(
                f"Resolução confirmada/manual ({unidade})",
                min_value=0.0, step=0.001, format="%.9g",
                key=f"resolucao_manual_{instrumento}_{grandeza}_{unidade}_{faixa}",
                help="Informe uma resolução positiva e confirmada. Deixe em zero quando ainda não souber o valor."
            )
            origem_resolucao = "Informada pelo usuário" if resolucao_in > 0 else "Não informada"
    with c3:
        u_deriva = st.number_input(
            f"Incerteza padrão associada à deriva ({unidade})",
            min_value=0.0, step=0.001, format="%.9g",
            key=f"u_deriva_{instrumento}_{grandeza}_{unidade}_{faixa}",
            help="Use somente uma estimativa documentada em histórico ou procedimento técnico. Zero indica que o valor não foi informado."
        )

    with st.expander("ℹ️ Como o MMG trata os dados técnicos"):
        st.markdown("""
        - **Tipo A:** calculada a partir da dispersão das medições repetidas.
        - **Resolução:** convertida em incerteza padrão como resolução / √12, assumindo distribuição retangular. Confirme se essa hipótese é adequada ao método.
        - **Calibração:** só entra quando houver valor fundamentado no certificado.
        - **Deriva:** só entra quando houver estimativa documentada. Campo sem informação não significa deriva real zero.
        - **Combinação:** os componentes são combinados quadraticamente assumindo ausência de correlação entre eles; se houver correlação, o método precisa ser ajustado.
        - **Precisão do fabricante:** exibida como referência técnica; não é confundida automaticamente com incerteza de calibração.
        - **Fator k:** o sistema usa valores de referência aproximados para 90%, 95% e 99%. Eles não substituem a avaliação dos graus de liberdade efetivos exigida pelo método metrológico aplicável.
        - **Resultado parcial:** permite calcular com os componentes disponíveis e identifica os que faltam; componente ausente não é considerado conhecido como zero.
        - **Resultado completo estimado:** exige resolução positiva documentada ou confirmada, mas continua preliminar quando faltarem outros componentes relevantes.
        """)

    chave_entrada_atual = criar_chave_entrada()

    st.divider()
    st.subheader("Calcular e visualizar resultados")
    st.write("Após o cálculo, o MMG abre a tela de resultados. O relatório em PDF fica disponível nessa tela.")
    botao_parcial, botao_completo = st.columns(2)
    with botao_parcial:
        if st.button("Calcular resultado parcial", key="calc_parcial", type="primary", use_container_width=True):
            calcular_e_registrar("parcial")
    with botao_completo:
        if st.button("Calcular resultado completo estimado", key="calc_completo", type="primary", use_container_width=True):
            calcular_e_registrar("completo")

else:
    st.markdown("""
    <div class="mmg-topbar">
      <div style="font-size:30px;font-weight:800;">⚙ MMG</div>
      <div style="font-size:12px;opacity:.95;">Medição - Metrologia - Gestão</div>
      <div style="font-size:19px;font-weight:650;margin-top:9px;">Sistema de análise de incerteza de medição</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("### Resultados da medição")
    topo_voltar, topo_info = st.columns([1, 2])
    with topo_voltar:
        if st.button("← Voltar aos dados", key="voltar_entrada", use_container_width=True):
            st.session_state["mmg_restaurar_entrada"] = True
            st.session_state["mmg_pagina"] = "entrada"
            st.rerun()
    with topo_info:
        st.caption("Os resultados abaixo correspondem aos dados utilizados no cálculo. Volte aos dados para editar ou iniciar outra análise.")

    resultado = st.session_state.get("mmg_resultado_atual")
    if not resultado:
        st.info("Ainda não há resultado calculado. Volte à entrada de dados e realize um cálculo.")
    else:
        resultado_tab, analise_tab = st.tabs(["Resultado principal", "Análise metrológica"])
        with resultado_tab:
            st.caption(
                f"{resultado['instrumento']} · {resultado['grandeza']} · "
                f"Faixa: {resultado['faixa']} · Unidade: {resultado['unidade']}"
            )
            mostrar_resultado_principal(resultado)

        with analise_tab:
            st.caption(
                f"{resultado['instrumento']} · {resultado['grandeza']} · "
                f"Faixa: {resultado['faixa']} · Unidade: {resultado['unidade']}"
            )
            st.subheader("Componentes de incerteza")
            a, b, c = st.columns(3)
            a.metric("Incerteza Tipo A", f"{resultado['ua']:.6g} {resultado['unidade']}")
            b.metric("Incerteza Tipo B", f"{resultado['ub']:.6g} {resultado['unidade']}")
            c.metric("Incerteza combinada", f"{resultado['uc']:.6g} {resultado['unidade']}")
            st.caption(
                f"Incerteza expandida U = {resultado['U']:.6g} {resultado['unidade']} · "
                f"k = {resultado['k']:.3f} · nível selecionado: {resultado['confianca']}."
            )
            st.markdown("#### Gráfico de variação das medições e incerteza expandida")
            import plotly.graph_objects as go
            leituras = resultado["medicoes"]
            media = resultado["media"]
            limite_inferior = resultado["limite_inferior"]
            limite_superior = resultado["limite_superior"]
            unidade_grafico = resultado["unidade"]
            fig = go.Figure()
            fig.add_hrect(
                y0=limite_inferior, y1=limite_superior,
                fillcolor="#F2B134", opacity=0.22, line_width=0,
                annotation_text="Faixa média ± U", annotation_position="top left"
            )
            fig.add_hline(
                y=media, line_color="#730000", line_width=2,
                annotation_text=f"Média = {formatar_significativo(media)} {unidade_grafico}",
                annotation_position="bottom right"
            )
            fig.add_hline(
                y=limite_inferior, line_color="#94601D", line_dash="dot", line_width=1,
                annotation_text=f"Limite inferior = {formatar_significativo(limite_inferior)} {unidade_grafico}",
                annotation_position="bottom left"
            )
            fig.add_hline(
                y=limite_superior, line_color="#94601D", line_dash="dot", line_width=1,
                annotation_text=f"Limite superior = {formatar_significativo(limite_superior)} {unidade_grafico}",
                annotation_position="top right"
            )
            fig.add_trace(go.Scatter(
                x=list(range(1, len(leituras) + 1)), y=leituras,
                mode="lines+markers", name="Medições",
                line=dict(color="#176B70", width=2), marker=dict(size=9),
                hovertemplate="Medição %{x}: %{y:.9g} " + unidade_grafico + "<extra></extra>"
            ))
            fig.update_layout(
                height=430, paper_bgcolor="white", plot_bgcolor="white",
                font_color="#222222", margin=dict(l=20, r=20, t=70, b=25),
                xaxis_title="Ordem da medição", yaxis_title=f"Valor medido ({unidade_grafico})",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                yaxis=dict(gridcolor="#E8EDF2"), xaxis=dict(dtick=1, gridcolor="#F2F2F2")
            )
            st.plotly_chart(fig, use_container_width=True)
            st.caption(
                f"Faixa colorida: média ± U. Limite inferior = {formatar_significativo(limite_inferior)} {unidade_grafico}; "
                f"limite superior = {formatar_significativo(limite_superior)} {unidade_grafico}. "
                "Os pontos representam as leituras; a linha entre eles indica a ordem de aquisição."
            )
            st.markdown("#### Dados usados no cálculo")
            detalhes = pd.DataFrame({
                "Componente": [
                    "Tipo A (incerteza-padrão da média)", "Calibração (incerteza padrão informada)",
                    "Resolução considerada", "Incerteza padrão de resolução (resolução/√12)",
                    "Deriva (incerteza padrão informada)", "Tipo B combinado", "Incerteza combinada",
                    "Fator de abrangência k (aproximado)", "Incerteza expandida", "Limite inferior (média − U)",
                    "Limite superior (média + U)"
                ],
                "Valor": [
                    resultado["ua"], resultado["u_certificado"], resultado["resolucao"], resultado["ures"],
                    resultado["u_deriva"], resultado["ub"], resultado["uc"], resultado["k"], resultado["U"],
                    resultado["limite_inferior"], resultado["limite_superior"]
                ],
                "Unidade": [resultado["unidade"]] * 7 + ["", resultado["unidade"], resultado["unidade"], resultado["unidade"]]
            })
            st.caption(f"Origem da resolução: {resultado.get('origem_resolucao', 'Não informada')}.")
            st.dataframe(detalhes, use_container_width=True, hide_index=True)
            if resultado.get("faltantes"):
                st.warning(
                    "Esta análise é preliminar. Dados ausentes: " + "; ".join(resultado["faltantes"])
                    + ". Consulte a documentação aplicável antes de usar o resultado para decisões de conformidade."
                )
            pdf_analise = st.session_state.get("mmg_pdf_atual")
            if pdf_analise is None:
                pdf_analise = gerar_pdf_analise(resultado)
                st.session_state["mmg_pdf_atual"] = pdf_analise
            st.download_button(
                label="📄 Baixar relatório completo em PDF",
                data=pdf_analise,
                file_name=f"relatorio_MMG_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                mime="application/pdf",
                type="primary",
                use_container_width=True,
                key=f"baixar_pdf_analise_{resultado['modo']}",
                help="Relatório com os resultados, componentes de incerteza, leituras e gráfico."
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
