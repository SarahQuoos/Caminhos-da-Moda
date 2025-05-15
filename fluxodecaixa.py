import streamlit as st
import time
import pandas as pd
from datetime import datetime
import gspread

#Acesso a planilha banco de dados
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
arquivo = get_client().open('Fluxodecaixa_Caminhosdamoda')
sheet = arquivo.worksheet("Lista Produtos")
data = sheet.get_all_values()
colunas = data.pop(0)
listaprodutos = pd.DataFrame(data,columns=colunas)

arquivo.client.session.close()

#Rotina Cadastro categoria e geração de código
def Cadastro():
    categoria = st.selectbox("Categoria:",("Select","Biquini","Blazer","Blusa","Bolsa","Calça","Camisa","Camiseta",
                                           "Casaco","Chapéu","Cinto","Colete","Jaqueta","Macacão","Maiô","Outros",
                                           "Pijama","Saia","Saída de Praia","Sapato","Shorts","TOP","Vestido"),)
    
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
        numeracao = st.selectbox("Numeração:",("Select","ÚNICO","PP","P","M","G","GG","34","35","36","37","38","40","42","44","46"),)
        with st.expander("Revenda de peça?"): 
            valorpago = st.number_input('Valor Pago na peça:', value=0.00)
            valor_sugestao = (((valorpago*1.5)+5)*1.05)
            st.metric(label="Valor Sugestão de Venda", value=f"{'R$ {:,.2f}'.format(valor_sugestao)} ",)
        with st.expander("Peça Consignada?"):
            valoretorno = st.number_input('Porcentagem Consignação:')
        valor = st.number_input('Valor de Venda:')
        date = datetime.today().strftime('%d-%m-%Y')
        
        #Faz dataframe
        cadastro = [status, categoria, codigo, proprietario, produto, marca, numeracao, valor, valorpago, valoretorno,date]
        
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
        valorreal_aux = st.number_input('Valor Real da Venda:', value=valorpago)
        pagamento = st.selectbox("Forma de Pagamento:",("Select", "Pix Maquininha","Pix CPF", "Crédito","Débito","Dinheiro"),)
        date = datetime.today().strftime('%d-%m-%Y')
        botao_vendido = st.form_submit_button('Vendido')

        #Aplica taxas maquininha
        if pagamento == "Crédito":
            taxa = 0.0498
        elif pagamento == "Débito":
            taxa = 0.0199
        elif pagamento == "Pix Maquininha":
            taxa = 0.0049
        elif pagamento == "Pix CPF":
            taxa = 0
            
    #Atualiza planilhas
    if botao_vendido:
        if (codigo == "") or (pagamento == "Select") or (valorreal_aux == 0):
            st.write("Preencha todas as informações para realizar a venda")
        else:   
            #Calculo do valor com as taxas
            valorreal = valorreal_aux - (valorreal_aux*taxa)
            #Calculo do valor com as porcentagens de consignação
            if porcentagem == 0:
                valorfinal = valorreal
                retorno = 0
            else:
                valorfinal = valorreal - (((100-porcentagem)*valorreal)/100)
                retorno = valorreal - ((porcentagem)*valorreal)/100
                
            #Faz dataframe
            venda = [valorreal_aux, pagamento, taxa, valorreal, retorno, valorfinal, date]

            #Substitui status e atualiza planilhas
            data[0] = "Vendido"
            venda_new = data + venda
            sheet2.append_row(venda_new, value_input_option=gspread.utils.ValueInputOption.user_entered)
            time.sleep(0.5)
            sheet1.delete_rows(linha)
            time.sleep(0.5)
            st.write("Produto atualizado com sucesso!")
            #atulizando a pagina
            st.rerun()

#Rotina de cadastro de despesas mensais
def Despesas():
    date = datetime.today().strftime('%d-%m-%Y')
    des = st.text_input('Informe a Descrição da Despesa:')
    valor = st.number_input('Valor da Despesa:')
    
    #Faz dataframe
    despesa = [date, des, valor]
    
    #Abrindo arquivo excel
    arquivo = get_client().open('Fluxodecaixa_Caminhosdamoda')
    sheet4 = arquivo.worksheet("Despesas")
    
    if st.button("Cadastrar", key='cadastrar_despesa'):
        if (des == "") or (valor == 0):
            st.write("Preencha todas as informações para cadastro")
        else:
            sheet4.append_row(despesa)
            st.write("Despesa cadastrada com sucesso!")

#Rotina do Modo Feira
def Modofeira():
    arquivo = get_client().open('Fluxodecaixa_Caminhosdamoda')
    sheet6 = arquivo.worksheet("Modo Feira")

    with st.form(key='Modo Feira'):
        with st.expander("Item 1"):
            codigo1 = st.text_input('Código Peça 1:')
            valor1 = st.number_input('Valor Peça 1:', value=0.00)  
        with st.expander("Item 2"):
            codigo2 = st.text_input('Código Peça 2:')
            valor2 = st.number_input('Valor Peça 2:', value=0.00)  
        with st.expander("Item 3"):
            codigo3 = st.text_input('Código Peça 3:')
            valor3 = st.number_input('Valor Peça 3:', value=0.00)
        with st.expander("Item 4"):
            codigo4 = st.text_input('Código Peça 4:')
            valor4 = st.number_input('Valor Peça 4:', value=0.00)
        with st.expander("Item 5"):
            codigo5 = st.text_input('Código Peça 5:')
            valor5 = st.number_input('Valor Peça 5:', value=0.00)  
        valor_final_aux = valor1 + valor2 + valor3 + valor4 + valor5
        valor_final = st.number_input('Valor Total da Venda:', value=valor_final_aux)
        pagamento = st.selectbox("Forma de Pagamento:",("Select", "Pix Maquininha","Pix CPF", "Crédito","Débito","Dinheiro"),)
        botao_feira = st.form_submit_button('Venda Feira')
    if botao_feira:
        if (pagamento == "Select") or (valor_final == 0):
            st.write("Preencha todas as informações!")
        else:
            cadastro_feira = [codigo1, codigo2, codigo3, codigo4, codigo5, pagamento, valor_final]
            sheet6.append_row(cadastro_feira)
            st.write("Produto cadastrado com sucesso!")
            #atualizando a página
            time.sleep(1.0)
            st.rerun()

#Menu de opções
with st.sidebar:
    st.title("Opções e Serviços")
    if st.checkbox ("Cadastro"):
        Cadastro()
    if st.checkbox ("Vendas"):
        Venda()
    if st.checkbox ("Despesas"):
        Despesas()
    if st.checkbox ("Modo Feira"):
        Modofeira()
        
#Visualização do Estoque
with st.expander("Conferir estoque"):
    query = st.text_input("Filtro")
    if query:
        mask = listaprodutos.applymap(lambda x: query.upper() in str(x).upper()).any(axis=1)
        listaprodutos = listaprodutos[mask]
    st.data_editor(listaprodutos,hide_index=True,) 

#Visualização de produtos vendidos
st.markdown("### Consulta produtos vendidos")
sheet2 = arquivo.worksheet("Vendas")
data2 = sheet2.get_all_values()
colunas2 = data2.pop(0)
listavendas = pd.DataFrame(data2,columns=colunas2)
with st.expander("Conferir vendas"):
    if st.button("Carregar dados de vendas"):
        query = st.text_input("Conferir vendas")
        if query:
            mask = listavendas.applymap(lambda x: query.upper() in str(x).upper()).any(axis=1)
            listavendas = listavendas[mask]
        st.data_editor(listavendas,hide_index=True,) 

sheet3 = arquivo.worksheet("Despesas")
data3 = sheet3.get_all_values()
colunas3 = data3.pop(0)
listadespesas = pd.DataFrame(data3,columns=colunas3)

#Calculo do Lucro
st.markdown("### Consulta Lucro Mensal")
with st.expander("Conferir Lucro Mensal"):
    #listaprodutos['Data de Cadastro'] = pd.to_datetime(listaprodutos['Data de Cadastro'], dayfirst=True)
    #listaprodutos['MêsInicio'] = listaprodutos['Data de Cadastro'].dt.to_period('M').dt.to_timestamp()
    #listaprodutos['Mês/Ano'] = listaprodutos['MêsInicio'].dt.strftime('%B/%Y').str.capitalize()
    #Definindo mes de visualização
    #meses_unicos = listaprodutos[['Mês/Ano', 'MêsInicio']].drop_duplicates().sort_values('MêsInicio')
    #mes_escolhido = st.selectbox("Selecione o mês:", meses_unicos['Mês/Ano'])
    
    listadespesas['Data'] = pd.to_datetime(listadespesas['Data'], dayfirst=True)
    listadespesas['MêsInicio'] = listadespesas['Data'].dt.to_period('M').dt.to_timestamp()
    listadespesas['Mês/Ano'] = listadespesas['MêsInicio'].dt.strftime('%B/%Y').str.capitalize()
    #Definindo mes de visualização
    meses_unicos = listadespesas[['Mês/Ano', 'MêsInicio']].drop_duplicates().sort_values('MêsInicio')
    mes_escolhido = st.selectbox("Selecione o mês:", meses_unicos['Mês/Ano'])
    
    #listadespesas['Data'] = pd.to_datetime(listadespesas['Data'], dayfirst=True)
    #listadespesas['Mês/Ano'] = listadespesas['Data'].dt.strftime('%B/%Y')
    #time.sleep(0.5)
    #Definindo mes de visualização
    #meses_disponiveis = listadespesas['Mês/Ano'].unique()
    #mes_escolhido = st.selectbox("Selecione o mês:", sorted(meses_disponiveis))
  
    if st.button("Carregar dados de lucro"):
        #Formatando coluna de data
        listavendas['Data de Venda'] = pd.to_datetime(listavendas['Data de Venda'], dayfirst=True)
        listavendas['Mês/Ano'] = listavendas['Data de Venda'].dt.strftime('%B/%Y')
        time.sleep(0.5)
        listaprodutos['Data de Cadastro'] = pd.to_datetime(listaprodutos['Data de Cadastro'], dayfirst=True)
        listaprodutos['Mês/Ano'] = listaprodutos['Data de Cadastro'].dt.strftime('%B/%Y')
        time.sleep(0.5)

        #Filtrando dados
        filtered_pecas = listaprodutos[listaprodutos['Mês/Ano'] == mes_escolhido]
        filtered_pecas['Valor Pago na peça'] = filtered_pecas['Valor Pago na peça'].str.replace(',', '.').astype(float)
        time.sleep(0.5)
        filtered_vendas = listavendas[listavendas['Mês/Ano'] == mes_escolhido]
        filtered_vendas['Valor Real de Venda'] = filtered_vendas['Valor Real de Venda'].str.replace(',', '.').astype(float)
        filtered_vendas['Valor Líquido'] = filtered_vendas['Valor Líquido'].str.replace(',', '.').astype(float)
        time.sleep(0.5)
        filtered_despesas = listadespesas[listadespesas['Mês/Ano'] == mes_escolhido]
        filtered_despesas['Valor Despesa'] = pd.to_numeric(filtered_despesas['Valor Despesa'], errors='ignore')
        #filtered_despesas['Valor Despesa'] = filtered_despesas['Valor Despesa'].str.replace(',', '.').astype(float)
        
        #Contas
        pecas_sum = filtered_pecas['Valor Pago na peça'].sum()
        vendas_liq_sum = filtered_vendas['Valor Líquido'].sum()
        vendas_bru_sum = filtered_vendas['Valor Real de Venda'].sum()
        despesas_sum = filtered_despesas['Valor Despesa'].sum()
        lucro = vendas_liq_sum - pecas_sum - despesas_sum
        
        #Visualização
        st.markdown("###") 

        pecas_sum_formato = f"R${pecas_sum:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        despesas_sum_formato = f"R${despesas_sum:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        vendas_bru_sum_formato = f"R${vendas_bru_sum:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        lucro_formato = f"R${lucro:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        
        tab1, tab2, tab3, tab4 = st.columns(4)
        tab1.metric(label="Gastos Compra de Peças", value=pecas_sum_formato)
        tab2.metric(label="Despesas Gerais", value=despesas_sum_formato)
        tab3.metric(label="Ganho Bruto Vendas", value=vendas_bru_sum_formato)
        tab4.metric(label="Lucro Líquido Mensal", value=lucro_formato)
