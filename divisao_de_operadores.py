import pandas as pd
import numpy as np
import streamlit as st


class Divisao_de_contas():
    def __init__(self):
        print('O programa iniciou')


    def limpando_dados(self):
        self.controle = pd.read_excel(r'C:\Users\lauro.telles\Desktop\Mesa_app_3\controle.xlsx')
        self.saldo = pd.read_excel(r'C:\Users\lauro.telles\Desktop\Mesa_app_3\Saldo.xlsx')
        self.pl = pd.read_excel(r'C:\Users\lauro.telles\Desktop\Mesa_app_3\PL Total.xlsx')

        
        self.controle = self.controle.iloc[:-5,[1,2,6,7,12,16,17,18,-1]].drop(0).rename(columns={
            'Unnamed: 1':'Nome','Unnamed: 2':'Conta','Mesa de Operação':'Operador','Backoffice/ Mesa':'Status','Unnamed: 12':'Perfil da carteira',
            'Mesa de Operação.1':'Avisos Mesa','Gestão/ Head comercial':'Avisos comercial','Backoffice.2 ':'Avisos Backoffice','Unnamed: 80':'PL Controle'
        })
        self.controle['Conta'] = self.controle['Conta'].astype(str).apply(lambda x: '00'+x)

        self.saldo = pd.read_excel(r'C:\Users\lauro.telles\Desktop\Mesa_app_3\Saldo.xlsx').iloc[:,[0,2]]
        self.pl = pd.read_excel(r'C:\Users\lauro.telles\Desktop\Mesa_app_3\PL Total.xlsx').iloc[:,[0,2]]

        self.arquivo_compilado = pd.merge(self.saldo,self.pl,on='Conta',how='outer').merge(self.controle,on='Conta',how='outer').iloc[:,[0,3,1,5,6,7,8,9,10,2,4]]
        return self.arquivo_compilado       

    def filtrando_dados_e_separando_operadores(self,arquivo_compilado):

        self.arquivo_compilado = arquivo_compilado

        self.filtrando_saldo = self.arquivo_compilado.loc[(self.arquivo_compilado['Saldo']>1000)|(self.arquivo_compilado['Saldo']<0)].sort_values(by='Saldo',ascending=False)

        self.filtrando_saldo.loc[(self.filtrando_saldo['Valor']>250000) & (self.filtrando_saldo['Operador'] == 'Bruno'),'Operador'] = 'Bruno'
        self.filtrando_saldo.loc[(self.filtrando_saldo['Valor']<250000) & (self.filtrando_saldo['Operador'] == 'Bruno'),'Operador'] = 'Breno'
        self.filtrando_saldo.loc[(self.filtrando_saldo['Valor']>200000) & (self.filtrando_saldo['Operador'] == 'Léo'),'Operador'] = 'Léo'
        self.filtrando_saldo.loc[(self.filtrando_saldo['Valor']<200000) & (self.filtrando_saldo['Operador'] == 'Léo'),'Operador'] = 'Augusto'

        self.filtrando_saldo.loc[(self.filtrando_saldo['Valor']>200000) & (self.filtrando_saldo['Operador'] == 'Augusto'),'Operador'] = 'Léo'
        self.filtrando_saldo.loc[(self.filtrando_saldo['Valor']>250000) & (self.filtrando_saldo['Operador'] == 'Breno'),'Operador'] = 'Bruno'
        colunas_ajustar_decimal = ['Saldo','PL Controle','Valor']
        for coluna in colunas_ajustar_decimal:
            self.filtrando_saldo[coluna] = self.filtrando_saldo[coluna].apply(lambda x: '{:,.2f}'.format(x))

        self.filtrando_saldo = self.filtrando_saldo[self.filtrando_saldo['Operador'].notnull()]
        return self.filtrando_saldo
        

    def contas_nao_encontradas(self,arquivo_compilado):
        
        self.contas_nao_encontrados = arquivo_compilado[(arquivo_compilado['Operador'].isnull())&(arquivo_compilado['Saldo']>1000)]
        return self.contas_nao_encontrados


