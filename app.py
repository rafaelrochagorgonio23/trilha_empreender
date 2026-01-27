import streamlit as st
from trilhas import TRILHAS
from recomendador import recomendar_trilha

st.set_page_config(page_title="Trilha Empreender", page_icon="📈")
st.title("📈Trilha Empreender")
st.write("Descubra o próximo passo ideal para sua jornada.")

perfil = st.selectbox("Qual é sua situação atual?", ["Iniciante", "Estudante", "CLT", "Autônomo", "Já empreendo"])
objetivo = st.selectbox("Qual é seu principal objetivo?", ["Renda extra", "Empreender", "Mudar de carreira", "Validar ideia"])
tempo = st.selectbox("Em quanto tempo você espera resultados?", ["Até 3 meses", "3 a 6 meses", "Mais de 6 meses"])



area = st.selectbox("Qual área você mais se identifica?", [
    
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
   
])

if st.button("Gerar trilha"):
    trilha = recomendar_trilha(perfil, objetivo, area)
    
    st.write("---Estimativas de mercado com base em estatística---")
    st.subheader(trilha['nome'])
    st.write(trilha['descricao'])
    
    st.write("**Primeiros passos:")
    for passo in trilha['passos']:
        st.write(f"- {passo}")
        
    st.write("**Exemplos:")
    for exemplo in trilha['exemplos']:
        st.write(f"- {exemplo}")

    st.write("**Complexidade de produção:")
    st.write(trilha['complexidade_deproducao'])
    
    st.write("**Margem de lucro:")
    st.write(trilha['margem_delucro'])
    
    st.write("**Risco de mercado: É o risco de um investimento perder valor por causa de mudanças nas condições do mercado, como: Variação de preços (ações, moedas, commodities), variação das taxas de juros, inflação inesperada, crises econômicas ou políticas e mudança na oferta e demanda.")
    st.write(trilha['risco_demercado'])
    
    st.write("**Estimativa de investimento:")
    st.write(trilha['estimativa_investimentoinicial'])
    
    st.write("**Estimativa de capital de giro no início até o negócio atingir o ponto de equilíbrio - Break-even - Momento em que as receitas totais de uma empresa se igualam aos seus custos totais:")
    st.write(trilha['estimativa_capitaldegiro'])
    
    st.write("**Estimativa de rendimento inicial mensal:")
    st.write(trilha['estimativa_rendimentosiniciomensal'])
        
    st.write("**CAC - Custo de aquisição de clientes - CAC = (Total gasto em marketing + total gasto em vendas) / número de novos clientes no período:")
    st.write(trilha['CAC'])

st.markdown("---")
