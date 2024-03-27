import pandas as pd
import numpy as np
import streamlit as st
from functools import reduce

# equities = {'ARZZ3': 5,'ASAI3':6.50,'BBSE3':5,'CPFE3':5.50,'EGIE3':5.50,'HYPE3':8.00,'KEPL3':8.75,
#             'LEVE3':5,'PRIO3':8,'PSSA3':2.50,'SBSP3':4,'SLCE3':7,'VALE3':10,'VIVT3':5,'Caixa':14.25}
equities = {'Renda Variável': 85.75,'Pós-fixado':14.25}

income = {'Pós-fixado':15,'Inflação':38,'Pré-fixado':44,'FundoDI':3}

small_caps = {'BPAC11':10,'ENEV3':4,'HBSA3':7,'IFCM3':5,'IFCM3':5,'JALL3':10,'KEPL3':12,'MYPK3':5,'PRIO3':12,'SIMH3':8,'TASA4':8,'TUPY3':11,'WIZC3':5}

dividendos = {'TAEE11':9,'VIVT3':12,'BBSE3':17, 'ABCB4':16,' VBBR3':15,' CPLE6':16,' TRPL4':5}

fii = {'BTLG11':22.30,'Caixa':6,'HGLG11':22.30,'KNCA11':7.25,'MALL11':7.75,'PLCR11':13.57,'RURA11':7.26,'TRXF11':13.57}

lista_acoes_em_caixa = [ 'ARZZ3', 'ASAI3', 'BBSE3', 'CPFE3', 'EGIE3','HYPE3', 'KEPL3', 'LEVE3', 'PRIO3', 'PSSA3', 'SBSP3', 'VIVT3', 'SLCE3', 'VALE3',]


conservadora = {'Pós-fixado':8.50,'Inflação':34.43,'Pré-fixado':39.53,'FundoDI':2.55, 'Renda Variável':15}
moderada = {'Pós-fixado':7,'Inflação':28.35,'Pré-fixado':32.55,'FundoDI':2.10, 'Renda Variável':30}
arrojada = {'Pós-fixado':5,'Inflação':20.25,'Pré-fixado':23.25,'FundoDI':1.50, 'Renda Variável':45}

controle = pd.read_excel(r'C:\Users\lauro.telles\Desktop\Mesa_app_3\app_mesa_de_opera-es_corrigido\controle.xlsx',skiprows=1).iloc[:,[2,12]]
controle['Conta'] = controle['Conta'].astype(str).apply(lambda x: '00'+x).str[:-2]


posicao = pd.read_excel(r'C:\Users\lauro.telles\Desktop\Mesa_app_3\app_mesa_de_opera-es_corrigido\Posição.xlsx')
posicao = posicao.loc[~posicao['Produto'].str.contains('PREV').fillna(True)]
posicao = posicao.loc[~posicao['Produto'].str.contains('COE').fillna(True)]

posicao = posicao.groupby(['Conta','Estratégia'])['Valor Líquido'].sum().reset_index()
pl_das_contas = posicao.groupby('Conta')['Valor Líquido'].sum().reset_index()
posicao = posicao.merge(pl_das_contas,on='Conta',how='outer').merge(controle,on='Conta',how='outer')
posicao['Posicao Porcentagem'] = round((posicao['Valor Líquido_x']/posicao['Valor Líquido_y'])*100,2)

def criando_carteiras(carteira,proporcao_e_ativos):
    
    carteira = pd.DataFrame(list(proporcao_e_ativos.items()),columns=[f'Ativo','Proporção'])
    # carteira[f'Proporção__{carteira}'] = carteira['Proporção']
    # carteira = carteira.drop(columns='Proporção')
    return carteira


carteira_equity = criando_carteiras('Carteira_equity',equities)
carteira_income = criando_carteiras('Carteira Income',income)
carteira_small = criando_carteiras('Carteira Small',small_caps)
carteira_dividendos = criando_carteiras('Carteira Dividendos',dividendos)
carteira_fii = criando_carteiras('Carteira FII', fii)
carteira_conservadora = criando_carteiras('Carteira CON',conservadora)
carteira_moderada = criando_carteiras('Carteira MOD', moderada)
carteira_arrojada = criando_carteiras('Carteira ARR',arrojada)



posicao_income = posicao[posicao['Carteira']=='INC']
posicao_con = posicao[posicao['Carteira']=='CON']
posicao_mod = posicao[posicao['Carteira']=='MOD']
posicao_arr = posicao[posicao['Carteira']=='ARR']
posicao_eqt = posicao[posicao['Carteira']=='EQT']

posicao_income = posicao_income.merge(carteira_income,left_on='Estratégia',right_on='Ativo').rename(columns={'Ativo':'Ativo_Income'})
posicao_con = posicao_con.merge(carteira_conservadora,left_on='Estratégia',right_on='Ativo').rename(columns={'Ativo':'Ativo_Con'})
posicao_mod = posicao_mod.merge(carteira_moderada,left_on='Estratégia',right_on='Ativo').rename(columns={'Ativo':'Ativo_Mod'})
posicao_arr = posicao_arr.merge(carteira_arrojada,left_on='Estratégia',right_on='Ativo').rename(columns={'Ativo':'Ativo_Arr'})
posicao_eqt = posicao_eqt.merge(carteira_equity,left_on='Estratégia',right_on='Ativo').rename(columns={'Ativo':'Ativo_Eqt'})

dfs_checar_enquadramento = [posicao_income,posicao_con,posicao_mod,posicao_arr,posicao_eqt]
for dataframe in dfs_checar_enquadramento:
    dataframe['Enquadramento'] = dataframe['Posicao Porcentagem']-dataframe['Proporção']

arquivo_final = pd.concat(dfs_checar_enquadramento)

arquivo_final = arquivo_final[(arquivo_final['Enquadramento']>10)|(arquivo_final['Enquadramento']<-10)].reset_index().drop(columns='index')



st.dataframe(arquivo_final)
st.dataframe(posicao_eqt)
