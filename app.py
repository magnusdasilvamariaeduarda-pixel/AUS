import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import sqlite3
import datetime as dt
import hashlib
import hmac
import io

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
)

st.set_page_config(
    page_title="IncertezaLab | MMG",
    page_icon="📐",
    layout="wide"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');

.stApp {
    background: #F5F7FA;
    color: #1C2B3A;
    font-family: 'DM Sans', sans-serif;
}

.block-container {
    padding-top: 1.6rem;
    max-width: 1450px;
}

h1, h2, h3 {
    font-family: 'Manrope', sans-serif !important;
    color: #17365D;
}

[data-testid="stSidebar"] {
    background: #132A43;
}

[data-testid="stSidebar"] * {
    color: #F4F7FA;
}

[data-testid="stMetric"] {
    background: white;
    border: 1px solid #E4EAF0;
    border-radius: 15px;
    padding: 18px;
    box-shadow: 0 4px 18px #17365D0A;
}

.stButton button,
.stDownloadButton button {
    border-radius: 10px;
    min-height: 2.7rem;
    font-weight: 700;
}

.stButton button[kind="primary"] {
    background: #176B70;
    color: white;
    border-color: #176B70;
}

.stTextInput input,
.stNumberInput input {
    border-radius: 9px;
}

.hero {
    background: linear-gradient(
        120deg, #17365D, #20506D 65%, #176B70
    );
    padding: 26px 30px;
    border-radius: 19px;
    color: white;
    margin-bottom: 22px;
}

.hero h1 {
    color: white !important;
    margin: 0;
}

.hero p {
    color: #DDEAF3;
    margin: .5rem 0 0;
}

.eyebrow {
    color: #A8E2DD;
    font-size: .75rem;
    text-transform: uppercase;
    letter-spacing: .12em;
    font-weight: 800;
}
</style>
""", unsafe_allow_html=True)


# BANCO DE DADOS

DB = "incertezalab.db"


def db():
    conexao = sqlite3.connect(
        DB,
        check_same_thread=False
    )
    conexao.row_factory = sqlite3.Row
    return conexao


with db() as conexao:
    conexao.execute("""
        CREATE TABLE IF NOT EXISTS med (
            id INTEGER PRIMARY KEY,
            user TEXT,
            date TEXT,
            grandeza TEXT,
            unidade TEXT,
            instrumento TEXT,
            confianca TEXT,
            n INTEGER,
            media REAL,
            ua REAL,
            ub REAL,
            uc REAL,
            k REAL,
            U REAL,
            resultado TEXT,
            valores TEXT
        )
    """)


# LOGIN

def hash_pw(senha):
    return hashlib.sha256(
        senha.encode()
    ).hexdigest()


def users():
    try:
        return dict(st.secrets["auth"]["users"])
    except Exception:
        return {}


def login_ok(usuario, senha):
    senha_salva = users().get(usuario)

    return (
        senha_salva is not None
        and hmac.compare_digest(
            str(senha_salva),
            hash_pw(senha)
        )
    )


# RELATÓRIO PDF

def pdf_bytes(r, usuario):
    arquivo = io.BytesIO()

    doc = SimpleDocTemplate(
        arquivo,
        pagesize=A4,
        rightMargin=42,
        leftMargin=42,
        topMargin=42,
        bottomMargin=42
    )

    estilos = getSampleStyleSheet()

    estilos.add(
        ParagraphStyle(
            name="TituloIncerteza",
            parent=estilos["Title"],
            textColor=colors.HexColor("#17365D"),
            alignment=TA_CENTER,
            fontSize=21
        )
    )

    dados = [
        ["Campo", "Valor"],
        ["Data", r["date"]],
        ["Usuário", usuario],
        [
            "Grandeza",
            f'{r["grandeza"]} ({r["unidade"]})'
        ],
        ["Instrumento", r["instrumento"]],
        ["Confiança", r["confianca"]],
        [
            "Número de medições",
            str(r["n"])
        ],
        ["Valores medidos", r["valores"]],
        [
            "Média",
            f'{r["media"]:.6f} {r["unidade"]}'
        ],
        [
            "Incerteza Tipo A",
            f'{r["ua"]:.6f} {r["unidade"]}'
        ],
        [
            "Incerteza Tipo B",
            f'{r["ub"]:.6f} {r["unidade"]}'
        ],
        [
            "Incerteza combinada",
            f'{r["uc"]:.6f} {r["unidade"]}'
        ],
        ["Fator k", f'{r["k"]:.3f}'],
        [
            "Incerteza expandida",
            f'{r["U"]:.6f} {r["unidade"]}'
        ],
        ["Resultado", r["resultado"]]
    ]

    tabela = Table(
        dados,
        colWidths=[155, 330],
        repeatRows=1
    )

    tabela.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0), (-1, 0),
                colors.HexColor("#17365D")
            ),
            (
                "TEXTCOLOR",
                (0, 0), (-1, 0),
                colors.white
            ),
            (
                "GRID",
                (0, 0), (-1, -1),
                .5,
                colors.HexColor("#DCE4EC")
            ),
            (
                "BACKGROUND",
                (0, 1), (0, -1),
                colors.HexColor("#F1F5F9")
            ),
            (
                "LEFTPADDING",
                (0, 0), (-1, -1), 8
            ),
            (
                "TOPPADDING",
                (0, 0), (-1, -1), 7
            ),
            (
                "BOTTOMPADDING",
                (0, 0), (-1, -1), 7
            )
        ])
    )

    elementos = [
        Paragraph(
            "IncertezaLab",
            estilos["TituloIncerteza"]
        ),
        Spacer(1, 18),
        tabela,
        Spacer(1, 20),
        Paragraph(
            "Relatório gerado pelo IncertezaLab. "
            "Confira os dados de entrada e os critérios "
            "técnicos aplicáveis antes de usar o resultado.",
            estilos["Italic"]
        )
    ]

    doc.build(elementos)

    return arquivo.getvalue()


# ESTADO DE LOGIN

if "logged" not in st.session_state:
    st.session_state.logged = False


if not st.session_state.logged:

    st.markdown(
        '<div class="hero">'
        '<div class="eyebrow">'
        'MMG • ENGENHARIA E METROLOGIA'
        '</div>'
        '<h1>IncertezaLab</h1>'
        '<p>Análise de incerteza de medição, '
        'com histórico e relatórios.</p>'
        '</div>',
        unsafe_allow_html=True
    )

    with st.container(border=True):

        st.subheader("Acessar sua conta")

        with st.form("login"):

            usuario = st.text_input("Usuário")

            senha = st.text_input(
                "Senha",
                type="password"
            )

            entrar = st.form_submit_button(
                "Entrar",
                type="primary",
                use_container_width=True
            )

        if entrar:

            if login_ok(usuario.strip(), senha):

                st.session_state.logged = True
                st.session_state.user = usuario.strip()

                st.rerun()

            else:
                st.error(
                    "Usuário ou senha incorretos. "
                    "Configure as credenciais em "
                    "Streamlit Secrets."
                )

    st.stop()


usuario = st.session_state.user


# MENU LATERAL

with st.sidebar:

    st.markdown("## 📐 IncertezaLab")
    st.caption("Automatic Uncertainty System")

    pagina = st.radio(
        "NAVEGAÇÃO",
        [
            "Painel",
            "Nova medição",
            "Histórico",
            "Relatórios"
        ],
        label_visibility="collapsed"
    )

    st.divider()
    st.caption(f"Conta: {usuario}")

    if st.button(
        "Sair da conta",
        use_container_width=True
    ):

        st.session_state.logged = False
        st.session_state.pop("user", None)

        st.rerun()


# HISTÓRICO DO USUÁRIO

def get_history():

    with db() as conexao:

        registros = conexao.execute(
            """
            SELECT * FROM med
            WHERE user = ?
            ORDER BY id DESC
            """,
            (usuario,)
        ).fetchall()

    return pd.DataFrame(
        [dict(registro) for registro in registros]
    )


hist = get_history()


# CABEÇALHO

st.markdown(
    f'<div class="hero">'
    f'<div class="eyebrow">'
    f'MMG • AUTOMATIC UNCERTAINTY SYSTEM'
    f'</div>'
    f'<h1>{pagina}</h1>'
    f'<p>Gestão de medições e análise de incerteza '
    f'em um só lugar.</p>'
    f'</div>',
    unsafe_allow_html=True
)


# PAINEL PRINCIPAL

if pagina == "Painel":

    a, b, c = st.columns(3)

    a.metric(
        "Medições salvas",
        len(hist)
    )

    b.metric(
        "Última grandeza",
        hist.iloc[0]["grandeza"]
        if len(hist)
        else "—"
    )

    c.metric(
        "Último resultado",
        hist.iloc[0]["resultado"]
        if len(hist)
        else "Sem registros"
    )

    st.subheader("Histórico das últimas medições")

    if len(hist):

        grafico = hist.head(20).copy().iloc[::-1]

        grafico["media"] = pd.to_numeric(
            grafico["media"]
        )

        fig = px.line(
            grafico,
            x="date",
            y="media",
            markers=True,
            color_discrete_sequence=["#176B70"],
            labels={
                "date": "Data",
                "media": "Média medida"
            },
            hover_data=[
                "grandeza",
                "instrumento",
                "resultado"
            ]
        )

        fig.update_layout(
            paper_bgcolor="white",
            plot_bgcolor="white",
            font_color="#17365D",
            height=360,
            margin=dict(
                l=15, r=15, t=20, b=20
            ),
            xaxis=dict(showgrid=False),
            yaxis=dict(gridcolor="#E8EDF2")
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        st.subheader("Registros recentes")

        st.dataframe(
            hist.head(5)[
                [
                    "date",
                    "grandeza",
                    "instrumento",
                    "resultado"
                ]
            ].rename(
                columns={
                    "date": "Data",
                    "grandeza": "Grandeza",
                    "instrumento": "Instrumento",
                    "resultado": "Resultado"
                }
            ),
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info(
            "Ainda não há medições. "
            "Acesse Nova medição para começar."
        )


# NOVA MEDIÇÃO

elif pagina == "Nova medição":

    with st.form("medicao"):

        a, b, c = st.columns(3)

        grandeza = a.selectbox(
            "Grandeza",
            [
                "Temperatura",
                "Pressão",
                "Comprimento",
                "Massa",
                "Tensão elétrica",
                "Outro"
            ]
        )

        unidade = b.text_input(
            "Unidade",
            placeholder="mm, °C, kg..."
        )

        confianca = c.selectbox(
            "Nível de confiança",
            ["90%", "95%", "99%"],
            index=1
        )

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

        valores_txt = st.text_input(
            "Medições separadas por vírgula",
            placeholder="10.01, 10.03, 10.02"
        )

        presets = {
            "Paquímetro": (.02, .05, .01),
            "Micrômetro": (.01, .01, .005),
            "Multímetro": (.05, .01, .02),
            "Termômetro": (.10, .10, .05),
            "Balança": (.02, .01, .01)
        }

        p0 = presets.get(
            instrumento,
            (0, 0, 0)
        )

        with st.expander(
            "Componentes da incerteza Tipo B"
        ):

            x, y, z = st.columns(3)

            certificado = x.number_input(
                "Certificado",
                min_value=0.0,
                value=float(p0[0]),
                format="%.6f"
            )

            resolucao = y.number_input(
                "Resolução",
                min_value=0.0,
                value=float(p0[1]),
                format="%.6f"
            )

            deriva = z.number_input(
                "Deriva",
                min_value=0.0,
                value=float(p0[2]),
                format="%.6f"
            )

        calcular = st.form_submit_button(
            "Calcular e salvar",
            type="primary",
            use_container_width=True
        )

    if calcular:

        try:

            valores = [
                float(v.strip())
                for v in valores_txt.split(",")
                if v.strip()
            ]

        except ValueError:

            valores = []

        if len(valores) < 2:

            st.error(
                "Informe pelo menos duas medições "
                "numéricas separadas por vírgula."
            )

        elif not unidade.strip():

            st.error("Informe a unidade de medida.")

        else:

            media = float(np.mean(valores))

            ua = float(
                np.std(valores, ddof=1)
                / np.sqrt(len(valores))
            )

            ub = float(
                np.sqrt(
                    certificado ** 2
                    + resolucao ** 2
                    + deriva ** 2
                )
            )

            uc = float(
                np.sqrt(ua ** 2 + ub ** 2)
            )

            k = {
                "90%": 1.645,
                "95%": 2.0,
                "99%": 2.576
            }[confianca]

            U = k * uc

            data = dt.datetime.now().strftime(
                "%d/%m/%Y %H:%M"
            )

            resultado = (
                f"{media:.6f} ± {U:.6f} "
                f"{unidade.strip()}"
            )

            valores_formatados = ", ".join(
                map(str, valores)
            )

            with db() as conexao:

                conexao.execute(
                    """
                    INSERT INTO med (
                        user, date, grandeza, unidade,
                        instrumento, confianca, n,
                        media, ua, ub, uc, k, U,
                        resultado, valores
                    )
                    VALUES (
                        ?, ?, ?, ?, ?, ?, ?, ?, ?,
                        ?, ?, ?, ?, ?, ?
                    )
                    """,
                    (
                        usuario,
                        data,
                        grandeza,
                        unidade.strip(),
                        instrumento,
                        confianca,
                        len(valores),
                        media,
                        ua,
                        ub,
                        uc,
                        k,
                        U,
                        resultado,
                        valores_formatados
                    )
                )

                conexao.commit()

            st.session_state.last = {
                "date": data,
                "grandeza": grandeza,
                "unidade": unidade.strip(),
                "instrumento": instrumento,
                "confianca": confianca,
                "n": len(valores),
                "media": media,
                "ua": ua,
                "ub": ub,
                "uc": uc,
                "k": k,
                "U": U,
                "resultado": resultado,
                "valores": valores_formatados
            }

            st.success(
                "Medição calculada e salva."
            )

    if "last" in st.session_state:

        registro = st.session_state.last

        st.markdown("### Resultado")

        st.metric(
            "Resultado final",
            registro["resultado"]
        )

        st.download_button(
            "Baixar relatório PDF",
            pdf_bytes(registro, usuario),
            file_name="relatorio_incertezalab.pdf",
            mime="application/pdf",
            use_container_width=True
        )


# HISTÓRICO

elif pagina == "Histórico":

    st.subheader("Medições registradas")

    if hist.empty:

        st.info("O histórico está vazio.")

    else:

        c1, c2 = st.columns(2)

        filtro_grandeza = c1.selectbox(
            "Grandeza",
            ["Todas"]
            + sorted(
                hist.grandeza.dropna().unique().tolist()
            )
        )

        filtro_instrumento = c2.selectbox(
            "Instrumento",
            ["Todos"]
            + sorted(
                hist.instrumento.dropna().unique().tolist()
            )
        )

        filtrado = hist.copy()

        if filtro_grandeza != "Todas":

            filtrado = filtrado[
                filtrado.grandeza == filtro_grandeza
            ]

        if filtro_instrumento != "Todos":

            filtrado = filtrado[
                filtrado.instrumento == filtro_instrumento
            ]

        st.dataframe(
            filtrado[
                [
                    "id",
                    "date",
                    "grandeza",
                    "instrumento",
                    "n",
                    "resultado"
                ]
            ].rename(
                columns={
                    "id": "ID",
                    "date": "Data",
                    "grandeza": "Grandeza",
                    "instrumento": "Instrumento",
                    "n": "Nº medições",
                    "resultado": "Resultado"
                }
            ),
            use_container_width=True,
            hide_index=True
        )

        st.download_button(
            "Exportar histórico CSV",
            filtrado.to_csv(
                index=False
            ).encode("utf-8-sig"),
            "historico_incertezalab.csv",
            "text/csv"
        )


# RELATÓRIOS

elif pagina == "Relatórios":

    st.subheader("Exportar medição em PDF")

    if hist.empty:

        st.info(
            "Não há medições para exportar."
        )

    else:

        opcoes = {
            (
                f'#{registro["id"]} • '
                f'{registro["date"]} • '
                f'{registro["resultado"]}'
            ): registro
            for _, registro in hist.iterrows()
        }

        escolha = st.selectbox(
            "Escolha a medição",
            list(opcoes.keys())
        )

        registro = opcoes[escolha]

        dados_pdf = {
            "date": registro["date"],
            "grandeza": registro["grandeza"],
            "unidade": registro["unidade"],
            "instrumento": registro["instrumento"],
            "confianca": registro["confianca"],
            "n": int(registro["n"]),
            "media": float(registro["media"]),
            "ua": float(registro["ua"]),
            "ub": float(registro["ub"]),
            "uc": float(registro["uc"]),
            "k": float(registro["k"]),
            "U": float(registro["U"]),
            "resultado": registro["resultado"],
            "valores": registro["valores"]
        }

        st.markdown(
            f'### {dados_pdf["resultado"]}'
        )

        st.caption(
            f'{dados_pdf["grandeza"]} • '
            f'{dados_pdf["instrumento"]} • '
            f'{dados_pdf["date"]}'
        )

        st.download_button(
            "📄 Baixar PDF",
            pdf_bytes(dados_pdf, usuario),
            file_name=(
                f'relatorio_medicao_{registro["id"]}.pdf'
            ),
            mime="application/pdf",
            type="primary",
            use_container_width=True
        )


st.markdown("---")

st.caption(
    "IncertezaLab • MMG • Engenharia Mecânica • Versão 2.0"
)
