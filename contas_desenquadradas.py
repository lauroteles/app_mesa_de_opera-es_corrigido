import pandas as pd
import numpy as np
import streamlit as st

equities = {'ARZZ3': 5,'ASAI3':6.50,'BBSE3':5,'CPFE3':5.50,'EGIE3':5.50,'EZTC3':6.50,'HYPE3':8.00,'KEPL3':8.75,
            'LEVE3':5,'PRIO3':8,'PSSA3':2.50,'SBSP3':4,'SLCE3':9.75,'VALE3':10,'VIVT3':5,'Caixa':5}

income = {'POS':15,'Inflação':38,'PRE':44,'FundoDI':3}

small_caps = {'BPAC11':10,'ENEV3':4,'HBSA3':7,'IFCM3':5,'IFCM3':5,'JALL3':10,'KEPL3':12,'MYPK3':5,'PRIO3':12,'SIMH3':8,'TASA4':8,'TUPY3':11,'WIZC3':5}

dividendos = {'TAEE11':9,'VIVT3':12,'BBSE3':17, 'ABCB4':16,' VBBR3':15,' CPLE6':16,' TRPL4':5}

fii = {'BTLG11':22.30,'Caixa':6,'HGLG11':22.30,'KNCA11':7.25,'MALL11':7.75,'PLCR11':13.57,'RURA11':7.26,'TRXF11':13.57}

lista_acoes_em_caixa = [ 'ARZZ3', 'ASAI3', 'BBSE3', 'CPFE3', 'EGIE3', 'EZTC3', 'HYPE3', 'KEPL3', 'LEVE3', 'PRIO3', 'PSSA3', 'SBSP3', 'VIVT3', 'SLCE3', 'VALE3',]


controle = pd.read_excel(r'C:\Users\lauro.telles\Desktop\Mesa_app_3\app_mesa_de_opera-es_corrigido\controle.xlsx',skiprows=1).iloc[:,[2,12]]
controle['Conta'] = controle['Conta'].astype(str).apply(lambda x: '00'+x).str[:-2]


posicao = pd.read_excel(r'C:\Users\lauro.telles\Desktop\Mesa_app_3\app_mesa_de_opera-es_corrigido\Posição.xlsx')
posicao = posicao.groupby(['Conta','Estratégia'])['Valor Líquido'].sum().reset_index()
pl_das_contas = posicao.groupby('Conta')['Valor Líquido'].sum().reset_index()
posicao = posicao.merge(pl_das_contas,on='Conta',how='outer').merge(controle,on='Conta',how='outer')
posicao['Posicao Porcentagem'] = round((posicao['Valor Líquido_x']/posicao['Valor Líquido_y'])*100,2)

def criando_carteiras(carteira,proporcao_e_ativos):
    
    carteira = pd.DataFrame(list(proporcao_e_ativos.items()),columns=['Ativo','Proporção'])
    carteira['Proporção'] = carteira['Proporção']/100

    return carteira

def criando_carteiras_hibridas(carteira,proporcao_variavel,proporcao_fixa):
    base_de_distribuicao = {ativo:proporcao_fixa*income.get(ativo,0)+proporcao_variavel*equities.get(ativo,0) for ativo in set(income)|set(equities)}
    carteira = pd.DataFrame(list(base_de_distribuicao.items()),columns=['Ativo','Proporção'])
    carteira['Proporção'] = carteira['Proporção']/100
    return carteira

carteira_equity = criando_carteiras('Carteira_equity',equities)
carteira_income = criando_carteiras('Carteira Income',income)
carteira_small = criando_carteiras('Carteira Small',small_caps)
carteira_dividendos = criando_carteiras('Carteira Dividendos',dividendos)
carteira_fii = criando_carteiras('Carteira FII', fii)
carteira_conservadora = criando_carteiras_hibridas('Carteira Conservadora',0.15,0.85)
carteira_moderada = criando_carteiras_hibridas('Carteira Moderada',0.30,0.70)
carteira_arrojada = criando_carteiras_hibridas('Carteira Arrojada',0.50,0.50)

lista_carteiras =[carteira_equity,carteira_income,carteira_small,carteira_dividendos,carteira_fii,carteira_conservadora,carteira_moderada,carteira_arrojada]

# for carteira in lista_carteiras:
#     carteira_name = carteira['Ativo'][0]
#     posicao[carteira_name] = posicao.apply(lambda x: carteira.loc[carteira['Ativo'] == x['Produto'], 'Proporção'].iloc[0], axis=1)

st.dataframe(posicao)

