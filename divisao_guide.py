import pandas as pd
import numpy as np
import streamlit as st
class Guide_Divisao_contas():
    def __init__(self):
        print('Hello World')

    def trabalhando_dados(self,controle_g,pl,saldo):

        self.controle = controle_g
        self.pl = pl 
        self.saldo = saldo

        self.controle = self.controle.iloc[:,[1,2,6,7,8,12,19,20,21,-1]]
        self.pl = self.pl.iloc[:,[1,11]].rename(columns={'CLIE_ID':'Conta','SALDO_BRUTO':'PL'})
        self.pl = self.pl.groupby('Conta')['PL'].sum().reset_index()
        self.saldo = self.saldo.iloc[:,[2,5]].rename(columns={'Cod. Conta Local':'Conta','Saldo Previsto':'Saldo'})
        self.pl['Conta'] = self.pl['Conta'].astype(str)
        self.saldo['Conta'] = self.saldo['Conta'].astype(str)
        self.controle['Conta'] = self.controle['Conta'].str[:-1]

        self.arquivo_final = pd.merge(self.controle,self.pl, on='Conta',how='outer')
        self.arquivo_final = self.arquivo_final.merge(self.saldo,on='Conta',how='outer')

        return self.arquivo_final

    def dividindo_contas(self,arquivo_final):
        arquivo_compilado = arquivo_final


        self.dividindo_operadores = arquivo_compilado.loc[(arquivo_compilado['Saldo']>1000)|(arquivo_compilado['Saldo']<0)].sort_values(by='Saldo',ascending=False)

        self.dividindo_operadores.loc[self.dividindo_operadores['PL']>700000, 'Operador'] = 'Bruno'
        self.dividindo_operadores.loc[(self.dividindo_operadores['PL'] > 400000) & (self.dividindo_operadores['PL'] < 700000), 'Operador'] = 'Breno'
        self.dividindo_operadores.loc[self.dividindo_operadores['PL']<400000, 'Operador'] = 'Augusto'
        colunas_ajustar_decimal = ['Saldo','PL']
        contas_co_admin = ['005338054','004313254','005190138','004724018','004641487','004643737','004855570','004855596','004643746','005320069','004884046','005053939']
        self.dividindo_operadores = self.dividindo_operadores[~self.dividindo_operadores['Conta'].isin(contas_co_admin)]

        for coluna in colunas_ajustar_decimal:
            self.dividindo_operadores[coluna] = self.dividindo_operadores[coluna].apply(lambda x: '{:,.2f}'.format(x))

        self.dividindo_operadores = self.dividindo_operadores[self.dividindo_operadores['Operador'].notnull()]

        return self.dividindo_operadores
    
    def contas_nao_encontradas(self,arquivo_compilado):
        contas_co_admin = ['005190138','004724018','004641487','004643737','004855570','004855596','004643746','005320069','004884046','005053939']
        self.contas_nao_encontrados = arquivo_compilado[(arquivo_compilado['Operador'].isnull())&(arquivo_compilado['Saldo']>1000)|(arquivo_compilado['Saldo']<0)]
        self.contas_nao_encontrados = self.contas_nao_encontrados[~self.contas_nao_encontrados['Conta'].isin(contas_co_admin)]
        return self.contas_nao_encontrados

    def contando_oepradores(self,arquivo_compilado):
        self.arquivo_compilado = arquivo_compilado
        self.arquivo_compilado.loc[self.arquivo_compilado['PL']>700000, 'Operador'] = 'Bruno'
        self.arquivo_compilado.loc[(self.arquivo_compilado['PL'] > 400000) & (self.arquivo_compilado['PL'] < 700000), 'Operador'] = 'Breno'
        self.arquivo_compilado.loc[self.arquivo_compilado['PL']<400000, 'Operador'] = 'Augusto'
        
        return self.arquivo_compilado
                





