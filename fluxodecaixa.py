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
    categoria = st.selectbox("Categoria:",("Select", "Biquini","Blazer","Blusa","Bolsa","Calça", "Camisa","Camiseta",
                                           "Casaco","Chapéu","Cinto","Colete", "Jaqueta","Macacão","Maiô", "Outros",
                                           "Pijama","Saia","Saída de Praia","Shorts","TOP", "Vestido"),)
    
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
        numeracao = st.selectbox("Numeração:",("Select","ÚNICO","PP","P","M","G","GG","36","38","40","42","44","46"),)
        with st.expander("Revenda de peça?"): 
            valorpago = st.number_input('Valor Pago na peça:', value=0.00)
            valor_sugestao = ((valorpago*1.5)*1.05)+5
            st.metric(label="Valor Sugestão de Venda", value=f"{'R$ {:,.2f}'.format(valor_sugestao)} ",)
        with st.expander("Peça Consignada?"):
            valoretorno = st.number_input('Porcentagem Consignação:')
        valor = st.number_input('Valor de Venda:')
        date = datetime.today().strftime('%d-%m-%Y')

        #Sugestão valor de venda
        #if valorpago != 0:
        #    valor_sugestao = ((valorpago*1.5)*1.05)+5
        #    st.metric(label="Valor Sugestão de Venda", value=f"{'R$ {:,.2f}'.format(valor_sugestao)} ",)
            
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
    query = st.text_input("Conferir vendas")
    if query:
        mask = listavendas.applymap(lambda x: query.upper() in str(x).upper()).any(axis=1)
        listavendas = listavendas[mask]
    st.data_editor(listavendas,hide_index=True,) 

#Visualização de Despesas
st.markdown("### Consulta das despesas")
sheet4 = arquivo.worksheet("Despesas")
data4 = sheet4.get_all_values()
colunas4 = data4.pop(0)
listadespesas = pd.DataFrame(data4,columns=colunas4)    
with st.expander("Conferir Despesas"):
    st.write(listadespesas)
