import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import sqlite3, datetime as dt, hashlib, hmac, io
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

st.set_page_config(page_title="IncertezaLab | MMG", page_icon="📐", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
.stApp{background:#F5F7FA;color:#1C2B3A;font-family:'DM Sans',sans-serif}
.block-container{padding-top:1.6rem;max-width:1450px}
h1,h2,h3{font-family:'Manrope',sans-serif!important;color:#17365D}
[data-testid="stSidebar"]{background:#132A43}
[data-testid="stSidebar"] *{color:#F4F7FA}
[data-testid="stMetric"]{background:white;border:1px solid #E4EAF0;border-radius:15px;padding:18px;box-shadow:0 4px 18px #17365D0A}
.stButton button,.stDownloadButton button{border-radius:10px;min-height:2.7rem;font-weight:700}
.stButton button[kind="primary"]{background:#176B70;color:white;border-color:#176B70}
.stTextInput input,.stNumberInput input{border-radius:9px}
.hero{background:linear-gradient(120deg,#17365D,#20506D 65%,#176B70);padding:26px 30px;border-radius:19px;color:white;margin-bottom:22px}
.hero h1{color:white!important;margin:0}.hero p{color:#DDEAF3;margin:.5rem 0 0}
.eyebrow{color:#A8E2DD;font-size:.75rem;text-transform:uppercase;letter-spacing:.12em;font-weight:800}
</style>
""", unsafe_allow_html=True)

DB = "incertezalab.db"
def db():
    c=sqlite3.connect(DB,check_same_thread=False)
    c.row_factory=sqlite3.Row
    return c
with db() as c:
    c.execute("""CREATE TABLE IF NOT EXISTS med (id INTEGER PRIMARY KEY, user TEXT, date TEXT,
    grandeza TEXT, unidade TEXT, instrumento TEXT, confianca TEXT, n INTEGER, media REAL,
    ua REAL, ub REAL, uc REAL, k REAL, U REAL, resultado TEXT, valores TEXT)""")

def hash_pw(p): return hashlib.sha256(p.encode()).hexdigest()
def users():
    try: return dict(st.secrets["auth"]["users"])
    except Exception: return {}
def login_ok(u,p):
    saved=users().get(u)
    return saved is not None and hmac.compare_digest(str(saved),hash_pw(p))

def pdf_bytes(r, user):
    b=io.BytesIO()
    doc=SimpleDocTemplate(b,pagesize=A4,rightMargin=42,leftMargin=42,topMargin=42,bottomMargin=42)
    s=getSampleStyleSheet()
    s.add(ParagraphStyle(name="T",parent=s["Title"],textColor=colors.HexColor("#17365D"),alignment=TA_CENTER,fontSize=21))
    data=[["Campo","Valor"],["Data",r["date"]],["Usuário",user],["Grandeza",f'{r["grandeza"]} ({r["unidade"]})'],
          ["Instrumento",r["instrumento"]],["Confiança",r["confianca"]],["Número de medições",str(r["n"])],
          ["Valores medidos",r["valores"]],["Média",f'{r["media"]:.6f} {r["unidade"]}'],
          ["Incerteza Tipo A",f'{r["ua"]:.6f} {r["unidade"]}'],["Incerteza Tipo B",f'{r["ub"]:.6f} {r["unidade"]}'],
          ["Incerteza combinada",f'{r["uc"]:.6f} {r["unidade"]}'],["Fator k",f'{r["k"]:.3f}'],
          ["Incerteza expandida",f'{r["U"]:.6f} {r["unidade"]}'],["Resultado",r["resultado"]]]
    t=Table(data,colWidths=[155,330],repeatRows=1)
    t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.HexColor("#17365D")),("TEXTCOLOR",(0,0),(-1,0),colors.white),
        ("GRID",(0,0),(-1,-1),.5,colors.HexColor("#DCE4EC")),("BACKGROUND",(0,1),(0,-1),colors.HexColor("#F1F5F9")),
        ("LEFTPADDING",(0,0),(-1,-1),8),("TOPPADDING",(0,0),(-1,-1),7),("BOTTOMPADDING",(0,0),(-1,-1),7)]))
    doc.build([Paragraph("IncertezaLab",s["T"]),Spacer(1,18),t,Spacer(1,20),
        Paragraph("Relatório gerado pelo IncertezaLab. Confira os dados de entrada e os critérios técnicos aplicáveis antes de usar o resultado.",s["Italic"])])
    return b.getvalue()

if "logged" not in st.session_state: st.session_state.logged=False
if not st.session_state.logged:
    st.markdown('<div class="hero"><div class="eyebrow">MMG • ENGENHARIA E METROLOGIA</div><h1>IncertezaLab</h1><p>Análise de incerteza de medição, com histórico e relatórios.</p></div>',unsafe_allow_html=True)
    with st.container(border=True):
        st.subheader("Acessar sua conta")
        with st.form("login"):
            u=st.text_input("Usuário")
            p=st.text_input("Senha",type="password")
            go=st.form_submit_button("Entrar",type="primary",use_container_width=True)
        if go:
            if login_ok(u.strip(),p):
                st.session_state.logged=True; st.session_state.user=u.strip(); st.rerun()
            else: st.error("Usuário ou senha incorretos. Configure as credenciais em Streamlit Secrets.")
    st.stop()

user=st.session_state.user
with st.sidebar:
    st.markdown("## 📐 IncertezaLab")
    st.caption("Automatic Uncertainty System")
    page=st.radio("NAVEGAÇÃO",["Painel","Nova medição","Histórico","Relatórios"],label_visibility="collapsed")
    st.divider(); st.caption(f"Conta: {user}")
    if st.button("Sair da conta",use_container_width=True):
        st.session_state.logged=False; st.session_state.pop("user",None); st.rerun()

def get_history():
    with db() as c: rows=c.execute("SELECT * FROM med WHERE user=? ORDER BY id DESC",(user,)).fetchall()
    return pd.DataFrame([dict(x) for x in rows])
hist=get_history()
st.markdown(f'<div class="hero"><div class="eyebrow">MMG • AUTOMATIC UNCERTAINTY SYSTEM</div><h1>{page}</h1><p>Gestão de medições e análise de incerteza em um só lugar.</p></div>',unsafe_allow_html=True)

if page=="Painel":
    a,b,c=st.columns(3)
    a.metric("Medições salvas",len(hist))
    b.metric("Última grandeza",hist.iloc[0]["grandeza"] if len(hist) else "—")
    c.metric("Último resultado",hist.iloc[0]["resultado"] if len(hist) else "Sem registros")
    st.subheader("Histórico das últimas medições")
    if len(hist):
        chart=hist.head(20).copy().iloc[::-1]
        chart["media"]=pd.to_numeric(chart["media"])
        fig=px.line(chart,x="date",y="media",markers=True,color_discrete_sequence=["#176B70"],
                    labels={"date":"Data","media":"Média medida"},hover_data=["grandeza","instrumento","resultado"])
        fig.update_layout(paper_bgcolor="white",plot_bgcolor="white",font_color="#17365D",height=360,
                          margin=dict(l=15,r=15,t=20,b=20),xaxis=dict(showgrid=False),yaxis=dict(gridcolor="#E8EDF2"))
        st.plotly_chart(fig,use_container_width=True)
        st.subheader("Registros recentes")
        st.dataframe(hist.head(5)[["date","grandeza","instrumento","resultado"]].rename(columns={"date":"Data","grandeza":"Grandeza","instrumento":"Instrumento","resultado":"Resultado"}),use_container_width=True,hide_index=True)
    else: st.info("Ainda não há medições. Acesse Nova medição para começar.")

elif page=="Nova medição":
    st.subheader("Identificação do instrumento")
    c1, c2, c3 = st.columns(3)
    instrumentos = [
        "Paquímetro", "Micrômetro", "Alicate amperímetro / Multímetro",
        "Megôhmetro", "Manifold digital WK-6889", "Termômetro", "Balança", "Outro"
    ]
    instrumento = c1.selectbox("Instrumento", instrumentos, key="instrumento_sel")

    grandezas_por_instrumento = {
        "Paquímetro": ["Comprimento"],
        "Micrômetro": ["Comprimento"],
        "Alicate amperímetro / Multímetro": ["Tensão elétrica", "Corrente elétrica", "Resistência elétrica", "Frequência", "Temperatura"],
        "Megôhmetro": ["Resistência de isolamento", "Tensão elétrica"],
        "Manifold digital WK-6889": ["Pressão", "Temperatura"],
        "Termômetro": ["Temperatura"],
        "Balança": ["Massa"],
        "Outro": ["Temperatura", "Pressão", "Comprimento", "Massa", "Tensão elétrica", "Corrente elétrica", "Resistência elétrica", "Outro"]
    }
    grandeza = c2.selectbox("Grandeza medida", grandezas_por_instrumento[instrumento], key="grandeza_sel")

    unidades_por_grandeza = {
        "Comprimento": ["mm", "cm", "m", "in"],
        "Temperatura": ["°C", "°F"],
        "Pressão": ["kPa", "bar", "psi"],
        "Massa": ["g", "kg"],
        "Tensão elétrica": ["V", "mV"],
        "Corrente elétrica": ["A", "mA"],
        "Resistência elétrica": ["Ω", "kΩ", "MΩ", "GΩ"],
        "Resistência de isolamento": ["MΩ", "GΩ"],
        "Frequência": ["Hz", "kHz"],
        "Outro": ["unidade personalizada"]
    }
    unidade_opcoes = unidades_por_grandeza.get(grandeza, ["unidade personalizada"])
    unidade_padrao = {
        "Paquímetro": "mm", "Micrômetro": "mm",
        "Alicate amperímetro / Multímetro": {"Tensão elétrica":"V", "Corrente elétrica":"A", "Resistência elétrica":"Ω", "Frequência":"Hz", "Temperatura":"°C"}.get(grandeza, unidade_opcoes[0]),
        "Megôhmetro": {"Resistência de isolamento":"MΩ", "Tensão elétrica":"V"}.get(grandeza, unidade_opcoes[0]),
        "Manifold digital WK-6889": {"Pressão":"kPa", "Temperatura":"°C"}.get(grandeza, unidade_opcoes[0]),
        "Termômetro":"°C", "Balança":"g", "Outro":unidade_opcoes[0]
    }
    u1, u2, u3 = st.columns(3)
    unidade = u1.selectbox("Unidade de medida", unidade_opcoes,
                           index=unidade_opcoes.index(unidade_padrao[instrumento]) if unidade_padrao[instrumento] in unidade_opcoes else 0,
                           key=f"unidade_{instrumento}_{grandeza}")
    confianca = u2.selectbox("Nível de confiança", ["90%", "95%", "99%"], index=1)
    n_medicoes = u3.caption("Informe pelo menos duas medições")

    # Somente valores com base nas informações disponíveis são preenchidos automaticamente.
    # A resolução de 0,02 mm do paquímetro foi confirmada pela usuária.
    resolucoes_documentadas = {"Paquímetro": (0.02, "mm", "informada para este instrumento")}
    res_doc = resolucoes_documentadas.get(instrumento)
    if res_doc and res_doc[1] != unidade:
        resolucao_padrao = 0.0
    else:
        resolucao_padrao = float(res_doc[0]) if res_doc else 0.0

    st.markdown("### Dados da medição")
    valores_txt = st.text_input("Medições separadas por vírgula", placeholder="10.01, 10.03, 10.02", key="valores_medidos")
    with st.expander("Componentes de incerteza Tipo B", expanded=True):
        st.caption("Use valores de certificado, resolução e deriva na unidade selecionada. Não há valores de calibração ou deriva cadastrados automaticamente.")
        x, y, z = st.columns(3)
        cert_txt = x.number_input("Componente do certificado", min_value=0.0, value=0.0, format="%.6f", key=f"cert_{instrumento}_{grandeza}_{unidade}", help="Informe a incerteza do certificado na unidade da medição. Deixe zero apenas se não houver esse dado; o resultado será sinalizado como preliminar.")
        resolucao = y.number_input("Resolução do instrumento", min_value=0.0, value=resolucao_padrao, format="%.6f", key=f"res_{instrumento}_{grandeza}_{unidade}", help="Paquímetro: resolução informada de 0,02 mm. Para os demais, informe a resolução indicada no instrumento/manual.")
        deriva = z.number_input("Componente de deriva", min_value=0.0, value=0.0, format="%.6f", key=f"deriva_{instrumento}_{grandeza}_{unidade}", help="Informe um valor fundamentado no histórico de calibração. Não é estimado automaticamente.")

    st.caption("A resolução é convertida em incerteza-padrão por distribuição retangular: resolução / √12. Os componentes inseridos devem estar na mesma unidade da medição.")
    parcial_tab, completo_tab = st.tabs(["Resultado parcial", "Resultado completo (estimativa)"])

    def calcular_resultado(vals, certificado, resol, deriv, conf):
        media = float(np.mean(vals))
        ua = float(np.std(vals, ddof=1) / np.sqrt(len(vals)))
        u_res = float(resol / np.sqrt(12)) if resol > 0 else 0.0
        ub = float(np.sqrt(certificado**2 + u_res**2 + deriv**2))
        uc = float(np.sqrt(ua**2 + ub**2))
        k = {"90%": 1.645, "95%": 2.0, "99%": 2.576}[conf]
        U = k * uc
        return {"media":media, "ua":ua, "ub":ub, "uc":uc, "k":k, "U":U}

    try:
        vals_preview = [float(v.strip().replace(",", ".")) for v in valores_txt.split(";") if v.strip()] if ";" in valores_txt else [float(v.strip().replace(",", ".")) for v in valores_txt.split(",") if v.strip()]
        entrada_valida = len(vals_preview) >= 2
    except ValueError:
        vals_preview = []
        entrada_valida = False

    with parcial_tab:
        st.write("Calcula usando as medições e os componentes de incerteza que você informou.")
        calcular_parcial = st.button("Calcular resultado parcial", type="primary", key="calc_parcial", use_container_width=True)
        if calcular_parcial:
            if not entrada_valida:
                st.error("Informe pelo menos duas medições numéricas. Separe os valores por vírgula ou ponto e vírgula.")
            else:
                r = calcular_resultado(vals_preview, cert_txt, resolucao, deriva, confianca)
                faltantes = []
                if cert_txt == 0: faltantes.append("incerteza do certificado de calibração não informada")
                if resolucao == 0: faltantes.append("resolução não informada")
                if deriva == 0: faltantes.append("deriva não informada")
                preliminar = bool(faltantes)
                resultado = f"{r['media']:.6f} ± {r['U']:.6f} {unidade}"
                st.session_state.last = {"date":dt.datetime.now().strftime("%d/%m/%Y %H:%M"), "grandeza":grandeza, "unidade":unidade, "instrumento":instrumento, "confianca":confianca, "n":len(vals_preview), "media":r["media"], "ua":r["ua"], "ub":r["ub"], "uc":r["uc"], "k":r["k"], "U":r["U"], "resultado":resultado, "valores":", ".join(map(str,vals_preview)), "status":"Estimativa preliminar" if preliminar else "Calculado com os componentes informados", "faltantes":faltantes}
                st.session_state.last_mode = "parcial"
                st.rerun()
        if st.session_state.get("last_mode") == "parcial" and "last" in st.session_state:
            r = st.session_state.last
            st.metric("Resultado parcial", r["resultado"])
            if r.get("faltantes"):
                st.warning("Estimativa preliminar. Componentes ausentes: " + "; ".join(r["faltantes"]) + ". Isso não significa que o instrumento inteiro esteja sem calibração; significa apenas que esses dados não foram informados nesta análise.")
            st.caption(f"Média: {r['media']:.6f} {unidade} · Tipo A: {r['ua']:.6f} · Tipo B: {r['ub']:.6f} · Combinada: {r['uc']:.6f} · k = {r['k']:.3f}")
            salvar = st.button("Salvar resultado parcial no histórico", key="save_partial", use_container_width=True)
            if salvar:
                with db() as con:
                    con.execute("INSERT INTO med (user,date,grandeza,unidade,instrumento,confianca,n,media,ua,ub,uc,k,U,resultado,valores) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                        (user,r["date"],r["grandeza"],r["unidade"],r["instrumento"],r["confianca"],r["n"],r["media"],r["ua"],r["ub"],r["uc"],r["k"],r["U"],r["resultado"],r["valores"]))
                    con.commit()
                st.success("Resultado parcial salvo no histórico.")
            st.download_button("Baixar relatório PDF", pdf_bytes(r,user), file_name="relatorio_incerteza_parcial.pdf", mime="application/pdf", key="pdf_partial", use_container_width=True)

    with completo_tab:
        st.write("Usa as medições, a resolução conhecida quando disponível e os componentes que você informou. Valores ausentes não são inventados.")
        if res_doc:
            st.info(f"Resolução cadastrada para {instrumento}: {res_doc[0]:g} {res_doc[1]}. Fonte: informação fornecida para este instrumento.")
        else:
            st.info("Não há resolução documentada cadastrada para este instrumento. Informe-a acima para que seja considerada no cálculo.")
        calcular_completo = st.button("Calcular estimativa completa", type="primary", key="calc_completo", use_container_width=True)
        if calcular_completo:
            if not entrada_valida:
                st.error("Informe pelo menos duas medições numéricas. Separe os valores por vírgula ou ponto e vírgula.")
            elif resolucao <= 0:
                st.error("Para a estimativa completa, informe uma resolução válida com base no instrumento ou manual.")
            else:
                r = calcular_resultado(vals_preview, cert_txt, resolucao, deriva, confianca)
                faltantes = []
                if cert_txt == 0: faltantes.append("incerteza do certificado de calibração não informada")
                if deriva == 0: faltantes.append("deriva não informada")
                preliminar = bool(faltantes)
                resultado = f"{r['media']:.6f} ± {r['U']:.6f} {unidade}"
                rec = {"date":dt.datetime.now().strftime("%d/%m/%Y %H:%M"), "grandeza":grandeza, "unidade":unidade, "instrumento":instrumento, "confianca":confianca, "n":len(vals_preview), "media":r["media"], "ua":r["ua"], "ub":r["ub"], "uc":r["uc"], "k":r["k"], "U":r["U"], "resultado":resultado, "valores":", ".join(map(str,vals_preview)), "status":"Estimativa preliminar" if preliminar else "Estimativa calculada", "faltantes":faltantes}
                st.session_state.last_complete = rec
                st.session_state.last_mode = "completo"
                st.rerun()
        if st.session_state.get("last_mode") == "completo" and "last_complete" in st.session_state:
            r = st.session_state.last_complete
            st.metric("Resultado completo estimado", r["resultado"])
            if r.get("faltantes"):
                st.warning("Estimativa preliminar. Componentes ausentes: " + "; ".join(r["faltantes"]) + ". O resultado usa a resolução disponível, mas não substitui certificado de calibração nem histórico de deriva.")
            else:
                st.success("Cálculo realizado com os componentes informados e a resolução cadastrada.")
            st.caption(f"Média: {r['media']:.6f} {unidade} · Tipo A: {r['ua']:.6f} · Tipo B: {r['ub']:.6f} · Combinada: {r['uc']:.6f} · k = {r['k']:.3f}")
            salvar = st.button("Salvar estimativa no histórico", key="save_complete", use_container_width=True)
            if salvar:
                with db() as con:
                    con.execute("INSERT INTO med (user,date,grandeza,unidade,instrumento,confianca,n,media,ua,ub,uc,k,U,resultado,valores) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                        (user,r["date"],r["grandeza"],r["unidade"],r["instrumento"],r["confianca"],r["n"],r["media"],r["ua"],r["ub"],r["uc"],r["k"],r["U"],r["resultado"],r["valores"]))
                    con.commit()
                st.success("Estimativa salva no histórico.")
            st.download_button("Baixar relatório PDF", pdf_bytes(r,user), file_name="relatorio_incerteza_estimativa.pdf", mime="application/pdf", key="pdf_complete", use_container_width=True)

elif page=="Histórico":
    st.subheader("Medições registradas")
    if hist.empty: st.info("O histórico está vazio.")
    else:
        c1,c2=st.columns(2)
        fg=c1.selectbox("Grandeza",["Todas"]+sorted(hist.grandeza.dropna().unique().tolist()))
        fi=c2.selectbox("Instrumento",["Todos"]+sorted(hist.instrumento.dropna().unique().tolist()))
        f=hist.copy()
        if fg!="Todas": f=f[f.grandeza==fg]
        if fi!="Todos": f=f[f.instrumento==fi]
        st.dataframe(f[["id","date","grandeza","instrumento","n","resultado"]].rename(columns={"id":"ID","date":"Data","grandeza":"Grandeza","instrumento":"Instrumento","n":"Nº medições","resultado":"Resultado"}),use_container_width=True,hide_index=True)
        st.download_button("Exportar histórico CSV",f.to_csv(index=False).encode("utf-8-sig"),"historico_incertezalab.csv","text/csv")

elif page=="Relatórios":
    st.subheader("Exportar medição em PDF")
    if hist.empty: st.info("Não há medições para exportar.")
    else:
        labels={f'#{r["id"]} • {r["date"]} • {r["resultado"]}':r for _,r in hist.iterrows()}
        label=st.selectbox("Escolha a medição",list(labels.keys()))
        x=labels[label]
        record={"date":x["date"],"grandeza":x["grandeza"],"unidade":x["unidade"],"instrumento":x["instrumento"],"confianca":x["confianca"],"n":int(x["n"]),"media":float(x["media"]),"ua":float(x["ua"]),"ub":float(x["ub"]),"uc":float(x["uc"]),"k":float(x["k"]),"U":float(x["U"]),"resultado":x["resultado"],"valores":x["valores"]}
        st.markdown(f"### {record['resultado']}")
        st.caption(f"{record['grandeza']} • {record['instrumento']} • {record['date']}")
        st.download_button("📄 Baixar PDF",pdf_bytes(record,user),file_name=f"relatorio_medicao_{x['id']}.pdf",mime="application/pdf",type="primary",use_container_width=True)

st.markdown("---")
st.caption("IncertezaLab • MMG • Engenharia Mecânica • Versão 2.1")
