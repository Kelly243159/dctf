import streamlit as st
import pandas as pd
import json
import base64
import os
from datetime import datetime, timedelta
import tempfile

# Configuração da página
st.set_page_config(
    page_title="Monitoramento DCTFWeb/REINF",
    page_icon="📊",
    layout="wide"
)

# Estrutura de dados
if 'certificado' not in st.session_state:
    st.session_state.certificado = {"caminho": "", "senha": "", "arquivo": None}
if 'empresas' not in st.session_state:
    st.session_state.empresas = []
if 'periodo' not in st.session_state:
    st.session_state.periodo = {"inicio": datetime.now().replace(day=1), "fim": datetime.now()}

# Funções
def cadastrar_certificado(arquivo, senha):
    if arquivo and senha:
        # Ler conteúdo do arquivo
        file_bytes = arquivo.getvalue()
        st.session_state.certificado = {
            "caminho": arquivo.name,
            "senha": senha,
            "arquivo": base64.b64encode(file_bytes).decode('utf-8')
        }
        st.success("Certificado cadastrado com sucesso!")
        return True
    else:
        st.error("Por favor, selecione um arquivo e informe a senha.")
        return False

def adicionar_empresa(nome, cnpj):
    if nome and cnpj:
        # Verificar se CNPJ já existe
        for emp in st.session_state.empresas:
            if emp['cnpj'] == cnpj:
                st.error("CNPJ já cadastrado!")
                return False
        
        st.session_state.empresas.append({
            "nome": nome, 
            "cnpj": cnpj,
            "status": "Não verificado",
            "ultima_verificacao": None
        })
        st.success(f"Empresa {nome} adicionada com sucesso!")
        return True
    else:
        st.error("Por favor, preencha todos os campos.")
        return False

def remover_empresa(index):
    if 0 <= index < len(st.session_state.empresas):
        empresa = st.session_state.empresas.pop(index)
        st.success(f"Empresa {empresa['nome']} removida!")
    else:
        st.error("Índice de empresa inválido.")

def simular_consulta():
    # Esta função simularia a consulta real ao DCTFWeb/REINF
    # Em uma implementação real, aqui você usaria bibliotecas como requests, selenium, etc.
    
    if not st.session_state.certificado['arquivo']:
        st.error("Certificado não cadastrado!")
        return False
    
    if not st.session_state.empresas:
        st.error("Nenhuma empresa cadastrada!")
        return False
    
    # Simular processo de consulta
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, empresa in enumerate(st.session_state.empresas):
        progress = (i + 1) / len(st.session_state.empresas)
        progress_bar.progress(progress)
        status_text.text(f"Verificando {empresa['nome']} ({i+1}/{len(st.session_state.empresas)})")
        
        # Simular atraso de rede/processamento
        import time
        time.sleep(0.5)
        
        # Simular resultado (aleatório para demonstração)
        import random
        resultados = ["Entregue", "Não entregue", "Pendente"]
        st.session_state.empresas[i]['status'] = random.choice(resultados)
        st.session_state.empresas[i]['ultima_verificacao'] = datetime.now().strftime("%d/%m/%Y %H:%M")
    
    progress_bar.empty()
    status_text.empty()
    st.success("Consulta concluída!")
    return True

def exportar_resultados():
    if not st.session_state.empresas:
        st.error("Nenhum dado para exportar!")
        return None
    
    df = pd.DataFrame(st.session_state.empresas)
    return df.to_csv(index=False).encode('utf-8')

# Interface principal
st.title("📊 Monitoramento DCTFWeb/REINF")
st.markdown("Sistema para monitoramento de declarações fiscais via procuração digital")

# Abas para organização
tab1, tab2, tab3, tab4 = st.tabs(["Certificado", "Empresas", "Consulta", "Resultados"])

with tab1:
    st.header("📋 Cadastro de Certificado Digital")
    
    uploaded_file = st.file_uploader(
        "Selecione o certificado digital (PFX/P12)", 
        type=['pfx', 'p12'],
        help="Certificado digital no formato PFX ou P12"
    )
    
    cert_password = st.text_input(
        "Senha do certificado", 
        type="password",
        help="Senha do certificado digital"
    )
    
    if st.button("Cadastrar Certificado"):
        if cadastrar_certificado(uploaded_file, cert_password):
            st.info(f"Certificado: {st.session_state.certificado['caminho']}")

with tab2:
    st.header("🏢 Gestão de Empresas")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Adicionar Empresa")
        with st.form("empresa_form"):
            nome_empresa = st.text_input("Nome da Empresa")
            cnpj_empresa = st.text_input("CNPJ", help="Apenas números")
            
            if st.form_submit_button("Adicionar Empresa"):
                adicionar_empresa(nome_empresa, cnpj_empresa)
    
    with col2:
        st.subheader("Empresas Cadastradas")
        if st.session_state.empresas:
            for i, emp in enumerate(st.session_state.empresas):
                cols = st.columns([3, 1])
                cols[0].write(f"**{emp['nome']}** - {emp['cnpj']}")
                if cols[1].button("🗑️", key=f"del_{i}"):
                    remover_empresa(i)
                    st.rerun()
        else:
            st.info("Nenhuma empresa cadastrada.")

with tab3:
    st.header("🔍 Consulta de Status")
    
    st.subheader("Período de Referência")
    col1, col2 = st.columns(2)
    with col1:
        data_inicio = st.date_input(
            "Data inicial", 
            value=st.session_state.periodo['inicio'],
            help="Data inicial do período a ser consultado"
        )
    with col2:
        data_fim = st.date_input(
            "Data final", 
            value=st.session_state.periodo['fim'],
            help="Data final do período a ser consultado"
        )
    
    st.session_state.periodo = {"inicio": data_inicio, "fim": data_fim}
    
    if st.button("Realizar Consulta", type="primary"):
        simular_consulta()
        st.rerun()

with tab4:
    st.header("📋 Resultados da Consulta")
    
    if st.session_state.empresas:
        # Preparar dados para exibição
        df = pd.DataFrame(st.session_state.empresas)
        
        # Colorir status
        def color_status(val):
            if val == "Entregue":
                return 'color: green; font-weight: bold'
            elif val == "Não entregue":
                return 'color: red; font-weight: bold'
            else:
                return 'color: orange; font-weight: bold'
        
        styled_df = df.style.applymap(color_status, subset=['status'])
        
        st.dataframe(
            styled_df,
            use_container_width=True,
            hide_index=True
        )
        
        # Estatísticas
        col1, col2, col3 = st.columns(3)
        entregue = len(df[df['status'] == 'Entregue'])
        nao_entregue = len(df[df['status'] == 'Não entregue'])
        pendente = len(df[df['status'] == 'Pendente'])
        
        col1.metric("Entregue", entregue)
        col2.metric("Não Entregue", nao_entregue)
        col3.metric("Pendente", pendente)
        
        # Botão de exportação
        csv = exportar_resultados()
        if csv:
            st.download_button(
                label="📥 Exportar Resultados (CSV)",
                data=csv,
                file_name=f"resultados_dctf_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv"
            )
    else:
        st.info("Execute uma consulta para ver os resultados.")

# Sidebar com informações
with st.sidebar:
    st.header("ℹ️ Informações")
    
    if st.session_state.certificado['caminho']:
        st.success("Certificado cadastrado")
        st.caption(f"Arquivo: {st.session_state.certificado['caminho']}")
    else:
        st.warning("Certificado não cadastrado")
    
    st.divider()
    st.write(f"Empresas cadastradas: **{len(st.session_state.empresas)}**")
    
    if st.session_state.periodo:
        st.write("Período selecionado:")
        st.write(f"Início: **{st.session_state.periodo['inicio'].strftime('%d/%m/%Y')}**")
        st.write(f"Fim: **{st.session_state.periodo['fim'].strftime('%d/%m/%Y')}**")
    
    st.divider()
    st.caption("Versão 1.0 - Desenvolvido para monitoramento DCTFWeb/REINF")

# Notas de implementação
with st.expander("Notas de Implementação"):
    st.info("""
    **Funcionalidades implementadas:**
    - Cadastro de certificado digital (PFX/P12)
    - Gestão de empresas (CNPJs) para monitoramento
    - Seleção de período de consulta
    - Simulação de consulta ao DCTFWeb/REINF
    - Visualização de resultados com status colorido
    - Exportação de resultados em CSV
    
    **Para implementação real:**
    - Integração com API ou automação web do DCTFWeb/REINF
    - Armazenamento seguro de certificados
    - Agendamento de consultas automáticas
    - Notificações por e-mail/telegram
    - Histórico de consultas
    """)