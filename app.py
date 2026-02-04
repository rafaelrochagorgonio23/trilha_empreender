# ------------------------ IMPORTS ------------------------
import io
from datetime import datetime

import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors

# ---------------------------------------------------------
# Utilidades e normalizações
# ---------------------------------------------------------

def brl(valor):
    """Formata número em BRL. Para '', None e não numéricos, retorna '—'."""
    try:
        if valor in ("", None): 
            return "—"
        v = float(valor)
        return "R$ " + f"{v:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return str(valor) if valor not in ("", None) else "—"

def normaliza_cenarios(cenarios_dict):
    """
    Normaliza as chaves do dicionário de cenários para: Conservador, Provavel, Otimista.
    Aceita variações: 'conservador', 'Conservador', 'otimista', etc.
    """
    alvo = {"Conservador": "—", "Provavel": "—", "Otimista": "—"}
    if not isinstance(cenarios_dict, dict):
        return alvo
    m = {k.strip().lower(): v for k, v in cenarios_dict.items()}
    if "conservador" in m: alvo["Conservador"] = brl(m["conservador"])
    if "provavel" in m or "provável" in m:
        alvo["Provavel"] = brl(m.get("provavel", m.get("provável")))
    if "otimista" in m: alvo["Otimista"] = brl(m["otimista"])
    return alvo

def recomendar_trilha_por_area(area_escolhida: str, trilhas: list[dict]) -> dict | None:
    """
    Retorna a primeira trilha que bate com a área selecionada.
    (Se quiser lógica mais sofisticada com perfil/objetivo, me diga e eu ajusto.)
    """
    for t in trilhas:
        if str(t.get("area", "")).strip().lower() == str(area_escolhida).strip().lower():
            return t
    return None

def opcoes_de_area(trilhas: list[dict]) -> list[str]:
    """Lista única de áreas para o selectbox."""
    vistas = []
    for t in trilhas:
        a = t.get("area")
        if a and a not in vistas:
            vistas.append(a)
    return vistas

# ---------------------------------------------------------
# Geração do PDF (com base no seu TRILHAS)
# ---------------------------------------------------------

def gerar_pdf_trilha(form_data: dict, trilha: dict) -> bytes:
    """
    form_data: dict com dados do formulário (perfil, objetivo, tempo, area)
    trilha: item do TRILHAS selecionado
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm,
        title=f"Trilha - {trilha.get('nome','')}",
        author="Aplicativo de Trilhas"
    )

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="Titulo", parent=styles["Heading1"], spaceAfter=12))
    styles.add(ParagraphStyle(name="Subtitulo", parent=styles["Heading2"], textColor=colors.HexColor("#1f4e79"), spaceAfter=8))
    styles.add(ParagraphStyle(name="Body", parent=styles["BodyText"], leading=14))
    styles.add(ParagraphStyle(name="Label", parent=styles["BodyText"], textColor=colors.grey, spaceAfter=4))

    story = []

    # Cabeçalho
    story.append(Paragraph("Trilha Recomendada", styles["Titulo"]))
    story.append(Paragraph(datetime.now().strftime("%d/%m/%Y %H:%M"), styles["Label"]))
    story.append(Spacer(1, 12))

    # Resumo do formulário
    resumo_data = [
        ["Perfil", str(form_data.get("perfil", ""))],
        ["Objetivo", str(form_data.get("objetivo", ""))],
        ["Tempo disponível", str(form_data.get("tempo", ""))],
        ["Área escolhida", str(form_data.get("area", ""))],
    ]
    tabela_resumo = Table(resumo_data, colWidths=[4*cm, 10*cm])
    tabela_resumo.setStyle(TableStyle([
        ("BOX", (0,0), (-1,-1), 0.5, colors.grey),
        ("INNERGRID", (0,0), (-1,-1), 0.25, colors.grey),
        ("BACKGROUND", (0,0), (0,-1), colors.whitesmoke),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("ALIGN", (0,0), (-1,-1), "LEFT"),
    ]))
    story.append(Paragraph("Informações do formulário", styles["Subtitulo"]))
    story.append(tabela_resumo)
    story.append(Spacer(1, 14))

    # Título + descrição da trilha
    if trilha.get("nome"):
        story.append(Paragraph(trilha["nome"], styles["Subtitulo"]))
    if trilha.get("descricao"):
        story.append(Paragraph(str(trilha["descricao"]), styles["Body"]))
        story.append(Spacer(1, 10))

    # Bloco: Viabilidade / Risco / Margem / CAC
    cenarios = normaliza_cenarios(trilha.get("estimativa_rendimentosiniciomensal"))
    bloco_viabilidade = [
        ["Complexidade de produção", str(trilha.get("complexidade_deproducao", "—"))],
        ["Margem de lucro", str(trilha.get("margem_delucro", "—"))],
        ["Risco de mercado", str(trilha.get("risco_demercado", "—"))],
        ["CAC", str(trilha.get("CAC", "—"))],
        ["Investimento inicial", brl(trilha.get("estimativa_investimentoinicial"))],
        ["Capital de giro", brl(trilha.get("estimativa_capitaldegiro"))],
    ]
    tabela_viabilidade = Table(bloco_viabilidade, colWidths=[6*cm, 8*cm])
    tabela_viabilidade.setStyle(TableStyle([
        ("BOX", (0,0), (-1,-1), 0.5, colors.grey),
        ("INNERGRID", (0,0), (-1,-1), 0.25, colors.grey),
        ("BACKGROUND", (0,0), (0,-1), colors.HexColor("#f6f6f6")),
    ]))
    story.append(Paragraph("Viabilidade e indicadores", styles["Subtitulo"]))
    story.append(tabela_viabilidade)
    story.append(Spacer(1, 10))

    # Bloco: Estimativa de rendimentos
    tabela_renda = Table(
        [["Cenário", "Estimativa mensal"],
         ["Conservador", cenarios["Conservador"]],
         ["Provável", cenarios["Provavel"]],
         ["Otimista", cenarios["Otimista"]]],
        colWidths=[5*cm, 9*cm]
    )
    tabela_renda.setStyle(TableStyle([
        ("BOX", (0,0), (-1,-1), 0.5, colors.grey),
        ("INNERGRID", (0,0), (-1,-1), 0.25, colors.grey),
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#e8f0fe")),
    ]))
    story.append(Paragraph("Estimativas de rendimentos iniciais (mensal)", styles["Subtitulo"]))
    story.append(tabela_renda)
    story.append(Spacer(1, 10))

    # Passos
    passos = trilha.get("passos", [])
    if isinstance(passos, (list, tuple)) and passos:
        story.append(Paragraph("Principais passos", styles["Subtitulo"]))
        for i, p in enumerate(passos, 1):
            story.append(Paragraph(f"{i}. {p}", styles["Body"]))
        story.append(Spacer(1, 8))

    # Exemplos
    exemplos = trilha.get("exemplos", [])
    if isinstance(exemplos, (list, tuple)) and exemplos:
        story.append(Paragraph("Exemplos", styles["Subtitulo"]))
        for ex in exemplos:
            story.append(Paragraph(f"• {ex}", styles["Body"]))
        story.append(Spacer(1, 8))

    # Observação legal/sanidade de estimativas
    story.append(Spacer(1, 12))
    story.append(Paragraph(
        "Observação: As estimativas são aproximadas e não constituem garantia de resultados. "
        "Faça sua validação local de demanda, custos e preços.",
        styles["Label"]
    ))

    # Página 2 opcional (se desejar, descomente para separar seções longas)
    # story.append(PageBreak())

    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes

# ---------------------------------------------------------
# UI Streamlit (exemplo integrado ao seu fluxo)
# ---------------------------------------------------------

st.title("Trilhas para Empreender")

# As áreas vêm diretamente do seu TRILHAS
areas_disp = opcoes_de_area(TRILHAS)

col1, col2 = st.columns(2)
with col1:
    perfil = st.selectbox("Qual é o seu perfil?", ["Iniciante", "Intermediário", "Avançado"])
    tempo = st.selectbox("Quanto tempo você tem por semana?", ["2h", "4h", "6h", "8h+"])
with col2:
    objetivo = st.text_input("Qual é seu objetivo principal?")
    area = st.selectbox("Qual área você mais se identifica?", areas_disp)

if st.button("Gerar trilha"):
    trilha = recomendar_trilha_por_area(area, TRILHAS)

    if not trilha:
        st.error("Não encontrei trilha para a área selecionada. Verifique as opções.")
        st.stop()

    st.write("---")
    st.subheader(trilha.get("nome", "Trilha"))
    if trilha.get("descricao"): st.write(trilha["descricao"])

    st.markdown("**Principais passos:**")
    for p in trilha.get("passos", []):
        st.write(f"- {p}")

    st.markdown("**Exemplos:**")
    for ex in trilha.get("exemplos", []):
        st.write(f"- {ex}")

    st.markdown("**Complexidade de produção:**")
    st.write(trilha.get("complexidade_deproducao", "—"))

    st.markdown("**Margem de lucro / Risco de mercado / CAC:**")
    st.write(
        f"- Margem: {trilha.get('margem_delucro', '—')}\n"
        f"- Risco: {trilha.get('risco_demercado', '—')}\n"
        f"- CAC: {trilha.get('CAC', '—')}"
    )

    st.markdown("**Investimentos e rendimentos iniciais (mensal):**")
    cen = normaliza_cenarios(trilha.get("estimativa_rendimentosiniciomensal"))
    st.write(
        f"- Investimento inicial: {brl(trilha.get('estimativa_investimentoinicial'))}\n"
        f"- Capital de giro: {brl(trilha.get('estimativa_capitaldegiro'))}\n"
        f"- Conservador: {cen['Conservador']} | Provável: {cen['Provavel']} | Otimista: {cen['Otimista']}"
    )

    # Monta o dicionário do formulário para o PDF
    form_data = {
        "perfil": perfil,
        "objetivo": objetivo,
        "tempo": tempo,
        "area": area
    }

    # Gera PDF e oferece para download
    pdf_bytes = gerar_pdf_trilha(form_data, trilha)
    st.download_button(
        label="⬇️ Baixar PDF da trilha",
        data=pdf_bytes,
        file_name=f"trilha_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
        mime="application/pdf"
    )
