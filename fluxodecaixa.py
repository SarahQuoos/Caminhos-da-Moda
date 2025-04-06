# -*- coding: utf-8 -*-
"""
Created on Tue Mar 18 13:01:28 2025

@author: Sarah
"""

import streamlit as st
import time
import pandas as pd
from datetime import datetime
import gspread

@st.cache_resource(ttl=60)
def get_client():
    g_sheets_creds = st.secrets['gsheets']
    #Identificando arquivo do drive e as credenciais
    scope = ['https://www.googleapis.com/auth/spreadsheets', "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]

    client = gspread.service_account_from_dict(g_sheets_creds)
    return client



#Configuração de Página
st.set_page_config(
    page_title="Caminhos da Moda",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "# Desenvolvido por Sarah Quoos, Curitiba, PR, 2025"})

#Título Página
st.title("Fluxo de Caixa Caminhos da Moda")

#Subtítulo
st.markdown("### Consulta produtos disponíveis")

#Abrindo arquivo no drive e transformando em dataframe no pandas
arquivo = get_client().open('Fluxodecaixa_Caminhosdamoda')
sheet = arquivo.worksheet("Lista Produtos")

data = sheet.get_all_values()
colunas = data.pop(0)
listaprodutos = pd.DataFrame(data,columns=colunas)

arquivo.client.session.close()

#Fazendo filtro
query = st.text_input("Filtro")
if query:
    mask = listaprodutos.applymap(lambda x: query.upper() in str(x).upper()).any(axis=1)
    listaprodutos = listaprodutos[mask]

st.data_editor(listaprodutos,hide_index=True,) 

#Rotina Cadastro categoria e geração de código
def Cadastro():
    categoria = st.selectbox("Categoria:",("Select", "Biquini","Blazer","Blusa","Bolsa","Calça", "Camisa","Camiseta",
                                           "Chapéu","Jaqueta","Macacão","Maiô","Pijama","Saia","Saída de Praia",
                                           "Shorts","TOP", "Vestido"),)
    
    #Abrindo arquivos no drive
    arquivo = get_client().open('Fluxodecaixa_Caminhosdamoda')
    sheet1 = arquivo.worksheet("Lista Produtos")  
    sheet3 = arquivo.worksheet("Códigos")
    
    #Pegando código do produto
    cell = sheet3.find(categoria)
    linha = cell.row
    codx = sheet3.cell(linha, 6).value

    #Continuação do cadastro
    with st.form(key='cadastro'):
        status = 'Disponivel'
        codigo = st.text_input("Código:", codx)
        proprietario = st.text_input('Proprietária:')
        produto = st.text_input('Descrição do Produto:')
        marca = st.text_input('Marca:')
        numeracao = st.selectbox("Numeração:",("Select","PP","P","M","G","GG","36","38","40","42","44","46"),)
        valor = st.number_input('Valor de Venda:')
        valorpago = st.number_input('Valor Pago na peça:')
        valoretorno = st.number_input('Porcentagem Consignação:')
    
        #Faz dataframe
        cadastro = [status, categoria, codigo, proprietario, produto, marca, numeracao, valor, valorpago, valoretorno]
        
        #Botões de cadastro
        if st.form_submit_button("Cadastrar"):
            if (categoria == "Select") or (proprietario == "") or (produto == "") or (valor == 0):
                st.write("Preencha todas as informações para cadastro")
            else:
                sheet1.append_row(cadastro)
                st.write("Produto cadastrado com sucesso!")
                #atualizando a página
                time.sleep(1.0)
                st.rerun()
            
#Rotina Venda
def Venda():
    codigo = st.text_input('Qual é o Código?')
    #Procura código banco de dados
    arquivo = get_client().open('Fluxodecaixa_Caminhosdamoda')
    sheet1 = arquivo.worksheet("Lista Produtos")
    sheet2 = arquivo.worksheet("Vendas")
    
    #Pegando código do produto
    if codigo == "":
        linha = 0
        data = 0
        valorpago = 0
        porcentagem = 0  
    else: 
        #Pegando código do produto
        search = sheet1.find(codigo.upper())
        linha = search.row
        data = sheet1.row_values(linha)
        valorpago = sheet1.cell(linha, 8).value
        valorpago = float(valorpago.replace(',','.'))
        porcentagem = sheet1.cell(linha, 10).value
        porcentagem = float(porcentagem)
     
    with st.form(key='venda'):
        #Restante das informações de venda
        valorreal = st.number_input('Valor Real da Venda:', value=valorpago)
        pagamento = st.selectbox("Forma de Pagamento:",("Select", "Pix","Crédito","Débito","Dinheiro"),)
        date = datetime.today().strftime('%d-%m-%Y')

        botao_vendido = st.form_submit_button('Vendido')
    

    #Atualiza planilhas
    if botao_vendido:
        #Calculo do lucro
        if porcentagem == 0:  
            lucro = valorreal
            retorno = 0
        else:
            lucro = valorreal - (((100-porcentagem)*valorreal)/100)
            retorno = valorreal - ((porcentagem)*valorreal)/100
                
        #Faz dataframe
        venda = [valorreal, lucro, pagamento, retorno, date]
        if (codigo == "") or (pagamento == "Select") or (valorreal == 0):
            st.write("Preencha todas as informações para realizar a venda")
        else:
            #Substitui status e atualiza planilhas
            for i in range(len(data)):
                if data[i] == "Disponivel":
                    data[i] = "Vendido"
            venda_new = data + venda
            sheet2.append_row(venda_new, value_input_option=gspread.utils.ValueInputOption.user_entered)
            sheet1.delete_rows(linha)
            st.write("Produto atualizado com sucesso!")
            #atulizando a pagina
            st.rerun()

#Rotina de cadastro de despezas mensais
def Despezas():
    #ano =  st.selectbox("Selecione o Ano:",("Select", "2024","2025"),)
    #mes = st.selectbox("Selecione o Mês:",("Select", "Janeiro","Fevereiro","Março","Abril", "Maio", "Junho", "Julho"),)
    date = datetime.today().strftime('%d-%m-%Y')
    des = st.text_input('Informe a Descrição da Despeza:')
    valor = st.number_input('Valor da Despeza:')
    
    
    #Faz dataframe
    despeza = [date, des, valor]
    
    #Abrindo arquivo excel
    arquivo = get_client().open('Fluxodecaixa_Caminhosdamoda')
    sheet4 = arquivo.worksheet("Despezas")
    
    if st.button("Cadastrar", key='cadastrar_despesa'):
        if (des == "") or (valor == 0):
            st.write("Preencha todas as informações para cadastro")
        else:
            sheet4.append_row(despeza)
            st.write("Despeza cadastrada com sucesso!")
                
#Menu de opções
with st.sidebar:
    st.title("Opções e Serviços")
    if st.checkbox ("Cadastro"):
        Cadastro()
    if st.checkbox ("Vendas"):
        Venda()
    if st.checkbox ("Despezas"):
        Despezas()

#Visualização de Despezas e produtos vendidos
st.markdown("### Consulta produtos vendidos")
if st.checkbox("Conferir vendas"):
    sheet2 = arquivo.worksheet("Vendas")
    data2 = sheet2.get_all_values()
    colunas2 = data2.pop(0)
    listavendas = pd.DataFrame(data2,columns=colunas2)
    st.write(listavendas)

st.markdown("### Consulta das despezas")
if st.checkbox("Conferir Despezas"):
    sheet4 = arquivo.worksheet("Despezas")
    data4 = sheet4.get_all_values()
    colunas4 = data4.pop(0)
    listadespezas = pd.DataFrame(data4,columns=colunas4)    
    st.write(listadespezas)
