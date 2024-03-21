import pandas as pd
import numpy as np
import streamlit as st
class Guide_Divisao_contas():
    def __init__(self):
        print('Hello World')

    def trabalhando_dados(self):

        controle = pd.read_excel(r'C:\Users\lauro.telles\Desktop\Mesa_app_3\app_mesa_de_opera-es_corrigido\Controle de Contratos - Atualizado Fevereiro de 2024 (5).xlsx',3,skiprows=1)

        pl = pd.read_excel(r'C:\Users\lauro.telles\Desktop\Mesa_app_3\app_mesa_de_opera-es_corrigido\Bluemetrix20240318_ABS.xlsx')

        saldo = pd.read_excel(r'C:\Users\lauro.telles\Desktop\Mesa_app_3\app_mesa_de_opera-es_corrigido\IClientBalance-20240321-110159-af1ee8.xlsx',)

        controle = controle.iloc[:,[1,2,6,7,8,12,19,20,21,-1]]
        pl = pl.iloc[:,[1,11]].rename(columns={'CLIE_ID':'Conta','SALDO_BRUTO':'PL'})
        pl = pl.groupby('Conta')['PL'].sum().reset_index()
        saldo = saldo.iloc[:,[2,5]].rename(columns={'Cod. Conta Local':'Conta','Saldo Previsto':'Saldo'})
        pl['Conta'] = pl['Conta'].astype(str)
        saldo['Conta'] = saldo['Conta'].astype(str)
        controle['Conta'] = controle['Conta'].str[:-1]

        self.arquivo_final = pd.merge(controle,pl, on='Conta',how='outer')
        self.arquivo_final = self.arquivo_final.merge(saldo,on='Conta',how='outer')

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
                
# if __name__=='__main__':

#     iniciando = Guide_Divisao_contas()
#     arquivo_final = iniciando.trabalhando_dados()
#     dividindo_operadores = iniciando.dividindo_contas(arquivo_final=arquivo_final)
#     contas_nao_contradas = iniciando.contas_nao_encontradas(arquivo_compilado=arquivo_final)
#     contando_operadoress = iniciando.contando_oepradores(arquivo_final)

#     col1,col2 = st.columns(2)
#     st.text(f"{dividindo_operadores['Operador'].value_counts().to_string()}")
#     with col1:
#         seletor_operador = st.selectbox('Operadores',options=dividindo_operadores['Operador'].unique())
#         dividindo_operadores = dividindo_operadores.loc[dividindo_operadores['Operador']==seletor_operador] 



#     cores = {'Inativo':'background-color: yellow',
#             'Ativo':'background-color: green',
#             'Pode Operar':'background-color: green',
#             'Checar conta':'background-color: red',
#             'Encerrado':'background-color: #A0522D',
#             np.nan:'background-color: #A0522D'}
        
    
#     st.dataframe(dividindo_operadores.style.applymap(lambda x: cores[x], subset=['Status']),use_container_width=True)
#     st.subheader('Checar contas')
#     st.dataframe(contas_nao_contradas)
#     st.text(f" Contagem Total de clientes por {contando_operadoress['Operador'].value_counts().to_string()}")




