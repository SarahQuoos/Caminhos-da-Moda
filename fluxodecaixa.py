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
