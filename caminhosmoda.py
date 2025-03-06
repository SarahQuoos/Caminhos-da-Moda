# -*- coding: utf-8 -*-
"""
Created on Tue Mar  4 07:09:51 2025

@author: Sarah
"""

import streamlit as st
import pandas as pd
#import time
from datetime import datetime
import numpy as np
import PyAutoGUI

#Configuração de Página
st.set_page_config(
    page_title="Caminhos da Moda",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "# Desenvolvido por Sarah Quoos, Curitiba, PR, 2025"}
    )

#Título Página
st.title("Fluxo de Caixa Caminhos da Moda")

#Visualização de dados
st.markdown("### Consulta produtos disponíveis")
sheet = pd.read_excel('Caminhos da Moda.xlsx', sheet_name='Lista Produtos')
query = st.text_input("Filtro")
if query:
    mask = sheet.applymap(lambda x: query in str(x).upper()).any(axis=1)
    sheet = sheet[mask]

st.data_editor(sheet,hide_index=True,) 

#Botão atualizar dados
if st.button("Atualizar"):
    pyautogui.hotkey("ctrl","F5")
    time.sleep(0.5)

#Rotina Cadastro
def Cadastro():
    status = 'Disponível'
    categoria = st.selectbox("Categoria:",("Select", "Biquini","Blusa","Bolsa","Calça", "Camisa","Camiseta",
                                           "Chapéu","Jaqueta","Macacão","Maiô","Pijama","Saia","Saída de Praia",
                                           "Shorts","TOP", "Vestido"),)
    codigo = st.text_input('Código:')
    proprietario = st.text_input('Proprietária:')
    produto = st.text_input('Descrição do Produto:')
    marca = st.text_input('Marca:')
    numeracao = st.selectbox("Numeração:",("Select","PP","P","M","G","GG","36","38","40","42","44","46"),)
    valor = st.number_input('Valor de Venda:')
    valorpago = st.number_input('Valor Pago na peça:')
    valoretorno = st.number_input('Porcentagem Consignação:')
    
    #Faz dataframe
    cadastro = [[status, categoria, codigo, proprietario, produto, marca, numeracao, valor, valorpago, valoretorno],]
     
    cadastro_df = pd.DataFrame(
        data=cadastro,
        columns=['Status','Categoria','Código','Proprietária','Produto','Marca','Numeração','Valor de Venda',
                 'Valor Pago na peça','Porcetagem Consignação'])
    
    #Botões de cadastro e reset
    #bot_1, bot_2 = st.columns(2)
    
    #with bot_1:
    if st.button("Cadastrar"):
        df = pd.read_excel('Caminhos da Moda.xlsx', sheet_name='Lista Produtos')
        data = pd.concat([df, cadastro_df])
        with pd.ExcelWriter('Caminhos da Moda.xlsx', mode="a", engine="openpyxl", if_sheet_exists="replace",) as writer:
            data.to_excel(writer, sheet_name='Lista Produtos',index=False)
            st.write("Produto cadastrado com sucesso!")
   # with bot_2:       
    #    if st.button("Reset"):
    #        pyautogui.hotkey("ctrl","F5")    

#Rotina Venda
def Venda():
    codigox = st.text_input('Qual é o Código?')
    valorreal = st.number_input('Valor Real da Venda:')
    #frete = st.number_input('Valor do frete:')
    pagamento = st.selectbox("Forma de Pagamento:",("Select", "Pix","Crédito","Débito","Dinheiro"),)
    date = datetime.today().strftime('%d-%m-%Y')
    
    #Procura banco de dados
    sheet = pd.read_excel('Caminhos da Moda.xlsx', sheet_name='Lista Produtos')
    df = sheet[sheet['Código'] == codigox]
    row_index = sheet.index[sheet['Código'] == codigox].tolist()
            
    #Contas lucro
    valorpag = df['Valor Pago na peça'].tolist()
    valorpago = np.array(valorpag)
    porcentage = df['Porcetagem Consignação'].tolist()
    porcentagem = np.array(porcentage)
  
    if porcentagem == 0:  
        lucro = valorreal - valorpago
        retorno = 0
    else:
        lucro = valorreal - (((100-porcentagem)*valorreal)/100)
        retorno = valorreal - ((porcentagem)*valorreal)/100
              
    #Faz dataframe
    venda = [[codigox, valorreal, retorno, lucro, pagamento, date]]
    
    venda_df = pd.DataFrame(
        data=venda,
        columns=['Código','Valor real de Venda', 'Valor retorno proprietária', 'Lucro', 'Forma de pagamento','Data'])
    
    dff = df.merge(venda_df, how='left', on='Código')
    
    if st.button("Vendido"):
        df_new = dff.replace("Disponível", "Vendido")
        sheet1 = pd.read_excel('Caminhos da Moda.xlsx', sheet_name='Vendas')
        dado = pd.concat([sheet1, df_new])
        with pd.ExcelWriter('Caminhos da Moda.xlsx', mode="a", engine="openpyxl", if_sheet_exists="replace",) as writer:
            dado.to_excel(writer,sheet_name='Vendas',index=False)
            st.write("Produto atualizado com sucesso!")
            
        dado2 = sheet.drop(sheet.index[row_index])
        with pd.ExcelWriter('Caminhos da Moda.xlsx', mode="a", engine="openpyxl", if_sheet_exists="replace",) as writer:    
            dado2.to_excel(writer,sheet_name='Lista Produtos',index=False)
            
#Menu de opções
with st.sidebar:
    st.title("Opções e Serviços")
    if st.checkbox ("Cadastro"):
        #time.sleep(0.5)
        Cadastro()
    if st.checkbox ("Venda"):
        #time.sleep(0.5)
        Venda()

if st.checkbox ("Visualizar produtos vendidos"):
    sheet2 = pd.read_excel('Caminhos da Moda.xlsx', sheet_name='Vendas')
    sheet2
