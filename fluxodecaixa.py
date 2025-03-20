# -*- coding: utf-8 -*-
"""
Created on Tue Mar 18 13:01:28 2025

@author: Sarah
"""

import streamlit as st
import time
import pandas as pd
from datetime import datetime
#import pyautogui
import gspread
from oauth2client.service_account import ServiceAccountCredentials

#Identificando arquivo do drive e as credenciais
xl = ${{secrets.AAAAAAAAAAAAAAAAAAAAAAAA}}
scope = ['https://www.googleapis.com/auth/spreadsheets', "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials(xl,scope)
client = gspread.authorize(creds)

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
arquivo = client.open('Fluxodecaixa_Caminhosdamoda')
sheet = arquivo.worksheet("Lista Produtos")

data = sheet.get_all_values()
colunas = data.pop(0)
listaprodutos = pd.DataFrame(data,columns=colunas)

arquivo.client.session.close()

#Fazendo filtro
query = st.text_input("Filtro")
if query:
    mask = listaprodutos.applymap(lambda x: query in str(x).upper()).any(axis=1)
    listaprodutos = listaprodutos[mask]

st.data_editor(listaprodutos,hide_index=True,) 
