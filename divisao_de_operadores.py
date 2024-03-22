import pandas as pd
import numpy as np
import streamlit as st



class Divisao_de_contas():
    def __init__(self):
        print('O programa iniciou')


    def limpando_dados(self,controle,saldo,pl):
        self.controle = controle
        self.saldo = saldo
        self.pl =  pl

        
        self.controle = self.controle.iloc[:-5,[1,2,6,7,12,16,17,18,-1]].rename(columns={
            'Unnamed: 1':'Nome','Unnamed: 2':'Conta','Mesa de Operação':'Operador','Backoffice/ Mesa':'Status','Unnamed: 12':'Perfil da carteira',
            'Mesa de Operação.1':'Avisos Mesa','Gestão/ Head comercial':'Avisos comercial','Backoffice.2 ':'Avisos Backoffice','Unnamed: 80':'PL Controle'
        })
        self.controle['Conta'] = self.controle['Conta'].astype(str).apply(lambda x: '00'+x).str[:-2]

        self.saldo = saldo.iloc[:,[0,2]]
        self.pl = pl.iloc[:,[0,2]]

        self.arquivo_compilado = pd.merge(self.saldo,self.pl,on='Conta',how='outer').merge(self.controle,on='Conta',how='outer').iloc[:,[0,3,1,5,6,7,8,9,10,2,4]]

        return self.arquivo_compilado       
        
    def filtrando_dados_e_separando_operadores(self,arquivo_compilado):

        self.arquivo_compilado = arquivo_compilado

        self.filtrando_saldo = self.arquivo_compilado.loc[(self.arquivo_compilado['Saldo']>1000)|(self.arquivo_compilado['Saldo']<0)].sort_values(by='Saldo',ascending=False)

        self.filtrando_saldo.loc[self.filtrando_saldo['Valor']>700000, 'Operador'] = 'Bruno'
        self.filtrando_saldo.loc[(self.filtrando_saldo['Valor'] > 400000) & (self.filtrando_saldo['Valor'] < 700000), 'Operador'] = 'Breno'
        self.filtrando_saldo.loc[self.filtrando_saldo['Valor']<400000, 'Operador'] = 'Augusto'
        colunas_ajustar_decimal = ['Saldo','Valor']
        contas_co_admin = ['005338054','004313254','005190138','004724018','004641487','004643737','004855570','004855596','004643746','005320069','004884046','005053939']
        self.filtrando_saldo = self.filtrando_saldo[~self.filtrando_saldo['Conta'].isin(contas_co_admin)]

        for coluna in colunas_ajustar_decimal:
            self.filtrando_saldo[coluna] = self.filtrando_saldo[coluna].apply(lambda x: '{:,.2f}'.format(x))

        self.filtrando_saldo = self.filtrando_saldo[self.filtrando_saldo['Operador'].notnull()]
        return self.filtrando_saldo
        

    def contas_nao_encontradas(self,arquivo_compilado):
        contas_co_admin = ['005190138','004724018','004641487','004643737','004855570','004855596','004643746','005320069','004884046','005053939']
        self.contas_nao_encontrados = arquivo_compilado[(arquivo_compilado['Operador'].isnull())&(arquivo_compilado['Saldo']>1000)|(arquivo_compilado['Saldo']<0)]
        self.contas_nao_encontrados = self.contas_nao_encontrados[~self.contas_nao_encontrados['Conta'].isin(contas_co_admin)]
        return self.contas_nao_encontrados

    def contando_oepradores(self,arquivo_compilado):
        self.arquivo_compilado = arquivo_compilado
        self.arquivo_compilado = self.arquivo_compilado[self.arquivo_compilado['Status']=='Inativo']
        self.arquivo_compilado.loc[self.arquivo_compilado['Valor']>700000, 'Operador'] = 'Bruno'
        self.arquivo_compilado.loc[(self.arquivo_compilado['Valor'] > 400000) & (self.arquivo_compilado['Valor'] < 700000), 'Operador'] = 'Breno'
        self.arquivo_compilado.loc[self.arquivo_compilado['Valor']<400000, 'Operador'] = 'Augusto'

        return self.arquivo_compilado
        
