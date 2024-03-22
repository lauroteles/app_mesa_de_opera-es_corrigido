
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
import pytz
import divisao_de_operadores
from divisao_de_operadores import Divisao_de_contas
from divisao_guide import Guide_Divisao_contas

t0 = time.perf_counter()

st.set_page_config(layout='wide')

paginas = 'Home','Carteiras','Produtos','Divisão de operadores','Carteiras Co Admin','Analitico','Análise Tecnica',
selecionar = st.sidebar.radio('Selecione uma opção', paginas)


#---------------------------------- 
# Variaveis globais
@st.cache_data(ttl='3m')     
def le_excel(x,page,row):
    df = pd.read_excel(x,page,skiprows=row)
    return df

pl_original = le_excel('PL Total.xlsx',0,0)
controle_original = le_excel('controle.xlsx',0,0)
saldo_original = le_excel('Saldo.xlsx',0,0)
posicao_original = le_excel('Posição.xlsx',0,0)
produtos_original = le_excel('Produtos.xlsx',0,0)
cura_original = le_excel('Curva_comdinheiro.xlsx',0,0)
curva_de_inflacao = le_excel('Curva_inflação.xlsx',0,0)
posicao_btg1 = le_excel('Posição.xlsx',0,0)
planilha_controle1 = le_excel('controle.xlsx',0,0)
co_admin = le_excel('Controle de Contratos - Carteiras Co-Administradas.xlsx',1,1)
controle_psicao = le_excel('controle.xlsx',0,1)
rentabilidade = le_excel('Rentabilidade (1).xlsx',0,0)
bancos = le_excel('Limite Bancos 06_23.xlsx',0,1)

pl = pl_original.copy()
controle = controle_original.copy()
saldo = saldo_original.copy()
arquivo1 = posicao_original.copy()
produtos = produtos_original.copy()
curva_base = cura_original.copy()
curva_inflacao_copia = curva_de_inflacao.copy()
posicao_btg = posicao_btg1.copy()
planilha_controle = planilha_controle1.copy()
controle_co_admin = co_admin.copy()

#----------------------------------  ---------------------------------- ---------------------------------- ---------------------------------- 
# Pagina de Carteiras
#---------------------------------- ---------------------------------- ---------------------------------- ---------------------------------- 


colors_dark_rainbow = ['#9400D3', '#4B0082', '#0000FF', '#00FF00', '#FFFF00',
                       '#FF7F00', '#FF0000']
colors_dark_brewers = ['#2c7bb6', '#abd9e9', '#ffffbf', '#fdae61', '#d7191c']

equities = {'ARZZ3': 5,'ASAI3':6.50,'BBSE3':5,'CPFE3':5.50,'EGIE3':5.50,'EZTC3':6.50,'HYPE3':8.00,'KEPL3':8.75,
            'LEVE3':5,'PRIO3':8,'PSSA3':2.50,'SBSP3':4,'SLCE3':9.75,'VALE3':10,'VIVT3':5,'Caixa':5}

income = {'POS':15,'Inflação':38,'PRE':44,'FundoDI':3}

small_caps = {'BPAC11':10,'ENEV3':4,'HBSA3':7,'IFCM3':5,'IFCM3':5,'JALL3':10,'KEPL3':12,'MYPK3':5,'PRIO3':12,'SIMH3':8,'TASA4':8,'TUPY3':11,'WIZC3':5}

dividendos = {'TAEE11':9,'VIVT3':12,'BBSE3':17, 'ABCB4':16,' VBBR3':15,' CPLE6':16,' TRPL4':5}

fii = {'BTLG11':22.30,'Caixa':6,'HGLG11':22.30,'KNCA11':7.25,'MALL11':7.75,'PLCR11':13.57,'RURA11':7.26,'TRXF11':13.57}

lista_acoes_em_caixa = [ 'ARZZ3', 'ASAI3', 'BBSE3', 'CPFE3', 'EGIE3', 'EZTC3', 'HYPE3', 'KEPL3', 'LEVE3', 'PRIO3', 'PSSA3', 'SBSP3', 'VIVT3', 'SLCE3', 'VALE3',]



if selecionar == 'Carteiras':
    from carteiras_indiv import Basket_enquadramento_carteiras

    if __name__=='__main__':
        dia_e_hora = datetime.datetime.now()
        inciando_programa = Basket_enquadramento_carteiras()
        try:
            carteira_equity = inciando_programa.criando_carteiras('Carteira_equity',equities)
            carteira_income = inciando_programa.criando_carteiras('Carteira Income',income)
            carteira_small = inciando_programa.criando_carteiras('Carteira Small',small_caps)
            carteira_dividendos = inciando_programa.criando_carteiras('Carteira Dividendos',dividendos)
            carteira_fii = inciando_programa.criando_carteiras('Carteira FII', fii)
            carteira_conservadora = inciando_programa.criando_carteiras_hibridas('Carteira Conservadora',0.15,0.85)
            carteira_moderada = inciando_programa.criando_carteiras_hibridas('Carteira Moderada',0.30,0.70)
            carteira_arrojada = inciando_programa.criando_carteiras_hibridas('Carteira Arrojada',0.50,0.50)

            dados_finais = inciando_programa.juntando_arqeuivos(controle=controle_psicao,posicao=posicao_btg1)
            trantrando_dados_controle = inciando_programa.tratamento_de_dados_controle(controle_psicao)

            input_conta = st.sidebar.text_input('Escreva o número da conta : ')
            
            dados_finais = dados_finais.loc[dados_finais['Conta']==input_conta].iloc[:,[8,9,10]]

            patrimono_liquido_da_conta = dados_finais["Valor Líquido"].sum()
            trantrando_dados_controle = trantrando_dados_controle.loc[trantrando_dados_controle['Conta']==input_conta]

            carteira_modelo = inciando_programa.selecionando_modelo_de_carteira(trantrando_dados_controle,
                                                                                carteira_arrojada,carteira_conservadora,carteira_moderada,
                                                                                carteira_income,carteira_equity,carteira_small,carteira_dividendos,carteira_fii)
        
            carteira_modelo['Valor R$'] = carteira_modelo['Proporção']*patrimono_liquido_da_conta
            carteira_modelo['Proporção'] = carteira_modelo['Proporção'].map(lambda x: f"{x * 100:,.2f}  %")

            try:
                basket_ = inciando_programa.criacao_basket(carteira_modelo=carteira_modelo,dados_finais=dados_finais,input_conta=input_conta)
            except:
                pass

            st.text(f'Patrimônio Líquido da carteira :   {dados_finais["Valor Líquido"].sum():,.2f}')
                    
            try:        
                output4 = io.BytesIO()
                with pd.ExcelWriter(output4, engine='xlsxwriter') as writer:basket_.to_excel(writer,sheet_name=f'Basket__{input_conta}___',index=False)
                output4.seek(0)
                st.download_button(type='primary',label="Basket Download",data=output4,file_name=f'basket_{input_conta}__{dia_e_hora}.xlsx',key='download_button')
            except:
                pass    
            
            col1,col2 = st.columns(2)
            with col1:
                if st.toggle('Enquadramento da carteira'):
                            grafico_estrategia = inciando_programa.checando_estrategia(dados_finais)
                else:                    
                    posicao_atual_grafico = inciando_programa.criando_graficos_posicao_atual(dados_finais)

                st.dataframe(dados_finais.sort_values(by='Produto'),use_container_width=True)
                st.dataframe(trantrando_dados_controle.unstack(),use_container_width=True)
                basket_compra = basket_[basket_['C/V']=='C']
                basket_compra['Valor'] = basket_compra['Quantidade']*basket_compra['Preço']
                basket_venda = basket_[basket_['C/V']=='V']
                basket_venda['Valor'] = basket_venda['Quantidade']*basket_venda['Preço']
                st.warning(f' O saldo Nescessario para Compra : {basket_compra["Valor"].sum():,.2f}')
                st.warning(f' O saldo Nescessario para Venda : {basket_venda["Valor"].sum():,.2f}')
                st.dataframe(basket_)

            with col2:
                grafico_posicao_ideal = inciando_programa.criando_graficos_posicao_ideal(carteira_modelo=carteira_modelo)
                st.dataframe(carteira_modelo.sort_values(by='Ativo'),use_container_width=True)

                grafico_rentabilidade = inciando_programa.grafico_rentabilidade(rentabilidade,input_conta)
        except:
            st.write('Conta nâo encontrada')


#----------------------------------  ---------------------------------- ---------------------------------- ---------------------------------- 
# Pagina de produtos
#---------------------------------- ---------------------------------- ---------------------------------- ---------------------------------- 

if selecionar == 'Produtos':

    produtos = pd.read_excel('Produtos.xlsx')
    produtos = produtos[[
       'PRODUTO', 'PRAZO/VENCIMENTO', 'TAXA','TAXA EQ. CDB']]
    
    produtos['PRODUTO'] = produtos['PRODUTO'].fillna(0)
    produtos = produtos[produtos['PRODUTO'] !=0]


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
    fig2.add_traces(go.Scatter(x=curva_base['Data'],y=curva_base['Taxa Spot'],mode='lines',name='PREF',line=dict(color='white',width = 6),
                        
                        ))
    curva_do_ipca=go.Figure()
    curva_do_ipca.add_traces(go.Scatter(x=curva_inflacao_copia['Vencimento'],y=curva_inflacao_copia['ETTJ IPCA'],mode='lines',name='PREF',line=dict(color='#DC143C')))      


    produtos.sort_values(by='Vencimento',inplace=True)
    produtos_com_curva = go.Figure()
    for produto, dados in produtos.groupby('PRODUTO'):
        produtos_com_curva.add_trace(go.Scatter(x=dados['Vencimento'],y=dados['TAXA EQ. CDB'],mode='lines+markers',name=produto,text=produtos.apply(
                    lambda row: f'O vencimento e em:  **{row["Vencimento"]}** e a Taxa do produto é:  **{row["TAXA EQ. CDB"]:.2f}%**  e o Banco emissor:  **{row["PRODUTO"]}**',axis=1),))
        produtos_com_curva.update_layout(
        title=dict(text='Evolução PL dos Assessores ao longo do tempo', font=dict(size=20), x=0.1, y=0.9),showlegend=True,height=600,width = 1500,   xaxis=dict(
        showticklabels=True,))
        produtos_com_curva.update_yaxes(range=[9,12.5])      

    #----------------------------------
    #Scatter graph com curva:
    

    fig = go.Figure()
    if  lc in ['CDB','LCA' ,'LCI','LC'] and  pre_pos == 'PRÉ':    
        fig.add_trace(
            go.Scatter(x=produtos['Vencimento'],y=produtos['TAXA EQ. CDB'],mode='markers',marker=dict(size = 8,color = 'grey'     ),text=produtos.apply(    lambda row: f'O vencimento e em:  **{row["Vencimento"]}** e a Taxa do produto é:  **{row["TAXA EQ. CDB"]:.2f}%**  e o Banco emissor:  **{row["PRODUTO"]}**',axis=1),
                ))

    elif lc in ['CDB','LCA' ,'LCI','LC'] and pre_pos  =='PÓS':
        fig.add_trace(
            go.Scatter( x=produtos['Vencimento'], y=produtos['TAXA EQ. CDB'], mode='markers', marker=dict( size = 8, color = 'grey'      ),text=produtos.apply(
                    lambda row: f'O praze de vencimento e em:  {row["Vencimento"]}  dias   e a Taxa do produto é:  {row["TAXA EQ. CDB"]:.2f}%  e o Banco emissor:  {row["PRODUTO"]}',axis=1),))
    
    elif lc  == 'Inflação':
        fig_inflacao = go.Figure()
        fig_inflacao.add_trace(
            go.Scatter( x=produtos['Vencimento'], y=produtos['TAXA'], mode='markers', marker=dict( size = 8, color = 'grey'),text=produtos.apply(
                    lambda row: f'O praze de vencimento e em:  {row["Vencimento"]}  dias   e a Taxa do produto é:  {row["TAXA"]}%  e o Banco emissor:  {row["PRODUTO"]}',axis=1),))


    figura_inflacao_implicita = go.Figure()
    figura_inflacao_implicita.add_trace(
        go.Line(x=curva_inflacao_copia['Vertices'],y=curva_inflacao_copia['Inflação Implícita'],marker=dict(size = 8,color = 'red'),))
    figura_inflacao_implicita.update_yaxes(range=[3,6])
    figura_inflacao_implicita.update_xaxes(range=[0,2700])  


    fig.update_layout(
        showlegend= False,
        title = 'Produtos ofertadors',
        shapes =[dict(
            type='line',
            y0=100,y1=100,x0=0,x1=1,xref='paper',yref='y',line=dict(color='#FF8C00',width=2,dash='dash'))])
    
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
       
    col1,col2 = st.columns(2)
    produtos = produtos.drop(columns=['PRAZO/VENCIMENTO','TAXA EQ. CDB'])
    with col1:
        bancos =    bancos.iloc[:,:6]
        bancos['Risco'] = round(bancos['Risco'],2)
        seletor_bancos = st.text_input('')

        if seletor_bancos.strip():
            bancos = bancos[bancos['Emissores'].str.contains(seletor_bancos,case=False)]
        else:
            bancos = bancos    
        st.dataframe(bancos)    
    with col2 :
        st.dataframe(produtos)


#----------------------------------  ---------------------------------- ---------------------------------- ---------------------------------- 
# Pagina de divisão de contas por operador
#---------------------------------- ---------------------------------- ---------------------------------- ---------------------------------- 

if selecionar == 'Divisão de operadores':
    corretora = st.radio('',['BTG','Guide'])
    if corretora == 'BTG':    
        saldo_original1 = le_excel('Saldo.xlsx',0,0)
        pl_original1 = le_excel('PL Total.xlsx',0,0)
        controle_2 = le_excel('Controle de Contratos - Atualizado Fevereiro de 2024 (5).xlsx',2,1)

        arquivo1 = Divisao_de_contas()

        arquivo_compilado = arquivo1.limpando_dados(controle=controle_2,saldo=saldo_original1,pl=pl_original1)

        filtrando_saldo = arquivo1.filtrando_dados_e_separando_operadores(arquivo_compilado=arquivo_compilado)
        contando_operadores = arquivo1.contando_oepradores(arquivo_compilado=arquivo_compilado)

        col1,col2 = st.columns(2)
        st.text(f"{filtrando_saldo['Operador'].value_counts().to_string()}")
        with col1:
            seletor_operador = st.selectbox('Operadores',options=filtrando_saldo['Operador'].unique())
            filtrando_saldo = filtrando_saldo.loc[filtrando_saldo['Operador']==seletor_operador] 



        cores = {'Inativo':'background-color: yellow',
                'Ativo':'background-color: green',
                'Pode Operar':'background-color: green',
                'Checar conta':'background-color: red',
                np.nan:'background-color: #B8860B'}
            
        
        st.dataframe(filtrando_saldo.style.applymap(lambda x: cores[x], subset=['Status']),use_container_width=True)

        contas_faltantes = arquivo1.contas_nao_encontradas(arquivo_compilado=arquivo_compilado)

        st.text(f" Contagem Total de clientes por {contando_operadores['Operador'].value_counts().to_string()}")
        if contas_faltantes is not None:
            st.subheader('Checar Contas')
            st.dataframe(contas_faltantes)
        else:
            ''
    if corretora == 'Guide':

        controle_g = le_excel('Controle de Contratos - Atualizado Fevereiro de 2024 (5).xlsx',3,1)
        pl = le_excel('Bluemetrix20240318_ABS.xlsx',0,0)
        saldo = le_excel('Saldo_guide.xlsx',0,0)


        iniciando = Guide_Divisao_contas()
        arquivo_final = iniciando.trabalhando_dados(controle_g=controle_g,pl=pl,saldo=saldo)
        dividindo_operadores = iniciando.dividindo_contas(arquivo_final=arquivo_final)
        contas_nao_contradas = iniciando.contas_nao_encontradas(arquivo_compilado=arquivo_final)
        contando_operadoress = iniciando.contando_oepradores(arquivo_final)
        print(arquivo_final.info())
        col1,col2 = st.columns(2)
        st.text(f"{dividindo_operadores['Operador'].value_counts().to_string()}")
        with col1:
            seletor_operador = st.selectbox('Operadores',options=dividindo_operadores['Operador'].unique())
            dividindo_operadores = dividindo_operadores.loc[dividindo_operadores['Operador']==seletor_operador] 



        cores = {'Inativo':'background-color: yellow',
                'Ativo':'background-color: green',
                'Pode Operar':'background-color: green',
                'Checar conta':'background-color: red',
                'Encerrado':'background-color: #A0522D',
                np.nan:'background-color: #A0522D'}
            
        
        st.dataframe(dividindo_operadores.style.applymap(lambda x: cores[x], subset=['Status']),use_container_width=True)
        st.subheader('Checar contas')
        st.dataframe(contas_nao_contradas)
        st.text(f" Contagem Total de clientes por {contando_operadoress['Operador'].value_counts().to_string()}")

#----------------------------------  ---------------------------------- ---------------------------------- ---------------------------------- 
# Pagina de Analise
#---------------------------------- ---------------------------------- ---------------------------------- ---------------------------------- 
if selecionar == 'Analitico':




    posicao_btg = posicao_original.iloc[:,[0,4,10]]
    planilha_controle = controle.iloc[:,[2,12,]]
    posicao_btg = posicao_btg.rename(columns={'CONTA':'Conta','PRODUTO':'Produto','ATIVO':'Ativo','VALOR BRUTO':'Valor Bruto','QUANTIDADE':'Quantidade'})

    planilha_controle = planilha_controle.drop(0)
    planilha_controle['Unnamed: 2'] =planilha_controle['Unnamed: 2'].map((lambda x: '00'+str(x))) 
    planilha_final = pd.merge(posicao_btg,planilha_controle,left_on='Conta',right_on='Unnamed: 2',how='outer').reset_index()


    soma_dos_ativos_por_carteira = planilha_final.groupby(['Unnamed: 12','Produto'])['Valor Bruto'].sum().reset_index()
    
  



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
    
    lista_remover_excecoes = [
        carteira_inc,
        carteira_mod,
        carteira_arr,
        carteira_equity,
        carteira_FII,
        carteira_small,
        carteira_dividendos,
        carteira_MOD_PREV_MOD,
        carteira_INC_PREV_MOD]

    carteira_inc['Porcentagem'] = (carteira_inc['Valor Bruto']/carteira_inc['Valor Bruto'].sum())*100

    for dfs in lista_para_incluir_coluna_de_porcentagem:
        dfs['Porcentagem'] = (dfs['Valor Bruto']/dfs['Valor Bruto'].sum())*100
    for dfs in lista_remover_excecoes:
        dfs.drop(dfs[dfs['Porcentagem']<1].index, inplace=True) 

    carteira_con = carteira_con.drop(carteira_con[carteira_con['Porcentagem']<0.2].index)

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
    colors_dark24 = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
                 '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf',
                 '#5254a3', '#ff6f61', '#6b6b6b', '#738595', '#e71d36',
                 '#ff9f1c', '#f4d35e', '#6a4c93', '#374649', '#8aaabb',
                 '#f9f7f5', '#f9f7f5', '#f9f7f5', '#f9f7f5']
    colors_dark_rainbow = ['#9400D3', '#4B0082', '#0000FF', '#00FF00', '#FFFF00',
                       '#FF7F00', '#FF0000']
    colors_dark_brewers = ['#2c7bb6', '#abd9e9', '#ffffbf', '#fdae61', '#d7191c']
    colors_dark10 = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
                 '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
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
    caixa = [
        'BTG PACT TESOURO SELIC PREV FI RF REF DI',
        'TESOURO DIRETO - LFT',      
    ]
    small_caps = ['BPAC11','ENEV3','HBSA3','IFCM3','JALL3','KEPL3',
    'MYPK3','PRIO3','SIMH3','TASA4','TUPY3','WIZC3']


    #dividendos = ['TAEE11','VIVT3','BBSE3','ABCB4','VBBR3','CPLE6','TRPL4',]
    dividendos = ['CDB','BTG PACTUAL TESOURO SELIC FI RF REF DI']
        
    
    def criando_graficos_rf_rv (df,title,color):
        df['Renda Variavel'] = df.loc[df['Produto'].isin(lista_acoes_em_caixa),'Valor Bruto'].sum()
        df['Renda Fixa'] = df.loc[~df['Produto'].isin(lista_acoes_em_caixa),'Valor Bruto'].sum()
        df['Total RV RF'] = df['Renda Variavel'] + df['Renda Fixa']
        labels = ['Renda Variavel', 'Renda Fixa']
        values = [df['Renda Variavel'].sum(), df['Renda Fixa'].sum()]
        colors = cafe_colors
        fig = go.Figure(data=[go.Pie(labels=labels, values=values, marker=dict(colors=color))])
        fig.update_layout(title_text=title,
                              title_x=0.2,
                              title_font_size = 23,
                              uniformtext_minsize=14,)
        st.plotly_chart(fig,use_container_width=True)

        return df
    def criando_graficos_caixa (df,title,color):
        df['Caixa'] = df.loc[df['Produto'].isin(caixa),'Valor Bruto'].sum()
        df['Ativos'] = df.loc[~df['Produto'].isin(caixa),'Valor Bruto'].sum()
        df['Total Caixa Ativos'] = df['Caixa'] + df['Ativos']
        labels = ['Caixa', 'Ativos']
        values = [df['Caixa'].sum(), df['Ativos'].sum()]
        colors = cafe_colors
        fig2 = go.Figure(data=[go.Pie(labels=labels, values=values, marker=dict(colors=color))])
        fig2.update_layout(title_text=title,
                              title_x=0.2,
                              title_font_size = 23,
                              uniformtext_minsize=14,)
        st.plotly_chart(fig2,use_container_width=True)

        return df
    def criando_graficos_caixa_div (df,title,color):
        df['Caixa'] = df.loc[df['Produto'].isin(dividendos),'Valor Bruto'].sum()
        df['Ativos'] = df.loc[~df['Produto'].isin(dividendos),'Valor Bruto'].sum()
        df['Total Caixa Ativos'] = df['Caixa'] + df['Ativos']
        labels = ['Caixa', 'Ativos']
        values = [df['Caixa'].sum(), df['Ativos'].sum()]
        colors = cafe_colors
        fig2 = go.Figure(data=[go.Pie(labels=labels, values=values, marker=dict(colors=color))])
        fig2.update_layout(title_text=title,
                              title_x=0.2,
                              title_font_size = 23,
                              uniformtext_minsize=14,)
        st.plotly_chart(fig2,use_container_width=True)

        return df
    


    mostrar_rv_x_rf = st.toggle('Ver Proporção Renda Fixa vs Renda Variável e caixa')
    col1,col2 = st.columns(2)
 

    if mostrar_rv_x_rf:
        st.warning("Para caixa foram considerados: BTG PACT TESOURO SELIC PREV FI RF REF DI e TESOURO DIRETO - LFT")
        with col1:
            carteira_con_media_rv_rf = criando_graficos_rf_rv(carteira_con,'Conservadora',irises_colors)
            carteira_arr_media_rv_rf = criando_graficos_rf_rv(carteira_arr,'Arrojada',colors_dark10)
            carteira_inc_prevC_media_caixa = criando_graficos_caixa(carteira_INC_PREV_MOD,'Income Prev',colors_dark24)
            carteira_dividendos_caixa = criando_graficos_caixa_div(carteira_dividendos,'Dividendos',night_colors)
            carteira_smll_caixa = criando_graficos_caixa_div(carteira_small,'Small',colors_dark24)
        with col2:
            carteira_mod_media_rv_rf = criando_graficos_rf_rv(carteira_mod,'Moderada',colors_dark_rainbow)
            carteira_eqt_media_rv_rf = criando_graficos_rf_rv(carteira_equity,'Equity',cafe_colors)
            carteira_INC_media_caixa = criando_graficos_caixa(carteira_inc,'Income',colors_dark_rainbow)
            carteira_mod_prevC_media_caixa = criando_graficos_caixa(carteira_MOD_PREV_MOD,'Moderara Prev',colors_dark_brewers)


    def criando_graficos(carteira,padronizacao,titulo):

        figura = go.Figure(data=[go.Pie(
            labels=carteira['Produto'],
            values=carteira['Valor Bruto'],
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

if selecionar == 'Análise Tecnica':

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


    ativos_e_dispercoes = []
    try:
        @st.cache_resource(ttl= '2m')
        def obter_dados(ativo,start_dt,end_dt,):
            ticker_atual = yf.Ticker(ativo +'.SA').history(period='1m')['Close'].iloc[-1]
            data = yf.download(ativo+'.SA',start=start_dt,end=end_dt,period='1d')
            data['Preco momento'] = ticker_atual
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
        dados['Dispersão Momento 42'] = ((dados['Preco momento'].iloc[-1]/dados['SMA 42'])-1)*100
        dados['Dispersão Momento 21'] = ((dados['Preco momento'].iloc[-1]/dados['SMA 21'])-1)*100
        dados['Dispersão Maxima 42'] = dados['Dispersão Momento 42'].max()
        dados['Dispersão Minima 42'] = dados['Dispersão Momento 42'].min()
        dados['Dispersão Maxima 21'] = dados['Dispersão Momento 21'].max()
        dados['Dispersão Minima 21'] = dados['Dispersão Momento 21'].min()
        dados['Dispersão Media 42'] = dados['Dispersão Momento 42'].mean()
        dados['Dispersão Media 21'] = dados['Dispersão Momento 21'].mean()

        with st.sidebar:
            if st.toggle(f'Ver grafico {ativos}',key=f'{ativos}+1'):
                st.warning(f"Ativo : {ativos} Preço :{dados['Adj Close'].iloc[-1]:,.2f}")
                st.warning(f"Ativo : {ativos} ----Média de 42 periodos :{dados['SMA 42'].iloc[-1]:,.2f},---Dispersão maxima : {dados['Dispersão 42 periodos'].max()*100:,.2f}---%Dispersão minima : {dados['Dispersão 42 periodos'].min()*100:,.2f}%---Dispersão media : {dados['Dispersão 42 periodos'].mean()*100:,.2f}%---Disperção atual :{dados['Dispersão Momento 42'].iloc[-1]*100:,.2f}%")
                st.warning(f"Ativo : {ativos} ---- Média de 21 periodos :{dados['SMA 21'].iloc[-1]:,.2f},--- Dispersão maxima : {dados['Dispersão 21 periodos'].max()*100:,.2f}%,--- Dispersão minima : {dados['Dispersão 21 periodos'].min()*100:,.2f}%---Dispersão media  : {dados['Dispersão 21 periodos'].mean()*100:,.2f}%----  Disperção  atual :{dados['Dispersão Momento 21'].iloc[-1]*100:,.2f}%")
                

                graficos = go.Figure()
                graficos.add_trace(go.Candlestick(x=dados.index,
                                                open=dados['Open'],
                                                high=dados['High'],
                                                low=dados['Low'],
                                                close=dados['Close'],
                                                name=f"{ativos}"))
                #graficos.add_trace(go.Scatter(x=dados.index, y=dados['Adj Close'], mode='lines', line=dict(width=3,color='orange'), name=f'{ativos} - Preço'))
                graficos.add_trace(go.Scatter(x=dados.index, y=dados['SMA 42'], mode='lines', name=f'{ativos} - SMA 42'))
                graficos.add_trace(go.Scatter(x=dados.index, y=dados['SMA 21'], mode='lines', name=f'{ativos} - SMA 21'))

                graficos.update_layout(title=f'{ativos} - Metrics Comparison',
                                    xaxis_title='Data',
                                    yaxis_title='Valor',
                                    legend=dict(x=0, y=1, traceorder='normal'))

                st.plotly_chart(graficos,use_container_width=True)
        ativos_e_dispercoes.append(dados.iloc[-1,:])    


    df_final = pd.DataFrame(ativos_e_dispercoes).reset_index()
    df_final['Avisos'] = ''
    print(df_final.info())
    df_final = df_final.iloc[:,[8,-1,7,9,10,14,13,15,17,16,18,19,20]]
    df_final=df_final.rename(columns={
        'Preco momento':'Cotação',
        'Dispersão Momento 21':'Dispersão 21',
        'Dispersão Momento 42':'Dispersão 42'
    })
    colunas_df_final = ['Cotação','Dispersão 21', 'Dispersão 42',
        'Dispersão Maxima 42', 'Dispersão Maxima 21', 'Dispersão Minima 42',
        'Dispersão Minima 21', 'Dispersão Media 42', 'Dispersão Media 21','SMA 42','SMA 21']
    
    colocar_simbolo_percent = ['Dispersão 21', 'Dispersão 42',
        'Dispersão Maxima 42', 'Dispersão Maxima 21', 'Dispersão Minima 42',
        'Dispersão Minima 21', 'Dispersão Media 42', 'Dispersão Media 21']

    for coluna in colunas_df_final:
        #df_final[coluna] = df_final[coluna].abs()
        df_final[coluna] = df_final[coluna].map("{:,.2f}".format)
  
    

    df_final['Avisos'] = np.where(df_final['Cotação']<df_final['SMA 42'],'ATENÇÃO','AGUARDE')
    df_final['Avisos'] = np.where(df_final['Cotação']<df_final['SMA 21'],'ATENÇÃO','AGUARDE')
    df_final['Avisos'] = np.where(df_final['Dispersão 42'].iloc[-1]>df_final['Dispersão Maxima 42'].iloc[-1],'VENDA',df_final['Avisos'])
    df_final['Avisos'] = np.where(df_final['Dispersão 21'].iloc[-1]>df_final['Dispersão Maxima 21'].iloc[-1],'VENDA',df_final['Avisos'])
    df_final['Avisos'] = np.where(df_final['Dispersão 42'].iloc[-1]<df_final['Dispersão Minima 42'].iloc[-1],'COMPRA',df_final['Avisos'])
    df_final['Avisos'] = np.where(df_final['Dispersão 21'].iloc[-1]<df_final['Dispersão Minima 21'].iloc[-1],'COMPRA',df_final['Avisos'])

    #df_final['Dispersão 21'].at[]

    cores = {'COMPRA':'background-color: green',
            'VENDA':'background-color: red',
            'AGUARDE':'background-color: yellow',
            'ATENÇÃO':'background-color: orange',
            '':'background-color: DarkCyan'}


    print(df_final)

    for coluna in colocar_simbolo_percent:
        df_final[coluna] = df_final[coluna].astype(str).map(lambda x: x+" %") 
    st.dataframe(df_final.style.applymap(lambda x: cores[x], subset=['Avisos']),use_container_width=True)




pl = pl_original.copy()
controle = controle_original.copy()
saldo = saldo_original.copy()
arquivo1 = posicao_original.copy()
produtos = produtos_original.copy()
curva_base = cura_original.copy()
curva_inflacao_copia = curva_de_inflacao.copy()
posicao_btg = posicao_btg1.copy()
planilha_controle = planilha_controle1.copy()
controle_co_admin = co_admin.copy()

if selecionar == 'Carteiras Co Admin':


    class Carteiras_co_admin():
        def __init__(self,pl,controle_co_admin,saldo):
            self.pl = pl
            self.controle_co = controle_co_admin
            self.saldo = saldo

        def juntando_planilhas(self):
            arquivo_final = pd.merge(self.pl,self.saldo, on='Conta',how='outer')  
            controle_co_admin['Conta'] = self.controle_co['Conta'].astype(str).str[:-2].apply(lambda x: '00'+ x)
            controle_co_admin_df = pd.DataFrame(controle_co_admin)
            arquivo_final_completo = pd.merge(arquivo_final,controle_co_admin_df,on
                                              ='Conta',how='right').iloc[:-5,[0,2,4,6,10,16,11,20,21,22,-1]].rename(columns={'Valor':'PL'})
            coluna_final = arquivo_final_completo.columns[-1]

            arquivo_final_completo = arquivo_final_completo.rename(columns={coluna_final:'PL Planilha Controle'}).iloc[:,[0,2,3,5,6,7,8,1,4,9,10]]

            return arquivo_final_completo

    if __name__=='__main__':
    
        ler_arquivos = Carteiras_co_admin(pl,controle_co_admin,saldo)            
        dados_agregados = ler_arquivos.juntando_planilhas()
        print(dados_agregados)
        st.dataframe(dados_agregados)

    print(controle_co_admin.info())        
t1 = time.perf_counter()

print(t1-t0)






