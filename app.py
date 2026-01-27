# ==== IMPORTS (ordem correta) ====
import json
from datetime import datetime

import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

from trilhas import TRILHAS
from recomendador import recomendar_trilha


# ==== CONFIGURAÇÕES DE PÁGINA ====
st.set_page_config(page_title="Trilha Empreender", page_icon="📈", layout="centered")


# ==== CONEXÃO GOOGLE SHEETS (usando st.secrets) ====
# Em Settings > Secrets do Streamlit, você deve ter algo como:
# [gcp_service_account]
# ... (campos da sua service account)
# [sheets]
# sheet_id = "1tJUnK8kqe9uyRTCq20uSN5gswv1_0PpR1cMpxLq72gk"

scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"], scopes=scope
)
client = gspread.authorize(creds)

SHEET_ID = st.secrets.get("sheets", {}).get(
    "sheet_id", "1tJUnK8kqe9uyRTCq20uSN5gswv1_0PpR1cMpxLq72gk"  # fallback opcional
)
# ATENÇÃO: troque "respostas" pelo nome exato da aba (worksheet) da sua planilha.
ws = client.open_by_key(SHEET_ID).worksheet("A")


# ==== UI ====
st.title("📈 Trilha Empreender")
st.write("Descubra o próximo passo ideal para sua jornada.")

perfil = st.selectbox(
    "Qual é sua situação atual?",
    ["Iniciante", "Estudante", "CLT", "Autônomo", "Já empreendo"]
)

objetivo = st.selectbox(
    "Qual é seu principal objetivo?",
    ["Renda extra", "Empreender", "Mudar de carreira", "Validar ideia"]
)

tempo = st.selectbox(
    "Em quanto tempo você espera resultados?",
    ["Até 3 meses", "3 a 6 meses", "Mais de 6 meses"]
)

area = st.selectbox(
    "Qual área você mais se identifica?",
    [
        "Alimentos e bebidas",
        "Artesanato",
        "Entregador de Comidas (iFood, Rappi, Apps Locais) - Logística de Entrega de Alimentos - Delivery",
        "Entregador de Mercadorias (Mercado Livre, Shopee, Amazon e Entregas Locais) - Logística Última Milha",
        "Moda e Brechó",
        "Pet e Bem-estar Animal",
        "Produtos personalizados Sublimação",
        "Serviços Digitais Design",
        "Serviços Digitais Edição de Vídeo",
        "Serviços Digitais Social Media",
        "Serviços de Tecnologia Suporte Técnico",
        "Serviços Pessoais Barbearia e Corte Masculino",
        "Serviços Pessoais Design de Sobrancelhas",
        "Serviços Pessoais Manicure e Cuidados com as Unhas",
        "Serviços Pessoais Salão de Beleza e Corte Feminino",
        "Tecnologia / dados",
        "Tecnologia Impressão 3D",
        "Transporte Individual de Passageiros Motorista de Aplicativo",
        "Varejo Automotivo Baterias para Carros (linha leve)",
        "Varejo de Acessórios para Dispositivos Móveis - Loja de Acessórios para Celular e Tablet",
        "Varejo Materiais/Artigos Elétricos",
    ],
)


# ==== AÇÃO 1: Mostrar a trilha detalhada ====
if st.button("Gerar trilha (detalhes)"):
    # Garanta que a assinatura de recomendar_trilha aceite (perfil, objetivo, tempo, area)
    trilha = recomendar_trilha(perfil, objetivo, tempo, area)

    st.write("---")
    st.subheader(trilha["nome"])
    st.write(trilha["descricao"])

    st.write("**Primeiros passos:**")
    for passo in trilha["passos"]:
        st.write(f"- {passo}")

    st.write("**Exemplos:**")
    for exemplo in trilha["exemplos"]:
        st.write(f"- {exemplo}")

    st.write("**Complexidade de produção:**")
    st.write(trilha["complexidade_deproducao"])

    st.write("**Margem de lucro:**")
    st.write(trilha["margem_delucro"])

    st.write(
        "**Risco de mercado:** É o risco de um investimento perder valor por causa de "
        "mudanças nas condições do mercado, como: variação de preços (ações, moedas, commodities), "
        "variação das taxas de juros, inflação inesperada, crises econômicas ou políticas e mudança na oferta e demanda."
    )
    st.write(trilha["risco_demercado"])

    st.write("**Estimativa de investimento:**")
    st.write(trilha["estimativa_investimentoinicial"])

    st.write(
        "**Estimativa de capital de giro no início até o negócio atingir o ponto de equilíbrio (Break-even):**"
    )
    st.write(trilha["estimativa_capitaldegiro"])

    st.write("**Estimativa de rendimento inicial mensal:**")
    st.write(trilha["estimativa_rendimentosiniciomensal"])

    st.write(
        "**CAC (Custo de Aquisição de Clientes)** = (Total gasto em marketing + total gasto em vendas) / número de novos clientes no período:"
    )
    st.write(trilha["CAC"])


# ==== AÇÃO 2: Gerar recomendação + salvar no Sheets (sem try/except) ====
if st.button("Gerar recomendação e salvar"):
    trilha = recomendar_trilha(perfil, objetivo, tempo, area)

    # Mostra um resumo da recomendação
    st.success(f"Recomendação: {trilha['nome']}")

    # Salva no Google Sheets (apenas campos simples)
    ws.append_row(
        [
            datetime.now().isoformat(timespec="seconds"),
            perfil,
            objetivo,
            tempo,
            area,
            trilha["nome"],  # se quiser salvar tudo: json.dumps(trilha, ensure_ascii=False)
        ],
        value_input_option="USER_ENTERED",
    )

    st.info("Registro salvo com sucesso na planilha. ✅")
