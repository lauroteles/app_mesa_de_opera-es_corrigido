
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf
import io
import openpyxl as op
import xlsxwriter
from xlsxwriter import Workbook
import base64
from io import BytesIO
import io
import xlsxwriter as xlsxwriter
import datetime
import time



t0 = time.perf_counter()

st.set_page_config(layout='wide')

paginas = 'Home','Carteiras','Produtos','Divisão de operadores','Analitico','Análise Tecnica'
selecionar = st.sidebar.radio('Selecione uma opção', paginas)


#---------------------------------- 
# Variaveis globais
@st.cache_data(ttl="2m")
     
def le_excel(x):
    df = pd.read_excel(x)
    return df
pl_original = le_excel('PL Total.xlsx')
controle_original = le_excel('controle.xlsx')
saldo_original = le_excel('Saldo.xlsx')
posicao_original = le_excel('Posição.xlsx')
produtos_original = le_excel('Produtos.xlsx')
cura_original = le_excel('Curva_comdinheiro.xlsx')
curva_de_inflacao = le_excel('Curva_inflação.xlsx')

pl = pl_original.copy()
controle = controle_original.copy()
saldo = saldo_original.copy()
arquivo1 = posicao_original.copy()
produtos = produtos_original.copy()
curva_base = cura_original.copy()
curva_inflacao_copia = curva_de_inflacao.copy()


#----------------------------------  ---------------------------------- ---------------------------------- ---------------------------------- 
# Pagina de Carteiras
#---------------------------------- ---------------------------------- ---------------------------------- ---------------------------------- 


#--------------------- EQUITIES
     

equities = {'ARZZ3': 4.5,
            'ASAI3':5.75,
            'CSAN3':6,
            'CSED3':5,
            'EGIE3':4.5,
            'EQTL3':6,
            'EZTC3':5.75,
            'HYPE3':6.50,
            'KEPL3':6.50,
            'MULT3':5,
            'PRIO3':8,
            'PSSA3':5.50,
            'SBSP3':4.50,
            'SLCE3':6.50,
            'VALE3':10,
            'Caixa':10
            }
equities_graf= pd.DataFrame(list(equities.items()),columns=['Ativo','Proporção'])
equities_graf['Proporção'] =equities_graf['Proporção']/100

     
    #--------------------- iNCOME
   

income = {
    'POS':15,
    'Inflação':38,
    'PRE':44,
    'FundoDI':3
    }

small_caps = {
    'BPAC11':10,
    'ENEV3':4,
    'HBSA3':7,
    'IFCM3':5,
    'JALL3':10,
    'KEPL3':12,
    'MYPK3':5,
    'PRIO3':12,
    'SIMH3':8,
    'TASA4':8,
    'TUPY3':11,
    'WIZC3':5,
}
fii = {
    'BTLG11':22.30,
    'Caixa':6,
    'HGLG11':22.30,
    'KNCA11':7.25,
   ' MALL11':7.75,
   ' PLCR11':13.57,
    'RURA11':7.26,
    'TRXF11':13.57
}

dividendos = {
    'TAEE11':9,
   ' VIVT3':12,
    'BBSE3':17,
    'ABCB4':16,
   ' VBBR3':15,
   ' CPLE6':16,
   ' TRPL4':5
    }

small_caps_dataframe = pd.DataFrame(list(small_caps.items()),columns=['Ativo','Proporção'])
small_caps_dataframe['Proporção'] = small_caps_dataframe['Proporção']/100    
    #---------------------- Small caps

dividendos_dataframe = pd.DataFrame(list(dividendos.items()),columns=['Ativo','Proporção'])
dividendos_dataframe['Proporção'] = dividendos_dataframe['Proporção']/100
        #---------------------- Dividendos

fii_dataframe = pd.DataFrame(list(fii.items()),columns=['Ativo','Proporção'])
fii_dataframe['Proporção'] = fii_dataframe['Proporção']/100 
    #---------------------- FII

income_graf = pd.DataFrame(list(income.items()),columns=['Ativo','Proporção'])
income_graf['Proporção'] = income_graf['Proporção']/100
    
    #---------------------- Moderada
moderada = {ativo:0.75*income.get(ativo,0)+0.25*equities.get(ativo,0) for ativo in set(income)|set(equities)}
moderada_grafico = pd.DataFrame(list(moderada.items()),columns=['Ativo','Proporção'])
moderada_grafico['Proporção'] = moderada_grafico['Proporção']/100

   
    #-------------------- Arrojada     
arrojada = {ativo:0.60*income.get(ativo,0)+0.40*equities.get(ativo,0) for ativo in set(income)|set(equities)}   
arrojada_graf = pd.DataFrame(list(arrojada.items()),columns=['Ativo','Proporção'])
arrojada_graf['Proporção'] = arrojada_graf['Proporção']/100
 
    #------------------ Conservadora
   
conservadora = {ativo:0.87*income.get(ativo,0)+0.13*equities.get(ativo,0) for ativo in set(income)|set(equities)}   
conservadora_graf = pd.DataFrame(list(conservadora.items()),columns=['Ativo','Proporção'])
conservadora_graf['Proporção'] = conservadora_graf['Proporção']/100


if selecionar == 'Carteiras':


    #--------------------------------
    # --------Manipulação de arquivos
   

    arquivo2 = arquivo1.groupby(['CONTA','PRODUTO','ATIVO'])[['VALOR BRUTO','VALOR LÍQUIDO','QUANTIDADE']].sum().reset_index('CONTA')

    # Sidebar

    input_text = st.sidebar.text_input('Escreva o número conta')

    #---------------
    
    novo_arq = arquivo2.loc[arquivo2['CONTA']  == input_text]
    cont_df = controle.loc[controle['Unnamed: 2'] == input_text]


    #----------------

    novo_arq = novo_arq.groupby(['PRODUTO','CONTA'])[['VALOR LÍQUIDO','QUANTIDADE']].sum().reset_index()
    controle = controle.iloc[:,[1,2,3,4,5,7,8,9,12,16,17,18]]
    
    

    #------------- Manipulando arquivos para unir planilhas

    controle['Unnamed: 2'] = controle['Unnamed: 2'].astype(str)
    controle['Unnamed: 2'] = list(map(lambda x: '00' + x,controle['Unnamed: 2']))
    try:
                
        novo_controle = pd.merge(controle,novo_arq, left_on='Unnamed: 2',right_on='CONTA', how= 'outer' )
        nov_controle = controle.loc[controle['Unnamed: 2'] == input_text ]
        
        #--------------- somando PL da carteira


        qtd_ativos = novo_arq.groupby('CONTA')['QUANTIDADE'].sum().reset_index()
        pl_por_produtos = novo_arq.groupby('CONTA')['VALOR LÍQUIDO'].sum().reset_index()

        valor_liquido = pl_por_produtos.loc[0,'VALOR LÍQUIDO']

        novo_arq['Basket'] = novo_arq['QUANTIDADE']/novo_arq['VALOR LÍQUIDO']
        



        #------------------ Selecionando qual tipo de carteira

        if 'Unnamed: 12' in nov_controle.columns:
            valor_coluna = nov_controle['Unnamed: 12'].iloc[0]
        if valor_coluna == 'CON':
            moderada_graf = conservadora_graf
        elif valor_coluna == 'ARR':
            moderada_graf = arrojada_graf
        elif valor_coluna =='MOD':
            moderada_graf = moderada_grafico
        elif valor_coluna == 'INC':
            moderada_graf = income_graf
        elif valor_coluna == 'EQT':
            moderada_graf = equities_graf 
        elif valor_coluna == 'SMLL':
            moderada_graf = small_caps_dataframe                  
        elif valor_coluna == 'FII':
            moderada_graf = fii_dataframe   
        elif valor_coluna == 'DIV':
            moderada_graf = dividendos_dataframe   
        else:
            st.success('Essa carteira e exeção')

        
        st.text('Valor total da carteira')
        st.title(f'{valor_liquido:,.2f}')
        

        moderada_graf['Valor Distribuido'] = moderada_graf['Proporção']*valor_liquido





        #-----------------acertando valores em ordem e retirando colunas
        lista_acoes_sem_caixa = ['ARZZ3',
            'ASAI3',
            'CSAN3',
            'CSED3',
            'EGIE3',
            'EQTL3',
            'EZTC3',
            'HYPE3',
            'KEPL3',
            'MULT3',
            'PRIO3',
            'PSSA3',
            'SBSP3',
            'SLCE3',
            'VALE3']

        distribuicao_alvo = moderada_graf[['Ativo','Valor Distribuido']].reset_index()
        distribuicao_alvo['Ativo']=distribuicao_alvo['Ativo'].str.upper()
        distribuicao_alvo = distribuicao_alvo.sort_values(by='Ativo')
        distribuicao_alvo = distribuicao_alvo.drop(columns='index')

        novo_arq = novo_arq.sort_values(by='PRODUTO')
        novo_arq = novo_arq.drop(columns='CONTA')
        arquivo_basket = pd.merge(distribuicao_alvo,novo_arq, left_on='Ativo',right_on='PRODUTO',how='outer')
        arquivo_basket['Quantidade Ideal'] = arquivo_basket['Basket']*arquivo_basket['Valor Distribuido']
        arquivo_basket = arquivo_basket[['Ativo', 'Valor Distribuido','Quantidade Ideal']]

        precos_de_mercado = {}
        for ativo in lista_acoes_sem_caixa:
            ticker = yf.Ticker(ativo +'.SA')
            preco_atual = ticker.history(period='2m')['Close'].iloc[-1]
        
            precos_de_mercado[ativo] = preco_atual

        arquivo_basket['Preco_de_mercado'] = ''
        arquivo_basket['Preco_de_mercado'] = arquivo_basket['Ativo'].map(precos_de_mercado)
        arquivo_basket['Quantidade Ideal' ]= arquivo_basket['Valor Distribuido']/arquivo_basket['Preco_de_mercado'] 



        #-------------------filtrando RV x RF

        lista_acoes = ['ARZZ3','ARZZ',
            'ASAI3',
            'CSAN3',
            'CSED3',
            'EGIE3',
            'EQTL3',
            'EZTC3',
            'HYPE3',
            'KEPL3',
            'MULT3',
            'PRIO3',
            'PSSA3',
            'SBSP3',
            'SLCE3',
            'VALE3',
            'Caixa']

        filtro_rv = novo_arq[novo_arq['PRODUTO'].isin(lista_acoes)].reset_index()
        filtro_rf = novo_arq[~novo_arq['PRODUTO'].isin(lista_acoes)].reset_index()

        filtro_rv_BASE = moderada_graf[moderada_graf['Ativo'].isin(lista_acoes)].reset_index()
        
        filtro_rf_BASE = moderada_graf[~moderada_graf['Ativo'].isin(lista_acoes)].reset_index()

        base_df_rf = arquivo_basket[arquivo_basket['Ativo'].isin(lista_acoes)].reset_index()
        base_df_rv = arquivo_basket[~arquivo_basket['Ativo'].isin(lista_acoes)].reset_index()

        filtro_total_rvrf = novo_arq[novo_arq['PRODUTO'].isin(lista_acoes)].sum().reset_index()
        analise_rvrf = novo_arq[~novo_arq['PRODUTO'].isin(lista_acoes)].sum().reset_index()


        st.markdown("<br>",unsafe_allow_html=True)
        st.markdown("<br>",unsafe_allow_html=True)
        mostrar_rv = st.toggle('Mostrar apenas renda variavel')
        mostrar_rf = st.toggle('Mostrar apenas renda fixa')
        st.markdown("<br>",unsafe_allow_html=True)


        
        if mostrar_rv and mostrar_rf:
            novo_arq = novo_arq
            moderada_graf = moderada_graf
            arquivo_basket = arquivo_basket

        elif mostrar_rv:
            novo_arq = filtro_rv
            moderada_graf =filtro_rv_BASE
            arquivo_basket = base_df_rf

        elif mostrar_rf:
            novo_arq = filtro_rf
            moderada_graf = filtro_rf_BASE
            arquivo_basket = base_df_rv
        else:
            novo_arq = novo_arq
            moderada_graf = moderada_graf
            arquivo_basket = arquivo_basket            


        #---------------------------
        #        Graficos

        

        graf1 = go.Figure(data=[go.Pie(labels=novo_arq['PRODUTO'],
                                        values=novo_arq['VALOR LÍQUIDO'],
                                        hole=0.4,
                                        textinfo='label+percent',
                                        insidetextorientation='radial',
                                        textposition='outside'
                                        )])


        figas=px.pie(moderada_graf,values='Proporção',labels='Ativo')

        graf_moderada = go.Figure(data=[go.Pie(labels=moderada_graf['Ativo'], values=moderada_graf['Proporção'],
                                                            hole=0.4,
                                        textinfo='label+percent',
                                        insidetextorientation='radial',
                                        textposition='outside'
                                        )])
        graf1.update_layout(title='Posição atual da carteira')
        graf_moderada.update_layout(title = 'Carteira balanceada')



        nov_controle = nov_controle.rename(columns={
            'Unnamed: 1':'Nome do cliente',
            'Unnamed: 2':'Conta',
                'Unnamed: 3':'Escritorio',
                'Unnamed: 4':'Estado',
                    'Unnamed: 5':'Assessor',
        'Backoffice/ Mesa':'Status',
            'Mesa de Operação.1':'Situação',
            'Backoffice.1':'Exeção',
            'Unnamed: 12':'Perfil',
        'Mesa de Operação.2':'Lembretes mesa',
            'Gestão/ Head comercial':'Observações',
            'Backoffice ':'Observações'
        })
        nov_controle = nov_controle.unstack()
        
        # -------------- Criando arquivo para Basket
        
        basket = pd.merge(arquivo_basket,novo_arq,left_on='Ativo',right_on='PRODUTO',how='inner').reset_index()
        
        precos_mercado = {}

        basket['Basket_BTG'] = basket['Quantidade Ideal']-basket['QUANTIDADE']
        basket = basket[[
            'Ativo',  'Basket_BTG']]
        basket['C/V'] = np.where(basket['Basket_BTG']<0,'V','C')
        basket['Basket_BTG'] = basket['Basket_BTG'].fillna(0)
        basket['Basket_BTG'] = np.where(basket['Basket_BTG']<0,basket['Basket_BTG'].astype(int).astype(str).str[1:],basket['Basket_BTG'])
        basket['Conta'] = input_text
        basket['Validade'] = 'DIA'
        basket['Basket_BTG'] =basket['Basket_BTG'].astype(int)
        
        for ativo in basket['Ativo']:
            ticker = yf.Ticker(ativo +'.SA')
            preco_atual = ticker.history(period='5m')['Close'].iloc[-1]

            precos_mercado[ativo] = preco_atual
        basket['Preço'] = ''
        basket['Preço'] = basket['Ativo'].map(precos_mercado)

        basket= basket.rename(columns={
            'Basket_BTG':'Quantidade',
        })
        basket = basket [['Ativo','C/V','Quantidade','Preço','Conta','Validade']]

        data_e_hora = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M')
        nome_arquivo = f'{data_e_hora}_{input_text}.xlsx'

        if basket is not None:
            
            
            # Use io.BytesIO para criar um buffer de bytes
            output4 = io.BytesIO()
            # Salve o DataFrame no buffer no formato XLSX
            with pd.ExcelWriter(output4, engine='xlsxwriter') as writer:
                basket.to_excel(writer,
                                            sheet_name='Basket',
                                                index=False)
            
            # Crie um link para download
            output4.seek(0)
            st.download_button(type='primary',
                label="Basket Download",
                data=output4,
                file_name=nome_arquivo,
                key='download_button')
        

        #---------------------------------------------------
        #---------------------- Ajustando graficos e tabelas
        
        novo_arq = novo_arq[['PRODUTO', 'VALOR LÍQUIDO', 'QUANTIDADE']]
        novo_arq.rename(columns={
            'Produto':'Ativo',
            'VALOR LÍQUIDO':'Valor em R$',
            'QUANTIDADE':'Quantidade do ativo'
        },inplace=True)
        arquivo_basket.rename(columns={
            'Valor Distribuido':'Valor em R$',
            'Quantidade Ideal':'Quantidade do ativo',
            'Preco_de_mercado':'Cotação atual'
        },inplace=True)
        print(arquivo_basket.info())
        arquivo_basket['Quantidade do ativo'] = arquivo_basket['Quantidade do ativo'].fillna(0)
        arquivo_basket['Quantidade do ativo'] = arquivo_basket['Quantidade do ativo'].round(0).astype(int)


        somatario_basket = basket.copy()
        compra = somatario_basket[somatario_basket['C/V']=='C']
        compra['valor'] = compra['Quantidade']*compra['Preço']
    
        

        venda = somatario_basket[somatario_basket['C/V']=='V']
        venda['valor'] = venda['Quantidade']*venda['Preço']

        #----------------------------------------------
        #---------------------- Streamlit visualization



        col1, col2 = st.columns(2)

        # -------------Coluna 1

        with col1: 
            st.subheader('Proporção da carteira')
            st.plotly_chart(graf1,use_container_width= True)
            st.dataframe(novo_arq,use_container_width=True)
            with col1: ''
            with col1: ''
            st.subheader('Informações do cliente')
            st.dataframe(nov_controle,use_container_width=True)
            with col1:''
            st.subheader('Basket')
            try:
                st.warning(f' O saldo gerado pelas vendas  : {venda["valor"].sum():,.2f}')
            except:
                pass
            try:
                st.warning(f' O saldo Nescessario para compra : {compra["valor"].sum():,.2f}')          
            except:
                pass
            st.dataframe(basket,use_container_width=True)

            # --------------Coluna 2

        with col2: st.subheader('Proporção ideal')
        with col2: st.plotly_chart(graf_moderada,use_container_width=True)
        with col2: st.dataframe(arquivo_basket,use_container_width=True)


        #3 --------------- ROW

    except:
          st.header('Digite uma conta valida')



#----------------------------------  ---------------------------------- ---------------------------------- ---------------------------------- 
# Pagina de produtos
#---------------------------------- ---------------------------------- ---------------------------------- ---------------------------------- 

if selecionar == 'Produtos':

    produtos = pd.read_excel('Produtos.xlsx')
    produtos = produtos[[
       'PRODUTO', 'PRAZO/VENCIMENTO', 'TAXA','TAXA EQ. CDB']]
    
    produtos['PRODUTO'] = produtos['PRODUTO'].fillna(0)
    produtos = produtos[produtos['PRODUTO'] !=0]


    #----------------------------------
    # Seleção para filtragem de produtos

    bancos_que_podem_ser_utilizados = [
'Banco ABC',
'Banco Agibak',
'Banco Alfa',
'Banco BBC S.A',
'Banco BMG',
'Banco Bocom',
'Banco Bradesco',
'Banco BS2',
'Banco BTG Pactual',
'Banco C6 Consignado',
'Banco da China',
'Banco Daycoval',
'Banco de Brasilia',
'Banco Digimais',
'Banco do Brasil',
'Banco Factor',
'Banco Fibra',
'Banco Fidis',
'Banco Haitong',
'Banco ICBC',
'Banco Industrial',
'Banco Inter',
'Banco Itau',
'Banco Master',
'Banco Mercantil',
'Banco NBC',
'Banco Original',
'Banco Ourinvest',
'Banco Paulista',
'Banco Pine',
'Banco Randon',
'Banco Rendimento',
'Banco Rodobens',
'Banco Safra',
'Banco Santander',
'Banco Semear',
'Banco Sicoob',
'Banco Topazio',
'Banco Triangulo',
'Banco Volkswagen',
'Banco Votorantim',
'Banco XCMG',
'Banco Br Partners',
'Caixa econômica',
'Banco Caruana',
'Banco Citibank',
'Banco CNH Capital',
'Banco Omni CFI',
'Banco Paraná Banco',
'Banco RaboBank',
'Banco Sicred',
'Banco Via Certa']



    radio = ['CDB','LCA','LCI','LC','Inflação','Inflação Implícita']
    lc =st.sidebar.radio('selecione o tipo de produto',radio)
    

    if lc =='CDB':
        pre_pos =st.radio('',['PRÉ','PÓS'])
        produtos = produtos[(produtos['PRODUTO'].str.slice(0,3) == 'CDB')&(produtos['TAXA'].str.slice(0,4) != 'IPCA')&(produtos['TAXA'].str.slice(0,3) != 'CDI')]
        if pre_pos == 'PRÉ':
            produtos = produtos[produtos['PRODUTO'].str.slice(0,9) == 'CDB - PRÉ']
        elif pre_pos == 'PÓS':
           produtos=produtos[produtos['PRODUTO'].str.slice(0,9) == 'CDB - PÓS']  

    elif lc == 'LCI':
        pre_pos =st.radio('',['PRÉ','PÓS'])
        produtos = produtos[(produtos['PRODUTO'].str.slice(0,3) == 'LCI')&(produtos['TAXA'].str.slice(0,4) != 'IPCA')&(produtos['TAXA'].str.slice(0,3) != 'CDI')]
        if pre_pos == 'PRÉ':
            produtos = produtos[produtos['PRODUTO'].str.slice(0,9) == 'LCI - PRÉ']
        elif pre_pos == 'PÓS':
           produtos=produtos[produtos['PRODUTO'].str.slice(0,9) == 'LCI - PÓS']  
    
    elif lc == 'LC':
        pre_pos =st.radio('',['PRÉ','PÓS'])
        produtos = produtos[(produtos['PRODUTO'].str.slice(0,2) == 'LC')&(produtos['TAXA'].str.slice(0,4) != 'IPCA')&(produtos['TAXA'].str.slice(0,3) != 'CDI')]
        if pre_pos == 'PRÉ':
            produtos = produtos[produtos['PRODUTO'].str.slice(0,9) == 'LC - PRÉ']
        elif pre_pos == 'PÓS':
           produtos=produtos[produtos['PRODUTO'].str.slice(0,9) == 'LC - PÓS']          
    
    elif lc == 'LCA':
        pre_pos =st.radio('',['PRÉ','PÓS'])
        produtos = produtos[(produtos['PRODUTO'].str.slice(0,3) == 'LCA')&(produtos['TAXA'].str.slice(0,4) != 'IPCA')&(produtos['TAXA'].str.slice(0,3) != 'CDI')]
        if pre_pos == 'PRÉ':
            produtos = produtos[produtos['PRODUTO'].str.slice(0,9) == 'LCA - PRÉ']
        elif pre_pos == 'PÓS':
           produtos=produtos[produtos['PRODUTO'].str.slice(0,9) == 'LCA - PÓS']


    elif lc =='Inflação':
        produtos = produtos[produtos['PRODUTO'].str.slice(17,23) =='ÍNDICE']
        if lc=='Inflação':
            cdi_ipca = st.radio('',['CDI','IPCA'])
            if cdi_ipca == 'CDI':
                produtos=produtos[produtos['TAXA'].str.slice(0,3) == 'CDI']
            else:
                produtos=produtos[produtos['TAXA'].str.slice(0,4) == 'IPCA']

    elif lc == 'Infração Implícita':
        ''
          

    if lc in ['CDB','LCA' ,'LCI','LC']:
        produtos['PRE_POS'] = pre_pos
        produtos['PRODUTO'] = pd.Categorical(produtos['PRODUTO'], categories=produtos['PRODUTO'].unique(),ordered=True)
        produtos['PRE_POS'] = pd.Categorical(produtos['PRE_POS'],categories=['PRÉ','PÓS'],ordered=True)

    #----------------------------------
    # Retirando letras

    produtos['PRAZO/VENCIMENTO'] = produtos['PRAZO/VENCIMENTO'].str.extract('(\d+)').astype(float)
    produtos['TAXA EQ. CDB'] = produtos['TAXA EQ. CDB'].astype(str).str.extract('([\d,]+)')
    produtos['TAXA EQ. CDB'] = produtos['TAXA EQ. CDB'].str.replace(',','.').astype(float)

    if lc == 'Inflação' and cdi_ipca == 'CDI':
        produtos['TAXA']=produtos['TAXA'].str.slice(4,9)
        produtos['TAXA'] = produtos['TAXA'].str.replace(',','.')

    elif lc in 'Inflação' and cdi_ipca in 'IPCA':
        produtos['TAXA'] =produtos['TAXA'].str.slice(5,10)
        produtos['TAXA'] = produtos['TAXA'].str.replace(',','.')

    produtos['PRAZO/VENCIMENTO'] = produtos['PRAZO/VENCIMENTO'].sort_values(ascending=True)
    produtos['TAXA EQ. CDB'] = produtos['TAXA EQ. CDB'].sort_values(ascending=True)

    produtos['PRODUTO'] =produtos['PRODUTO'].str[:-13]
    produtos['PRODUTO'] =produtos['PRODUTO'].str[16:]
    if lc in 'Inflação':
        produtos['PRODUTO'] =produtos['PRODUTO'].str[7:]
    produtos = produtos[produtos['PRODUTO'].isin(bancos_que_podem_ser_utilizados)]    

    produtos['Vencimento'] = datetime.datetime.now() + pd.to_timedelta(produtos['PRAZO/VENCIMENTO'],unit='D')
    produtos['Vencimento'] = produtos['Vencimento'].dt.strftime('%Y-%m-%d')
    curva_inflacao_copia = curva_inflacao_copia.iloc[:15,:]
    curva_inflacao_copia['Vertices'] = pd.to_numeric(curva_inflacao_copia['Vertices'],errors='coerce')
    curva_inflacao_copia['ETTJ'] = pd.to_numeric(curva_inflacao_copia['Vertices'],errors='coerce')
    

    print(curva_inflacao_copia.info())
    curva_inflacao_copia['Vencimento'] = datetime.datetime.now() + pd.to_timedelta(curva_inflacao_copia['Vertices'],unit='D')
    curva_inflacao_copia['Vencimento'] = curva_inflacao_copia['Vencimento'].dt.strftime('%Y-%m-%d')                                                               
    #----------------------------------
    #Calculando a curva 

    fig2=go.Figure()
    fig2.add_traces(go.Scatter(x=curva_base['Data'],
                        y=curva_base['Taxa Spot'],
                        mode='lines',
                        name='PREF',
                        line=dict(color='white',width = 6),
                        
                        ))
    curva_do_ipca=go.Figure()
    curva_do_ipca.add_traces(go.Scatter(x=curva_inflacao_copia['Vencimento'],
                        y=curva_inflacao_copia['ETTJ IPCA'],
                        mode='lines',
                        name='PREF',
                        line=dict(color='#DC143C')
                        ))      


    #----------------------------------
    #Graficos
    produtos.sort_values(by='Vencimento',inplace=True)
    produtos_com_curva = go.Figure()
    for produto, dados in produtos.groupby('PRODUTO'):
        produtos_com_curva.add_trace(go.Scatter(
            x=dados['Vencimento'],
            y=dados['TAXA EQ. CDB'],
            mode='lines+markers',
            name=produto,
            text=produtos.apply(
                    lambda row: f'O vencimento e em:  **{row["Vencimento"]}** e a Taxa do produto é:  **{row["TAXA EQ. CDB"]:.2f}%**  e o Banco emissor:  **{row["PRODUTO"]}**',axis=1),
                
        ))
        produtos_com_curva.update_layout(
        title=dict(text='Evolução PL dos Assessores ao longo do tempo',
                                                     font=dict(size=20),
                                                     x=0.1,
                                                     y=0.9),
                                                    showlegend=True,
                                                    
                                                    height=600,
                                                    width = 1500,   
                                                    xaxis=dict(
        showticklabels=True,  # Ative a exibição de rótulos no eixo x
        #tickmode='array',    # Modo de exibição de rótulos
        #tickvals=dados['Vencimento'][::6],  # Ajuste os valores dos rótulos para cada 6 períodos
        #ticktext=dados['Vencimento'][::6],       
        ))
        produtos_com_curva.update_yaxes(range=[9,12.5])      

    
    
    #----------------------------------
    #Scatter graph com curva:
    

    fig = go.Figure()
    if  lc in ['CDB','LCA' ,'LCI','LC'] and  pre_pos == 'PRÉ':    
        fig.add_trace(
            go.Scatter(
                x=produtos['Vencimento'],
                y=produtos['TAXA EQ. CDB'],
                mode='markers',
                marker=dict(
                size = 8,
                color = 'grey'     
                ),
                text=produtos.apply(
                    lambda row: f'O vencimento e em:  **{row["Vencimento"]}** e a Taxa do produto é:  **{row["TAXA EQ. CDB"]:.2f}%**  e o Banco emissor:  **{row["PRODUTO"]}**',axis=1),
                
            )
        )

    elif lc in ['CDB','LCA' ,'LCI','LC'] and pre_pos  =='PÓS':
        fig.add_trace(
            go.Scatter(
                x=produtos['Vencimento'],
                y=produtos['TAXA EQ. CDB'],
                mode='markers',
                marker=dict(
                size = 8,
                color = 'grey'     
                ),
               text=produtos.apply(
                    lambda row: f'O praze de vencimento e em:  {row["Vencimento"]}  dias   e a Taxa do produto é:  {row["TAXA EQ. CDB"]:.2f}%  e o Banco emissor:  {row["PRODUTO"]}',axis=1),
               
        )
    )
    
    elif lc  == 'Inflação':
        fig_inflacao = go.Figure()
        fig_inflacao.add_trace(
            go.Scatter(
                x=produtos['Vencimento'],
                y=produtos['TAXA'],
                mode='markers',
                marker=dict(
                size = 8,
                color = 'grey'     
                ),
               text=produtos.apply(
                    lambda row: f'O praze de vencimento e em:  {row["Vencimento"]}  dias   e a Taxa do produto é:  {row["TAXA"]}%  e o Banco emissor:  {row["PRODUTO"]}',axis=1),
               
        )
    )


    figura_inflacao_implicita = go.Figure()
    figura_inflacao_implicita.add_trace(
        go.Line(
            x=curva_inflacao_copia['Vertices'],
            y=curva_inflacao_copia['Inflação Implícita'],
            marker=dict(
            size = 8,
            color = 'red'     
            ),
            
    )
)
    figura_inflacao_implicita.update_yaxes(range=[3,6])
    figura_inflacao_implicita.update_xaxes(range=[0,2700])  


    fig.update_layout(
        showlegend= False,
        title = 'Produtos ofertadors',
        shapes =[dict(
            type='line',
            y0=100,
            y1=100,
            x0=0,
            x1=1,
            xref='paper',
            yref='y',
            line=dict(color='#FF8C00',width=2,dash='dash')
        )
        ]
    )
    if lc in ['CDB','LCA' ,'LCI','LC']  and pre_pos =='PRÉ':
        fig.update_yaxes(range=[8,13])

    elif lc in ['CDB','LCA' ,'LCI','LC'] and pre_pos =='PÓS' :
        fig.update_yaxes(range=[95,125])

    if lc in 'Inflação' and cdi_ipca in 'CDI':
        fig_inflacao.update_yaxes(range=[0,1.5])

    elif lc in'Inflação' and cdi_ipca in 'IPCA' :
        fig_inflacao.update_yaxes(range=[3,7])
   
   

    fig.update_xaxes(showticklabels = False)

    fig3 = go.Figure(data=produtos_com_curva.data+fig2.data)



    if lc in ['CDB','LCA' ,'LCI','LC'] and  pre_pos == 'PRÉ':
        st.plotly_chart(fig3,use_container_width=True)
        
    elif lc in ['CDB','LCA' ,'LCI','LC'] and pre_pos =='PÓS':
        st.plotly_chart(fig,use_container_width=True)

    elif lc  in 'Inflação' and cdi_ipca in 'CDI':
        st.plotly_chart(fig_inflacao,use_container_width=True)

    elif lc  in 'Inflação' and cdi_ipca in 'IPCA':
        inflação_e_produtos =go.Figure(data=fig_inflacao.data+curva_do_ipca.data)
        inflação_e_produtos.update_yaxes(range=[3,7])
        st.plotly_chart(inflação_e_produtos)

    elif lc in 'Inflação Implícita':    
        st.plotly_chart(figura_inflacao_implicita)  

       

    produtos = produtos.drop(columns=['PRAZO/VENCIMENTO','TAXA EQ. CDB'])
    st.dataframe(produtos)
           


#----------------------------------  ---------------------------------- ---------------------------------- ---------------------------------- 
# Pagina de divisão de contas por operador
#---------------------------------- ---------------------------------- ---------------------------------- ---------------------------------- 

if selecionar == 'Divisão de operadores':


        #####       Limpando arquivo e retirando colunas

        pl = pl.drop(columns='NOME')
        saldo = saldo.drop(columns='NOME')

        
        controle =  controle.iloc[:,[1,2,6,7,12,16,17,18,-1]]
       
        
        
        controle = controle.rename(columns = {'Unnamed: 2':'CONTA'})

        controle = controle.rename(columns= 
                                            {'Mesa de Operação':'Operador'})

        ####        Mesclando arquivos e adicionando variaveis

        juncao = pd.merge(pl,saldo,
                        how='outer',
                            on= 'CONTA')
        # Filtros para adicionar operadores

        filtro_nov1 =  juncao.SALDO> 1000
        filtro_nov2 = juncao.SALDO < 0
        
        juncao = juncao.loc[(
            filtro_nov1|filtro_nov2
            )]


        ###         Adicionando 00 para mesclar os arquivos ###
        controle['CONTA']=controle['CONTA'].astype(str)


        controle['CONTA'] = list(
            map(
                lambda x:'00'+ x,controle['CONTA']
                )
                    )


        arquivo_final = pd.merge(
            controle,juncao,
            on='CONTA',
            how= 'outer'
        )
            ####        Mesclando arquivos e adicionando variaveis

    # Filtros para adicionar operadores

        #Filtro Breno
        filtro = (arquivo_final['VALOR']<200000) & (arquivo_final['Operador']=='Edu')
        arquivo_final.loc[filtro,'Operador'] ='Breno'

        #Filtro Edu

        filtro2 =  filtro = (arquivo_final['VALOR']>200000) & (arquivo_final['Operador']=='Edu')
        arquivo_final.loc[filtro2,'Operador'] = 'Edu'

        #filtro Bruno

        filtro4 = (arquivo_final['VALOR']<200000) & (arquivo_final['Operador']=='Léo')
        arquivo_final.loc[filtro4,'Operador'] ='Bruno'
        
        # Filtro léo
        filtro6  = (arquivo_final['VALOR']>200000) & (arquivo_final['Operador']=='Léo')
        arquivo_final.loc[filtro6,'Operador'] = 'Léo'

        filtro7 = (arquivo_final['VALOR']>200000)&(arquivo_final['Operador'] =='Breno')
        arquivo_final.loc[filtro7,'Operador'] = 'Edu'

        filtro8 = (arquivo_final['VALOR']>200000)&(arquivo_final['Operador'] =='Bruno')
        arquivo_final.loc[filtro8,'Operador'] = 'Léo'

        
        
        #st.subheader('Este e o novo filtro')
        
        filtro_de_saldo = ((arquivo_final['SALDO']>1000)|(arquivo_final['SALDO']<0))
        arquivo_final2 = arquivo_final.loc[filtro_de_saldo]

        arquivo_final2['Operador'] = arquivo_final2['Operador'].fillna('Checar conta')
        arquivo_final2['Backoffice/ Mesa'] = arquivo_final2['Backoffice/ Mesa'].fillna('Checar conta')
    
       
        #### Criando funcao para alterar o nome dos operardores de acordo com criterios #### 
    
        
        arquivo_final2 = arquivo_final2.reset_index()
        
        arquivo_final2 = arquivo_final2.sort_values(by='SALDO',ascending=False)
        
        arquivo_final2 = arquivo_final2.rename(columns=
                                            {'Mesa de Operação.2':'Lembretes Mesa'})

        arquivo_final2 = arquivo_final2.rename(columns=
                                            {'VALOR':'BTG PL'})
        arquivo_final2 = arquivo_final2.rename(columns=
                                            {'Saldo':'Saldo Disponivel'})
        arquivo_final2 = arquivo_final2.rename(columns=
                                            {'Unnamed: 1':'Nome'})
        arquivo_final2 = arquivo_final2.rename(columns=
                                            {'Backoffice/ Mesa':'Status'})
        #>>>>25/10  'Backoffice/ Mesa'
        arquivo_final2 = arquivo_final2.rename(columns=
                                            {'Unnamed: 12':'Perfil da Carteira'})
        arquivo_final2 = arquivo_final2.rename(columns=
                                    {'Unnamed: 35':'PL Desatualizado'})
        
        arquivo_final2 = arquivo_final2.loc[(arquivo_final2['Status'] == 'Ativo') | (arquivo_final2['Status'] == 'Pode Operar')| (arquivo_final2['Status'] == 'Checar conta')]

        
        arquivo_final2 = arquivo_final2.iloc[:,[2,1,11,5,6,7,8,9,10,4,3]]


        
        arquivo_final2.insert(loc = 0,
                            column='Checkbox',
                            value=st.checkbox('arquivo_final2'
                                            )
                                            )


        barra1 = st.selectbox('Selecione o Operador',
                            options=arquivo_final2['Operador'].unique())

        df7 = arquivo_final2.loc[arquivo_final2['Operador'] == barra1]
        df6 = arquivo_final2['Operador'].value_counts()
        
        data_frame_of = st.data_editor(df7,
                                    width=2000,
                                    height=500,
                                    num_rows='dynamic')
         
        if arquivo_final2 is not None:
            
            
            # Use io.BytesIO para criar um buffer de bytes
            output4 = io.BytesIO()

            # Salve o DataFrame no buffer no formato XLSX
            with pd.ExcelWriter(output4, engine='xlsxwriter') as writer:
                arquivo_final2.to_excel(writer,
                                            sheet_name='Divisão_de_operadores.xlsx',
                                              index=False)
            
            # Crie um link para download
            output4.seek(0)
            st.download_button(
                label="Exportar dados",
                data=output4,
                file_name='Dvisão de contas por operador.xlsx',
                key='download_button'
            )
        st.markdown("<br>",unsafe_allow_html=True)
        st.markdown("<br>",unsafe_allow_html=True)

        col1,col2,col3,col4,col5 = st.columns(5)

        class Contas_Operadas:
            def __init__(self, numero_da_conta, nome_do_cliente, operador_da_conta, horario_da_operação):
                self.numero_da_conta = numero_da_conta
                self.nome_do_cliente = nome_do_cliente
                self.operador_da_conta = operador_da_conta
                self.horario_da_operação = horario_da_operação

        def processar_registro_de_conta_e_operador_resposavel(numero_da_conta,operador_da_conta):
            nome_do_cliente = arquivo_final2.loc[arquivo_final2['CONTA'] == numero_da_conta,'Nome'].iloc[0]
            horario_da_operação = datetime.datetime.now().strftime('%d-%m-%Y_%H')
            conta_operada = Contas_Operadas(numero_da_conta,nome_do_cliente,operador_da_conta,horario_da_operação)
            excel_file = 'contas_operadas.xlsx'
            try:
                df_existing = pd.read_excel(excel_file)
                df_new = pd.DataFrame([conta_operada.__dict__]).copy()
                df_combined = pd.concat([df_existing,df_new],ignore_index=True)
            except FileNotFoundError:
                ''

            df_combined.to_excel(excel_file,index=False)

            if botao_de_registro:
                st.success(f'Operador e conta registrada')


        possiveis_operadores_para_registro = ['Breno','Edu','Leo','Bruno']        
        with col1:numero_da_conta = st.text_input('Numero da Conta')
        with col1:operador_da_conta = st.selectbox('Quem operou',possiveis_operadores_para_registro),
        botao_de_registro = st.button('registrar Conta Operada',type='primary')

        st.markdown("<br>",unsafe_allow_html=True)
        if botao_de_registro and numero_da_conta and operador_da_conta:
            processar_registro_de_conta_e_operador_resposavel(numero_da_conta,operador_da_conta)


        contas_operadas = pd.read_excel('contas_operadas.xlsx')
        contas_operadas = contas_operadas.sort_index(ascending = False)
        contas_operadas['horario_da_operação'] = pd.to_datetime(contas_operadas['horario_da_operação'],format='%d-%m-%Y_%H',errors='coerce')

        contas_operadas_today = contas_operadas.loc[contas_operadas['horario_da_operação'].dt.date == datetime.datetime.now().date()]
        contas_operadas_today = contas_operadas_today.sort_values(by='horario_da_operação', ascending=False)
        print(contas_operadas.columns)
        st.dataframe(contas_operadas_today)

        if arquivo_final2 is not None:
            
            
            # Use io.BytesIO para criar um buffer de bytes
            output12 = io.BytesIO()

            # Salve o DataFrame no buffer no formato XLSX
            with pd.ExcelWriter(output12, engine='xlsxwriter') as writer:
                contas_operadas.to_excel(writer,
                                            sheet_name='Contas_operadas.xlsx',
                                              index=False)
            
            # Crie um link para download
            output12.seek(0)
            st.download_button(
                label="Exportar dados",
                data=output12,
                file_name='Contas_operadas.xlsx',
                key='download_button_contas_operadas',
            )                  
#----------------------------------  ---------------------------------- ---------------------------------- ---------------------------------- 
# Pagina de Analise
#---------------------------------- ---------------------------------- ---------------------------------- ---------------------------------- 
if selecionar == 'Analitico':

    arquivo2 = arquivo1.groupby(['CONTA','PRODUTO','ATIVO'])[['VALOR BRUTO','VALOR LÍQUIDO','QUANTIDADE']].sum().reset_index('CONTA')


    novo_arq = arquivo2.groupby(['PRODUTO','CONTA'])[['VALOR LÍQUIDO','QUANTIDADE']].sum().reset_index()
    controle = controle.iloc[:,[2,6,12]]


    controle['Unnamed: 2'] = controle['Unnamed: 2'].astype(str)
    controle['Unnamed: 2'] = list(map(lambda x: '00' + x,controle['Unnamed: 2']))
        
    juncao_arquivo_de_posicao_e_controle = pd.merge(controle,novo_arq, left_on='Unnamed: 2',right_on='CONTA', how= 'outer' )

    soma_dos_ativos_por_carteira = juncao_arquivo_de_posicao_e_controle.groupby(['Unnamed: 12','PRODUTO'])['VALOR LÍQUIDO'].sum().reset_index()

    def criando_df_para_grafico(perfil_do_cliente):
      df = soma_dos_ativos_por_carteira[soma_dos_ativos_por_carteira['Unnamed: 12'] == perfil_do_cliente]
      return df
    
    carteira_inc = criando_df_para_grafico('INC')
    carteira_con = criando_df_para_grafico('CON')
    carteira_mod = criando_df_para_grafico('MOD')
    carteira_arr = criando_df_para_grafico('ARR')
    carteira_equity = criando_df_para_grafico('EQT')
    carteira_FII = criando_df_para_grafico('FII')
    carteira_small = criando_df_para_grafico('SMLL')
    carteira_dividendos = criando_df_para_grafico('DIV')
    carteira_MOD_PREV_MOD = criando_df_para_grafico('MOD/ PREV MOD')
    carteira_INC_PREV_MOD = criando_df_para_grafico('INC/ PREV MOD')

    lista_para_incluir_coluna_de_porcentagem = [
        carteira_inc,
        carteira_con,
        carteira_mod,
        carteira_arr,
        carteira_equity,
        carteira_FII,
        carteira_small,
        carteira_dividendos,
        carteira_MOD_PREV_MOD,
        carteira_INC_PREV_MOD]

    carteira_inc['Porcentagem'] = (carteira_inc['VALOR LÍQUIDO']/carteira_inc['VALOR LÍQUIDO'].sum())*100

    for dfs in lista_para_incluir_coluna_de_porcentagem:
        dfs['Porcentagem'] = (dfs['VALOR LÍQUIDO']/dfs['VALOR LÍQUIDO'].sum())*100
    for dfs in lista_para_incluir_coluna_de_porcentagem:
        dfs.drop(dfs[dfs['Porcentagem']<1].index, inplace=True)    

    padronizacao_dos_graficos = dict(hole=0.4,
                                    textinfo='label+percent',
                                    insidetextorientation='radial',
                                    textposition='inside')
    night_colors = ['rgb(56, 75, 126)', 'rgb(18, 36, 37)', 'rgb(34, 53, 101)',
                'rgb(36, 55, 57)', 'rgb(6, 4, 4)']
    sunflowers_colors = ['rgb(177, 127, 38)', 'rgb(205, 152, 36)', 'rgb(99, 79, 37)',
                     'rgb(129, 180, 179)', 'rgb(124, 103, 37)']
    irises_colors = ['rgb(33, 75, 99)', 'rgb(79, 129, 102)', 'rgb(151, 179, 100)',
                 'rgb(175, 49, 35)', 'rgb(36, 73, 147)']
    cafe_colors =  ['rgb(146, 123, 21)', 'rgb(177, 180, 34)', 'rgb(206, 206, 40)',
                'rgb(175, 51, 21)', 'rgb(35, 36, 21)']
    lista_acoes_em_caixa = [
            'ARZZ3',
            'ASAI3',
            'CSAN3',
            'CSED3',
            'EGIE3',
            'EQTL3',
            'EZTC3',
            'HYPE3',
            'KEPL3',
            'MULT3',
            'PRIO3',
            'PSSA3',
            'SBSP3',
            'SLCE3',
            'VALE3']
    
    def criando_graficos_rf_rv (df,title,color):
        df['Renda Variavel'] = df.loc[df['PRODUTO'].isin(lista_acoes_em_caixa),'VALOR LÍQUIDO'].sum()
        df['Renda Fixa'] = df.loc[~df['PRODUTO'].isin(lista_acoes_em_caixa),'VALOR LÍQUIDO'].sum()
        df['Total RV RF'] = df['Renda Variavel'] + df['Renda Fixa']
        labels = ['Renda Variavel', 'Renda Fixa']
        values = [df['Renda Variavel'].sum(), df['Renda Fixa'].sum()]
        colors = cafe_colors
        fig = go.Figure(data=[go.Pie(labels=labels, values=values, marker=dict(colors=color))])
        fig.update_layout(title_text=title,
                              title_x=0.2,
                              title_font_size = 23,
                              uniformtext_minsize=14,)
        
        # Exibe o gráfico no Streamlit
        st.plotly_chart(fig)

        #df2 = df.melt(id_vars=['PRODUTO'], var_name='VALOR LÍQUIDO', value_name='Valor')
        return df
    mostrar_rv_x_rf = st.toggle('Ver Proporção Renda Fixa vs Renda Variável')
    if mostrar_rv_x_rf:
        carteira_arr_media_rv_rf = criando_graficos_rf_rv(carteira_arr,'Arrojada',cafe_colors)
        carteira_mod_media_rv_rf = criando_graficos_rf_rv(carteira_mod,'Moderada',night_colors)
    

    def criando_graficos(carteira,padronizacao,titulo):

        figura = go.Figure(data=[go.Pie(
            labels=carteira['PRODUTO'],
            values=carteira['VALOR LÍQUIDO'],
            marker_colors=sunflowers_colors,
            scalegroup='one'

            
                        )])
        figura.update_traces(**padronizacao)
        figura.update_layout(title_text = titulo,
                              title_x=0.2,
                              title_font_size = 23,
                              uniformtext_minsize=14,
                              #uniformtext_mode='hide'
                              )

        return figura
        


    figura_carteira_inc = criando_graficos(carteira_inc,padronizacao_dos_graficos,'Carteira Income')
    figura_carteira_con = criando_graficos(carteira_con,padronizacao_dos_graficos,'Carteira Conservadora')
    figura_carteira_mod = criando_graficos(carteira_mod,padronizacao_dos_graficos,'Carteira Moderada')
    figura_carteira_arr = criando_graficos(carteira_arr,padronizacao_dos_graficos,'Carteira Arrojada')
    figura_carteira_equity = criando_graficos(carteira_equity,padronizacao_dos_graficos,'Carteira Equity')
    figura_carteira_FII = criando_graficos(carteira_FII,padronizacao_dos_graficos,'Carteira FII')
    figura_carteira_small = criando_graficos(carteira_small,padronizacao_dos_graficos,'Carteira Small Caps')
    figura_carteira_dividendos = criando_graficos(carteira_dividendos,padronizacao_dos_graficos,'Carteira Dividendos')
    figura_carteira_MOD_PREV_MOD = criando_graficos(carteira_MOD_PREV_MOD,padronizacao_dos_graficos,'Carteira Moderada - Previdencia - Moderada')
    figura_carteira_INC_PREV_MOD = criando_graficos(carteira_INC_PREV_MOD,padronizacao_dos_graficos,'Carteira Income - Previdencia - Moderada')

    col1,col2 = st.columns(2)
    with col1: 
        carteira_income = st.toggle('Income',key='ver_income')
        carteira_conse = st.toggle('Conservadora',key='ver_conservadora')
        carteira_moderada_tog = st.toggle('Moderada',key='ver_mdoerada')
        carteira_Arr = st.toggle('Arrojada',key='ver_arrojada')
        carteira_Eqt = st.toggle('Equity',key='ver_eqt') 
        st.markdown("<br>",unsafe_allow_html=True)
        st.markdown("<br>",unsafe_allow_html=True)
    with col2:  
        carteira_fii_tg = st.toggle('FII',key='ver_fiis')
        carteira_sml = st.toggle('Small',key='ver_smlss')
        carteira_dividendos_tg = st.toggle('Dividendos',key='ver_dividendos')
        carteira_mod_prev = st.toggle('Moderada Previdencia',key='ver_mod_prev')
        carteira_inc_prev = st.toggle('Income Previdencia',key='ver_inc')
        st.markdown("<br>",unsafe_allow_html=True)
        st.markdown("<br>",unsafe_allow_html=True)

    ajustas_coluna_de_porcentagem = [
        carteira_inc  , carteira_con,carteira_mod,
        carteira_arr,carteira_equity,
        carteira_FII,carteira_small,carteira_dividendos,
        carteira_MOD_PREV_MOD,carteira_INC_PREV_MOD
            ]
    for dfs in ajustas_coluna_de_porcentagem:
        dfs['Porcentagem'] = dfs['Porcentagem'].apply(lambda x: f'{x:.2f}%' )


    if carteira_income:
        with col1:st.plotly_chart(figura_carteira_inc,use_container_width=True)
        with col2:st.dataframe(carteira_inc)

    elif carteira_conse:
        with col1:st.plotly_chart(figura_carteira_con,use_container_width=True)
        with col2:st.dataframe(carteira_con)

    elif carteira_moderada_tog:
        with col1:st.plotly_chart(figura_carteira_mod,use_container_width=True)
        with col2:st.dataframe(carteira_mod)

    elif carteira_Arr:
        with col1:st.plotly_chart(figura_carteira_arr,use_container_width=True)
        with col2:st.dataframe(carteira_arr)

    elif carteira_Eqt:
        with col1:st.plotly_chart(figura_carteira_equity,use_container_width=True)
        with col2:st.dataframe(carteira_equity)

    elif carteira_fii_tg:
        with col1:st.plotly_chart(figura_carteira_FII,use_container_width=True)
        with col2:st.dataframe(carteira_FII)

    elif carteira_sml:
        with col1:st.plotly_chart(figura_carteira_small,use_container_width=True)
        with col2:st.dataframe(carteira_small)

    elif carteira_dividendos_tg:
        with col1:st.plotly_chart(figura_carteira_dividendos,use_container_width=True)
        with col2:st.dataframe(carteira_dividendos)

    elif carteira_inc_prev:
        with col1:st.plotly_chart(figura_carteira_INC_PREV_MOD,use_container_width=True)
        with col2:st.dataframe(carteira_INC_PREV_MOD)

    elif carteira_mod_prev:
        with col1:st.plotly_chart(figura_carteira_MOD_PREV_MOD,use_container_width=True)
        with col2:st.dataframe(carteira_MOD_PREV_MOD)


    ativos_e_dispercoes = []
    def obter_dados(ativo,start_dt,end_dt, numero_periodo):
        data = yf.download(ativo+'.SA',start=start_dt,end=end_dt,period='1d')
        return data['Close'].tail(numero_periodo)
    
    

    def calcular_media(ativo,inicio,fim):
        dados = obter_dados(ativo,inicio,fim,40)

        media_21 = dados.rolling(window=21).mean()
        media_42 = dados.rolling(window=42).mean()

        return media_21,media_42
    

    data_atual = pd.to_datetime('today').strftime('%Y-%m-%d')
    vinte_e_um_DIAS = (pd.to_datetime('today')-pd.DateOffset(days=21)).strftime('%Y-%m-%d')
    quarenta_e_dois = (pd.to_datetime('today')-pd.DateOffset(days=42)).strftime('%Y-%m-%d')

    for ativo in lista_acoes_em_caixa:
        media_21,media_42 = calcular_media(ativo,quarenta_e_dois,data_atual)
    
        print(ativo,media_21,media_42)

if selecionar == 'Análise Tecnica':
    st.header("Disperção dos ativos")       
    lista_acoes_em_caixa = [
        'ARZZ3',
        'ASAI3',
        'CSAN3',
        'CSED3',
        'EGIE3',
        'EQTL3',
        'EZTC3',
        'HYPE3',
        'KEPL3',
        'MULT3',
        'PRIO3',
        'PSSA3',
        'SBSP3',
        'SLCE3',
        'VALE3']


    data_atual = pd.to_datetime('today').strftime('%Y-%m-%d')
    vinte_e_um_DIAS = (pd.to_datetime('today')-pd.DateOffset(days=21)).strftime('%Y-%m-%d')
    quarenta_e_dois = (pd.to_datetime('today')-pd.DateOffset(days=755)).strftime('%Y-%m-%d')



    graficos = go.Figure()

    ativos_e_dispercoes = []
    try:
        def obter_dados(ativo,start_dt,end_dt,):
            data = yf.download(ativo+'.SA',start=start_dt,end=end_dt,period='1d')
            return data
    except:
        st.warning('Problema com os dados')
    for ativos in lista_acoes_em_caixa:

        ticker = obter_dados(ativos,quarenta_e_dois,data_atual)
        ticker['Ativo'] = ativos
        dados = ticker[ticker['Ativo']==ativos]
        dados = dados.dropna()
        dados['SMA 42'] = dados['Adj Close'].ewm(span=42,adjust=False).mean()
        dados['SMA 21'] = dados['Adj Close'].ewm(span=21,adjust=False).mean()

        dados['Dispersão 42 periodos'] = (dados['Adj Close']/dados['SMA 42'])-1
        dados['Dispersão 21 periodos'] = (dados['Adj Close']/dados['SMA 21'])-1

        dados['Disperção 42 preço'] = dados['Adj Close'].iloc[-1]*dados['Dispersão 42 periodos'].iloc[-1]

        st.warning(f"Ativo : {ativos} Preço :{dados['Adj Close'].iloc[-1]:,.2f}")
        st.warning(f" Média de 42 periodos :{dados['SMA 42'].iloc[-1]:,.2f}---Dispersão maxima : {dados['Dispersão 42 periodos'].max()*100:,.2f}%---Dispersão minima : {dados['Dispersão 42 periodos'].min()*100:,.2f}%---Dispersão media : {dados['Dispersão 42 periodos'].mean()*100:,.2f}%---Disperção atual :{dados['Dispersão 42 periodos'].iloc[-1]*100:,.2f}%")
        st.warning(f" Média de 21 periodos :{dados['SMA 21'].iloc[-1]:,.2f},--- Dispersão maxima : {dados['Dispersão 21 periodos'].max()*100:,.2f}%,--- Dispersão minima : {dados['Dispersão 21 periodos'].min()*100:,.2f}%---Dispersão media  : {dados['Dispersão 21 periodos'].mean()*100:,.2f}%----  Disperção  atual :{dados['Dispersão 21 periodos'].iloc[-1]*100:,.2f}%")
        

        graficos = go.Figure()
        graficos.add_trace(go.Scatter(x=dados.index, y=dados['Adj Close'], mode='lines', line=dict(width=3,color='orange'), name=f'{ativos} - Preço'))
        graficos.add_trace(go.Scatter(x=dados.index, y=dados['SMA 42'], mode='lines', name=f'{ativos} - SMA 42'))
        graficos.add_trace(go.Scatter(x=dados.index, y=dados['SMA 21'], mode='lines', name=f'{ativos} - SMA 21'))

        graficos.update_layout(title=f'{ativos} - Metrics Comparison',
                            xaxis_title='Data',
                            yaxis_title='Valor',
                            legend=dict(x=0, y=1, traceorder='normal'))


        st.plotly_chart(graficos,use_container_width=True)






t1 = time.perf_counter()

print(t1-t0)







