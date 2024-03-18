import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import yfinance as yf
import io
import datetime


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

class Basket_enquadramento_carteiras():
    def __init__(self):
        print("O programa iniciou")



    def criando_carteiras(self,carteira,proporcao_e_ativos):
        
        self.carteira = pd.DataFrame(list(proporcao_e_ativos.items()),columns=['Ativo','Proporção'])
        self.carteira['Proporção'] = self.carteira['Proporção']/100

        return self.carteira
    
    def criando_carteiras_hibridas(self,carteira,proporcao_variavel,proporcao_fixa):
        base_de_distribuicao = {ativo:proporcao_fixa*income.get(ativo,0)+proporcao_variavel*equities.get(ativo,0) for ativo in set(income)|set(equities)}
        self.carteira = pd.DataFrame(list(base_de_distribuicao.items()),columns=['Ativo','Proporção'])
        self.carteira['Proporção'] = self.carteira['Proporção']/100
        return self.carteira
    
    def trantamento_de_dados_posicao(self,posicao):
        planilha_posicao = pd.read_excel(posicao).iloc[:-2,[0,4,13,14]]
        posicao = planilha_posicao.groupby(['Conta','Produto','Produto'])['Valor Líquido'].sum().reset_index()
        return posicao
    
    def tratamento_de_dados_controle(self,planilha_controle):
        planilha_controle =planilha_controle.iloc[:-5,[1,2,6,7,12,16,17,18]]
        planilha_controle['Conta'] = planilha_controle['Conta'].astype(str).apply(lambda x: '00'+ x).str[:-2]
        return planilha_controle
    
    def juntando_arqeuivos(self,controle,posicao):
        planilha_controle = controle.iloc[:-5,[1,2,6,7,12,16,17,18]]
        planilha_controle['Conta'] = planilha_controle['Conta'].astype(str).apply(lambda x: '00'+ x).str[:-2]
        planilha_posicao = posicao.iloc[:-2,[0,4,13,14]]
        posicao = planilha_posicao.groupby(['Conta','Produto','Estratégia'])['Valor Líquido'].sum().reset_index()
        arquivo_final = pd.merge(planilha_controle,posicao,on='Conta',how='outer')
        return arquivo_final
    
    def selecionando_modelo_de_carteira(self,arquivo_final, carteira_arrojada, carteira_conservadora, carteira_moderada, carteira_income, carteira_equity, carteira_small, carteira_dividendos):

        if 'Carteira' in arquivo_final.columns:
            carteira_coluna = arquivo_final['Carteira'].iloc[0]
        if carteira_coluna =='CON':
            carteira_utilizada = carteira_conservadora
        if carteira_coluna == 'ARR':
            carteira_utilizada = carteira_arrojada
        if carteira_coluna =='MOD':
            carteira_utilizada = carteira_moderada
        if carteira_coluna =='INC':
            carteira_utilizada = carteira_income
        if carteira_coluna =='EQT':
            carteira_utilizada=carteira_equity
        if carteira_coluna=='SMLL':
            carteira_utilizada=carteira_small
        if carteira_coluna=='DIV':
            carteira_utilizada=carteira_dividendos
        else:
            print('')                         
        return carteira_utilizada
    
    def criando_graficos_posicao_atual(self,dados_finais):
        self.posicao_atual_da_carteira_grafico = go.Figure(data=[go.Pie(
                labels=dados_finais['Produto'],
                values=dados_finais['Valor Líquido'],
                hole=0.4,
                textinfo='label+percent',
                insidetextorientation='radial',
                textposition='outside',
                marker=dict(colors=colors_dark_brewers)
                )])
        return st.plotly_chart(self.posicao_atual_da_carteira_grafico)
    
    
    def criando_graficos_posicao_ideal(self,carteira_modelo):
        posicao_ideal_da_carteira = go.Figure(data=[go.Pie(labels=carteira_modelo['Ativo'],
                                        values=carteira_modelo['Valor R$'],
                                        hole=0.4,
                                        textinfo='label+percent',
                                        insidetextorientation='radial',
                                        textposition='outside',
                                        marker=dict(colors=colors_dark_rainbow)
                                        )])
        return st.plotly_chart(posicao_ideal_da_carteira)    
    
    def criacao_basket(self,carteira_modelo,dados_finais,input_conta):
        carteira_modelo = carteira_modelo[carteira_modelo['Ativo'].str.contains('3')]
        dados_finais = dados_finais[dados_finais['Produto'].str.contains('3')]
        basket = pd.merge(carteira_modelo.iloc[:,[0,2]],dados_finais.iloc[:,[0,2]],left_on='Ativo',right_on='Produto',how='outer')
        precos_de_mercado = []
        for ativo in lista_acoes_em_caixa:
                ticker = yf.Ticker(ativo +'.SA')
                preco_atual = ticker.history(period='2m')['Close'].iloc[-1]
            
                precos_de_mercado.append([ativo,preco_atual])

        cotacoes_momento = pd.DataFrame(precos_de_mercado,columns =['Ativo','Cotação atual'])     
        self.basket = basket.merge(cotacoes_momento,on='Ativo',how='outer').fillna(0)
        self.basket['Valor_compra_venda'] = round(self.basket['Valor R$']-self.basket['Valor Líquido'],2)
        self.basket['Quantidade'] = round(self.basket['Valor_compra_venda']/self.basket['Cotação atual'],0).abs()
        self.basket['C/V'] = np.where(self.basket['Valor_compra_venda']>0,'C','V')
        self.basket['Validade']='DIA'
        self.basket['Conta'] = input_conta
        self.basket = self.basket.rename(columns={'Cotação atual':'Preço'}).iloc[:,[0,7,6,4,9,8]]

        return self.basket
    
    def checando_estrategia(self,dados_finais):
        self.comparar_posicao_cliete_x_estrategia = posicao_atual_da_carteira_grafico = go.Figure(data=[go.Pie(
                labels=dados_finais['Estratégia'],
                values=dados_finais['Valor Líquido'],
                hole=0.4,
                textinfo='label+percent',
                insidetextorientation='radial',
                textposition='outside'
                )])
        return st.plotly_chart(self.comparar_posicao_cliete_x_estrategia)
    
    def grafico_rentabilidade(self,input_conta):
        rentabilidade = pd.read_excel('Rentabilidade (1).xlsx').iloc[:,[0,2,4,6,8,10,12,14,16,18,20,22,24]]
        rentabilidade = rentabilidade[rentabilidade['Periodo']==input_conta]
        
        rentabilidade = rentabilidade.transpose().reset_index().rename(columns={'index':'Periodo',146:'Rentabilidade'}).drop(0)
        rentabilidade['Rentabilidade acumulada'] = ((1 + rentabilidade['Rentabilidade']/100).cumprod(axis=0)-1)*10000

        grafico_retabilidade = px.line(y=rentabilidade['Rentabilidade acumulada'],x=rentabilidade['Periodo'],title='Rentabilidade')
        return  st.plotly_chart(grafico_retabilidade)
        

# if __name__=='__main__':
#     dia_e_hora = datetime.datetime.now()
#     inciando_programa = Basket_enquadramento_carteiras()
#     carteira_equity = inciando_programa.criando_carteiras('Carteira_equity',equities)
#     carteira_income = inciando_programa.criando_carteiras('Carteira Income',income)
#     carteira_small = inciando_programa.criando_carteiras('Carteira Small',small_caps)
#     carteira_dividendos = inciando_programa.criando_carteiras('Carteira Dividendos',dividendos)
#     carteira_fii = inciando_programa.criando_carteiras('Carteira FII', fii)
#     carteira_conservadora = inciando_programa.criando_carteiras_hibridas('Carteira Conservadora',0.85,0.15)
#     carteira_moderada = inciando_programa.criando_carteiras_hibridas('Carteira Moderada',0.70,0.30)
#     carteira_arrojada = inciando_programa.criando_carteiras_hibridas('Carteira Arrojada',0.50,0.50)

#     dados_finais = inciando_programa.juntando_arqeuivos()
#     trantrando_dados_controle = inciando_programa.tratamento_de_dados_controle()

#     input_conta = st.sidebar.text_input('Escreva o número da conta : ')
    
#     dados_finais = dados_finais.loc[dados_finais['Conta']==input_conta].iloc[:,[8,9,10]]

#     patrimono_liquido_da_conta = dados_finais["Valor Líquido"].sum()
#     trantrando_dados_controle = trantrando_dados_controle.loc[trantrando_dados_controle['Conta']==input_conta]

#     carteira_modelo = inciando_programa.selecionando_modelo_de_carteira(trantrando_dados_controle)
#     carteira_modelo['Valor R$'] = carteira_modelo['Proporção']*patrimono_liquido_da_conta
#     carteira_modelo['Proporção'] = carteira_modelo['Proporção'].map(lambda x: f"{x * 100:,.2f}  %")

#     try:
#         basket_ = inciando_programa.criacao_basket(carteira_modelo=carteira_modelo,dados_finais=dados_finais)
#     except:
#         pass

#     st.text(f'Patrimônio Líquido da carteira :   {dados_finais["Valor Líquido"].sum():,.2f}')
            
#     try:        
#         output4 = io.BytesIO()
#         with pd.ExcelWriter(output4, engine='xlsxwriter') as writer:basket_.to_excel(writer,sheet_name=f'Basket__{input_conta}___',index=False)
#         output4.seek(0)
#         st.download_button(type='primary',label="Basket Download",data=output4,file_name=f'basket_{input_conta}__{dia_e_hora}.xlsx',key='download_button')
#     except:
#         pass    
    
#     col1,col2 = st.columns(2)
#     with col1:
#         if st.toggle('Enquadramento da carteira'):
#                     grafico_estrategia = inciando_programa.checando_estrategia()
#         else:                    
#             posicao_atual_grafico = inciando_programa.criando_graficos_posicao_atual()
#         st.dataframe(dados_finais.sort_values(by='Produto'),use_container_width=True)
#         st.dataframe(trantrando_dados_controle.unstack(),use_container_width=True)
#         basket_compra = basket_[basket_['C/V']=='C']
#         basket_compra['Valor'] = basket_compra['Quantidade']*basket_compra['Preço']
#         basket_venda = basket_[basket_['C/V']=='V']
#         basket_venda['Valor'] = basket_venda['Quantidade']*basket_venda['Preço']
#         st.warning(f' O saldo Nescessario para Compra : {basket_compra["Valor"].sum():,.2f}')
#         st.warning(f' O saldo Nescessario para Venda : {basket_venda["Valor"].sum():,.2f}')
#         st.dataframe(basket_)

#     with col2:
#         grafico_posicao_ideal = inciando_programa.criando_graficos_posicao_ideal()
#         st.dataframe(carteira_modelo.sort_values(by='Ativo'),use_container_width=True)
#         grafico_rentabilidade = inciando_programa.grafico_rentabilidade()





