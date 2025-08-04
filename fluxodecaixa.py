import time
from datetime import datetime
import altair as alt
import gspread
import pandas as pd
import streamlit as st

# Configuração de Página
st.set_page_config(
    page_title="Caminhos da Moda",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={"About": "# Desenvolvido por Sarah Quoos, Curitiba, PR, 2025"},
)

# Título Página
st.title("Fluxo de Caixa Caminhos da Moda")

# Acesso a planilha banco de dados
g_sheets_creds = st.secrets["gsheets"]


@st.cache_resource(ttl=60)
def get_client():
    print(datetime.now(), "Criando cliente gspread")
    client = gspread.service_account_from_dict(
        g_sheets_creds,
        scopes=[
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive.file",
            "https://www.googleapis.com/auth/drive",
        ],
    )
    return client


@st.cache_data(ttl=60)
def get_planilha(planilha):
    arquivo = get_client().open("Fluxodecaixa_Caminhosdamoda")
    sheet = arquivo.worksheet(planilha)
    data = sheet.get_all_values()
    colunas = data.pop(0)
    return pd.DataFrame(data, columns=colunas)


# Rotina Cadastro categoria e geração de código
def pagina_cadastro():
    categoria = st.selectbox(
        label="Categoria:",
        options=[
            "Select",
            "Biquini",
            "Blazer",
            "Blusa",
            "Bolsa",
            "Calça",
            "Camisa",
            "Camiseta",
            "Casaco",
            "Chapéu",
            "Cinto",
            "Colete",
            "Jaqueta",
            "Macacão",
            "Maiô",
            "Outros",
            "Pijama",
            "Saia",
            "Saída de Praia",
            "Sapato",
            "Shorts",
            "TOP",
            "Vestido",
        ],
    )

    # Abrindo arquivos no drive
    arquivo = get_client().open("Fluxodecaixa_Caminhosdamoda")
    sheet1 = arquivo.worksheet("Lista Produtos")
    sheet3 = arquivo.worksheet("Códigos")

    # Pegando código do produto
    cell = sheet3.find(categoria)
    linha = cell.row
    codx = sheet3.cell(linha, 6).value

    # Continuação do cadastro
    with st.form(key="cadastro"):
        status = "Disponivel"
        codigo = st.text_input("Código:", codx)
        proprietario = st.text_input("Proprietária:")
        produto = st.text_input("Descrição do Produto:")
        marca = st.text_input("Marca:")
        numeracao = st.selectbox(
            label="Numeração:",
            options=[
                "Select",
                "ÚNICO",
                "PP",
                "P",
                "M",
                "G",
                "GG",
                "34",
                "35",
                "36",
                "37",
                "38",
                "40",
                "42",
                "44",
                "46",
            ],
        )
        with st.expander("Revenda de peça?"):
            valorpago = st.number_input(label="Valor Pago na peça:", value=0.00)
            valor_sugestao_rev = ((valorpago + 5) * 1.15) * 1.5
            # 0,15(taxas) e 5 (valor fixo despesa)
            lucro_estimado = (valor_sugestao_rev - (valor_sugestao_rev * 0.15)) - (
                valorpago + 5
            )
            st.metric(
                label="Valor Mínimo de Revenda",
                value=f"{'R$ {:,.2f}'.format(valor_sugestao_rev)} ",
            )
            st.metric(
                label="Lucro de Revenda",
                value=f"{'R$ {:,.2f}'.format(lucro_estimado)} ",
            )

        with st.expander("Peça Consignada?"):
            valoretorno = st.number_input("Porcentagem Consignação:")

        with st.expander("Valor Sugerido de Venda:"):
            if valorpago == 0:
                valor_pensado = st.number_input("Valor Ideia de Ganho:", value=0.00)
                valor_pensado_venda = st.number_input(
                    "Valor Ideia de Venda:", value=0.00
                )
                if valor_pensado != 0:
                    valor_sugestao = (valor_pensado + 5) * 1.15
                    st.metric(
                        label="Valor Mínimo de Venda",
                        value=f"{'R$ {:,.2f}'.format(valor_sugestao)} ",
                    )
                else:
                    ganho_estimado = (
                        valor_pensado_venda - (valor_pensado_venda * 0.15)
                    ) - 5
                    st.metric(
                        label="Lucro estimado",
                        value=f"{'R$ {:,.2f}'.format(ganho_estimado)} ",
                    )
        valor = st.number_input("Valor de Venda:")
        date = datetime.today().strftime("%d-%m-%Y")

        # Faz dataframe
        cadastro = [
            status,
            categoria,
            codigo,
            proprietario,
            produto,
            marca,
            numeracao,
            valor,
            valorpago,
            valoretorno,
            date,
        ]

        # Botões de cadastro
        if st.form_submit_button("Cadastrar"):
            if (
                (categoria == "Select")
                or (proprietario == "")
                or (produto == "")
                or (valor == 0)
            ):
                st.write("Preencha todas as informações para cadastro")
            else:
                sheet1.append_row(cadastro)
                st.write("Produto cadastrado com sucesso!")
                # atualizando a página
                time.sleep(1.0)
                st.rerun()


# Rotina Venda
def pagina_venda():
    codigo = st.text_input("Qual é o Código?")
    # Procura código banco de dados
    arquivo = get_client().open("Fluxodecaixa_Caminhosdamoda")
    sheet1 = arquivo.worksheet("Lista Produtos")
    sheet2 = arquivo.worksheet("Vendas")

    # Pegando código do produto
    if codigo == "":
        linha = 0
        data = 0
        valorpago = 0
        porcentagem = 0
    else:
        # Pegando código do produto
        search = sheet1.find(codigo.upper())
        linha = search.row
        data = sheet1.row_values(linha)
        valorpago = sheet1.cell(linha, 8).value
        valorpago = float(valorpago.replace(",", "."))
        porcentagem = sheet1.cell(linha, 10).value
        porcentagem = float(porcentagem)

    with st.form(key="venda"):
        # Restante das informações de venda
        valorreal_aux = st.number_input("Valor Real da Venda:", value=0.00)
        pagamento = st.selectbox(
            label="Forma de Pagamento:",
            options=[
                "Select",
                "Pix Maquininha",
                "Pix CPF",
                "Débito",
                "Dinheiro",
                "Crédito 1x",
                "Crédito 2x",
                "Crédito 3x",
                "Crédito 4x",
                "Crédito 5x",
                "Crédito 6x",
                "Crédito 7x",
                "Crédito 8x",
                "Crédito 9x",
                "Crédito 10x",
            ],
        )
        date = datetime.today().strftime("%d-%m-%Y")
        botao_vendido = st.form_submit_button("Vendido")

        # Aplica taxas maquininha
        if pagamento == "Pix Maquininha":
            taxa = 0.0049
        elif pagamento == "Pix CPF":
            taxa = 0
        elif pagamento == "Débito":
            taxa = 0.0167
        elif pagamento == "Dinheiro":
            taxa = 0
        elif pagamento == "Crédito 1x":
            taxa = 0.0357
        elif pagamento == "Crédito 2x":
            taxa = 0.0779
        elif pagamento == "Crédito 3x":
            taxa = 0.0845
        elif pagamento == "Crédito 4x":
            taxa = 0.0933
        elif pagamento == "Crédito 5x":
            taxa = 0.102
        elif pagamento == "Crédito 6x":
            taxa = 0.1109
        elif pagamento == "Crédito 7x":
            taxa = 0.1189
        elif pagamento == "Crédito 8x":
            taxa = 0.1274
        elif pagamento == "Crédito 9x":
            taxa = 0.1324
        elif pagamento == "Crédito 10x":
            taxa = 0.1349

    # Atualiza planilhas
    if botao_vendido:
        if (codigo == "") or (pagamento == "Select") or (valorreal_aux == 0):
            st.write("Preencha todas as informações para realizar a venda")
        else:
            # Calculo do valor com as taxas
            valorreal = valorreal_aux - (valorreal_aux * taxa)
            # Calculo do valor com as porcentagens de consignação
            if porcentagem == 0:
                retorno = 0
                valorfinal = valorreal
            else:
                retorno = (porcentagem * valorreal_aux) / 100
                valorfinal = valorreal - retorno

            # Faz dataframe
            venda = [
                valorreal_aux,
                pagamento,
                taxa,
                valorreal,
                retorno,
                valorfinal,
                date,
            ]

            # Substitui status e atualiza planilhas
            data[0] = "Vendido"
            venda_new = data + venda
            sheet2.append_row(
                venda_new,
                value_input_option=gspread.utils.ValueInputOption.user_entered,
            )
            time.sleep(0.5)
            sheet1.delete_rows(linha)
            st.write("Produto atualizado com sucesso!")
            time.sleep(1.0)
            # atulizando a pagina
            st.rerun()


# Rotina de cadastro de despesas mensais
def pagina_despesas():
    date = datetime.today().strftime("%d-%m-%Y")
    des = st.text_input("Informe a Descrição da Despesa:")
    valor = st.number_input("Valor da Despesa:")

    # Faz dataframe
    despesa = [date, des, valor]

    # Abrindo arquivo excel
    arquivo = get_client().open("Fluxodecaixa_Caminhosdamoda")
    sheet4 = arquivo.worksheet("Despesas")

    if st.button("Cadastrar", key="cadastrar_despesa"):
        if (des == "") or (valor == 0):
            st.write("Preencha todas as informações para cadastro")
        else:
            sheet4.append_row(despesa)
            st.write("Despesa cadastrada com sucesso!")


# Menu de opções
with st.sidebar:
    st.title("Opções e Serviços")
    if st.checkbox("Cadastro"):
        pagina_cadastro()
    if st.checkbox("Vendas"):
        pagina_venda()
    if st.checkbox("Despesas"):
        pagina_despesas()

# Visualização do Estoque
st.markdown("### Consulta produtos disponíveis")
if st.checkbox(label="Conferir estoque"):
    listaprodutos = get_planilha("Lista Produtos")
    query = st.text_input("Filtro")
    if query:
        mask = listaprodutos.applymap(lambda x: query.upper() in str(x).upper()).any(
            axis=1
        )
        listaprodutos = listaprodutos[mask]
    st.data_editor(
        listaprodutos,
        hide_index=True,
    )

# Visualização de produtos vendidos
st.markdown("### Consulta produtos vendidos")
if st.checkbox("Conferir vendas"):
    listavendas = get_planilha("Vendas")
    query = st.text_input("Conferir vendas")
    if query:
        mask = listavendas.applymap(lambda x: query.upper() in str(x).upper()).any(
            axis=1
        )
        listavendas = listavendas[mask]
    st.data_editor(
        listavendas,
        hide_index=True,
    )


# # Calculo do Lucro
st.markdown("### Consulta Fluxo de Caixa")
if st.checkbox("Conferir Fluxo de Caixa"):
    listadespesas = get_planilha("Despesas")
    listadespesas["Data"] = pd.to_datetime(listadespesas["Data"], dayfirst=True)
    listadespesas["MêsInicio"] = (
        listadespesas["Data"].dt.to_period("M").dt.to_timestamp()
    )
    listadespesas["Mês/Ano"] = (
        listadespesas["MêsInicio"].dt.strftime("%B/%Y").str.capitalize()
    )

    # Definindo mes de visualização
    meses_unicos = (
        listadespesas[["Mês/Ano", "MêsInicio"]]
        .drop_duplicates()
        .sort_values("MêsInicio")
    )
    mes_escolhido = st.selectbox("Selecione o mês:", meses_unicos["Mês/Ano"])

    if st.button("Carregar dados de lucro"):
        # Formatando coluna de data
        listavendas = get_planilha("Vendas")
        listavendas["Data de Venda"] = pd.to_datetime(
            listavendas["Data de Venda"], dayfirst=True
        )
        listavendas["Mês/Ano"] = listavendas["Data de Venda"].dt.strftime("%B/%Y")
        time.sleep(0.5)
        listavendas["Data de Cadastro"] = pd.to_datetime(
            listavendas["Data de Cadastro"], dayfirst=True
        )
        listavendas["Mês/Ano/aux"] = listavendas["Data de Cadastro"].dt.strftime(
            "%B/%Y"
        )
        time.sleep(0.5)

        listaprodutos = get_planilha("Lista Produtos")
        listaprodutos["Data de Cadastro"] = pd.to_datetime(
            listaprodutos["Data de Cadastro"], dayfirst=True
        )
        listaprodutos["Mês/Ano"] = listaprodutos["Data de Cadastro"].dt.strftime(
            "%B/%Y"
        )
        time.sleep(0.5)

        # Filtrando dados
        filtered_pecas = listaprodutos[listaprodutos["Mês/Ano"] == mes_escolhido]
        filtered_pecas["Valor Pago na peça"] = (
            filtered_pecas["Valor Pago na peça"]
            .str.replace(".", "", regex=False)
            .str.replace(",", ".", regex=False)
            .astype(float)
        )
        time.sleep(0.5)
        filtered_vendas = listavendas[listavendas["Mês/Ano"] == mes_escolhido]
        filtered_vendas["Valor Real de Venda"] = (
            filtered_vendas["Valor Real de Venda"]
            .str.replace(".", "", regex=False)
            .str.replace(",", ".", regex=False)
            .astype(float)
        )
        filtered_vendas["Valor Líquido"] = (
            filtered_vendas["Valor Líquido"]
            .str.replace(".", "", regex=False)
            .str.replace(",", ".", regex=False)
            .astype(float)
        )
        time.sleep(0.5)
        filtered_vendas_aux = listavendas[listavendas["Mês/Ano/aux"] == mes_escolhido]
        filtered_vendas_aux["Valor Pago na peça"] = (
            filtered_vendas_aux["Valor Pago na peça"]
            .str.replace(".", "", regex=False)
            .str.replace(",", ".", regex=False)
            .astype(float)
        )
        time.sleep(0.5)
        filtered_despesas = listadespesas[listadespesas["Mês/Ano"] == mes_escolhido]
        filtered_despesas["Valor Despesa"] = (
            filtered_despesas["Valor Despesa"]
            .str.replace(".", "", regex=False)
            .str.replace(",", ".", regex=False)
            .astype(float)
        )

        # Contas
        pecas_estoque_sum = filtered_pecas["Valor Pago na peça"].sum()
        pecas_vendas_sum = filtered_vendas_aux["Valor Pago na peça"].sum()
        pecas_sum = pecas_estoque_sum + pecas_vendas_sum
        vendas_liq_sum = filtered_vendas["Valor Líquido"].sum()
        vendas_bru_sum = filtered_vendas["Valor Real de Venda"].sum()
        despesas_sum = filtered_despesas["Valor Despesa"].sum()
        lucro = vendas_liq_sum - pecas_sum - despesas_sum

        # Visualização
        pecas_sum_formato = (
            f"R${pecas_sum:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        )
        despesas_sum_formato = (
            f"R${despesas_sum:,.2f}".replace(",", "X")
            .replace(".", ",")
            .replace("X", ".")
        )
        vendas_liq_sum_formato = (
            f"R${vendas_liq_sum:,.2f}".replace(",", "X")
            .replace(".", ",")
            .replace("X", ".")
        )
        lucro_formato = (
            f"R${lucro:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        )

        tab1, tab2, tab3, tab4 = st.columns(4)
        tab1.metric(label="Gastos Compra de Peças", value=pecas_sum_formato)
        tab2.metric(label="Despesas Gerais", value=despesas_sum_formato)
        tab3.metric(label="Ganho Líquido Vendas", value=vendas_liq_sum_formato)
        tab4.metric(label="Lucro Líquido Mensal", value=lucro_formato)

        # Gráfico de gastosxganhos e lucro por mes
        listaprodutos["Valor Pago na peça"] = (
            listaprodutos["Valor Pago na peça"]
            .str.replace(".", "", regex=False)
            .str.replace(",", ".", regex=False)
            .astype(float)
        )
        listavendas["Valor Pago na peça"] = (
            listavendas["Valor Pago na peça"]
            .str.replace(".", "", regex=False)
            .str.replace(",", ".", regex=False)
            .astype(float)
        )
        listavendas["Valor Líquido"] = (
            listavendas["Valor Líquido"]
            .str.replace(".", "", regex=False)
            .str.replace(",", ".", regex=False)
            .astype(float)
        )
        listadespesas["Valor Despesa"] = (
            listadespesas["Valor Despesa"]
            .str.replace(".", "", regex=False)
            .str.replace(",", ".", regex=False)
            .astype(float)
        )

        pecas_mensais = (
            listaprodutos.groupby("Mês/Ano")["Valor Pago na peça"].sum().reset_index()
        )
        listavendas["Data de Cadastro"] = pd.to_datetime(
            listavendas["Data de Cadastro"], dayfirst=True
        )
        listavendas["Mês/Ano Cadastro_aux"] = (
            listavendas["Data de Cadastro"].dt.to_period("M").dt.to_timestamp()
        )
        listavendas["Mês/Ano Cadastro"] = listavendas[
            "Mês/Ano Cadastro_aux"
        ].dt.strftime("%B/%Y")
        pecas_mensais_aux = (
            listavendas.groupby("Mês/Ano Cadastro")["Valor Pago na peça"]
            .sum()
            .reset_index()
        )
        ganhos_mensais = (
            listavendas.groupby("Mês/Ano")["Valor Líquido"].sum().reset_index()
        )
        despesas_mensais = (
            listadespesas.groupby("Mês/Ano")["Valor Despesa"].sum().reset_index()
        )

        # Juntando os dados filtrados por mês
        pecas_mensais_aux = pecas_mensais_aux.rename(
            columns={"Mês/Ano Cadastro": "Mês/Ano"}
        )
        pecas_todas = pd.concat([pecas_mensais, pecas_mensais_aux])
        pecas_mensais_total = (
            pecas_todas.groupby("Mês/Ano")["Valor Pago na peça"].sum().reset_index()
        )
        dados_mensal = pd.merge(
            pecas_mensais_total, ganhos_mensais, on="Mês/Ano", how="outer"
        )
        dados_mensal = pd.merge(
            dados_mensal, despesas_mensais, on="Mês/Ano", how="outer"
        )

        # Renomeando dados e colocando 0 no lugar de células vazias
        dados_mensal = dados_mensal.rename(
            columns={
                "Valor Líquido": "Ganhos",
                "Valor Pago na peça": "Gastos com Peças",
                "Valor Despesa": "Despesas",
            }
        )
        dados_mensal = dados_mensal.fillna(0)

        # Calculo do lucro e pegando coluna de data
        dados_mensal["Lucro"] = (
            dados_mensal["Ganhos"]
            - dados_mensal["Gastos com Peças"]
            - dados_mensal["Despesas"]
        )
        dados_mensal["Mês/Ano"] = pd.to_datetime(
            dados_mensal["Mês/Ano"], errors="coerce"
        )
        dados_mensal["Mês/Ano_str"] = dados_mensal["Mês/Ano"].dt.strftime("%b/%Y")

        # Criando barras de ganhos e gastos
        bar = (
            alt.Chart(dados_mensal)
            .transform_fold(
                ["Ganhos", "Gastos com Peças", "Despesas"], as_=["Tipo", "Valor"]
            )
            .mark_bar()
            .encode(
                # x=alt.X('Mês/Ano_str:N', title='Mês'),
                x=alt.X(
                    "Mês/Ano_str:N",
                    title="Mês",
                    sort=list(dados_mensal.sort_values("Mês/Ano")["Mês/Ano_str"]),
                ),
                y=alt.Y("Valor:Q", title="R$"),
                color="Tipo:N",
            )
        )

        # Criando linha do lucro
        # line = alt.Chart(dados_mensal).mark_line(color='black', point=True).encode(x='Mês/Ano_str:N',y='Lucro:Q')
        line = (
            alt.Chart(dados_mensal)
            .mark_line(color="black", point=True)
            .encode(
                x=alt.X(
                    "Mês/Ano_str:N",
                    sort=list(dados_mensal.sort_values("Mês/Ano")["Mês/Ano_str"]),
                ),
                y="Lucro:Q",
            )
        )

        # Criando e montrando o gráfico
        st.markdown("###")
        grafico_final = (bar + line).properties(width=700, height=400)
        st.altair_chart(grafico_final)
