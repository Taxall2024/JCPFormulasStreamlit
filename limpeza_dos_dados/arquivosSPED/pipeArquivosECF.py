import pandas as pd
import streamlit as st
import functools
import numpy as np
from calendar import monthrange

class SpedProcessor:
    def __init__(self, file_paths):
        self.file_paths = file_paths
        self.listaL100 = []
        self.listaL300 = []
        self.listaM300 = []
        self.listaM350 = []
        self.listaN630 = []
        self.listaN670 = []

    @functools.cache
    def lendoELimpandoDadosSped(self, file_path):
        data = []
        with open(file_path, 'r', encoding='latin-1') as file:
            for linha in file:
                linha = linha.strip()
                if linha.startswith('|'):
                    valores = linha.split('|')[1:]
                    data.append(valores)

        df = pd.DataFrame(data).iloc[:, :13]
        df['Data Inicial'] = df.iloc[0, 9]
        df['Data Final'] = df.iloc[0, 10]
        df['Ano'] = df['Data Inicial'].astype(str).str[-4:]
        df['CNPJ'] = df.iloc[0, 3]
        df['Período Apuração'] = None
        df['Período Apuração Trimestral'] = None
        df['Data Inicial'] = pd.to_datetime(df['Data Inicial'], format='%d%m%Y').dt.strftime('%d/%m/%Y')
        df['Data Final'] = pd.to_datetime(df['Data Final'], format='%d%m%Y').dt.strftime('%d/%m/%Y')
        
        return df

    def classificaPeriodoDeApuracao(self, arquivo, referencia):
        bloco_iniciado = False
        data_index = 0

        perido_apuracao = [
                'A01 – Balanço de Suspensão e Redução até Janeiro',
                'A02 – Balanço de Suspensão e Redução até Fevereiro',
                'A03 – Balanço de Suspensão e Redução até Março',
                'A04 – Balanço de Suspensão e Redução até Abril',
                'A05 – Balanço de Suspensão e Redução até Maio',
                'A06 – Balanço de Suspensão e Redução até Junho',
                'A07 – Balanço de Suspensão e Redução até Julho',
                'A08 – Balanço de Suspensão e Redução até Agosto',
                'A09 – Balanço de Suspensão e Redução até Setembro',
                'A10 – Balanço de Suspensão e Redução até Outubro',
                'A11 – Balanço de Suspensão e Redução até Novembro',
                'A12 – Balanço de Suspensão e Redução até Dezembro',
                'A00 – Receita Bruta/Balanço de Suspensão e Redução Anual']
        
        trimestres = ['T01 – 1º Trimestre',
                    'T02 – 2º Trimestre',
                    'T03 – 3º Trimestre',
                    'T04 – 4º Trimestre']

        for i in range(len(arquivo)):
            if arquivo.loc[i, 2] == referencia:
                if bloco_iniciado:
                    data_index += 1
                else:
                    bloco_iniciado = True

                if data_index < len(perido_apuracao):
                    arquivo.loc[i:, 'Período Apuração'] = perido_apuracao[data_index]
                    try:
                        arquivo.loc[i:, 'Período Apuração Trimestral'] = trimestres[data_index] 
                    except:
                        pass
        return arquivo
    
    @functools.cache
    def gerandoArquivosECF(self, caminho):
        df_sped = self.lendoELimpandoDadosSped(caminho)

        df_sped_l100 = df_sped[(df_sped[0] == 'L100') | (df_sped[0] == 'N030')].reset_index(drop=True)
        df_sped_l100 = self.classificaPeriodoDeApuracao(df_sped_l100, 'ATIVO')


        df_sped_l300 = df_sped[df_sped[0] == 'L300'].reset_index(drop=True)
        df_sped_l300 = self.classificaPeriodoDeApuracao(df_sped_l300, 'RESULTADO LÍQUIDO DO PERÍODO')

        df_sped_m300 = df_sped[df_sped[0] == 'M300'].reset_index(drop=True)
        df_sped_m300 = self.classificaPeriodoDeApuracao(df_sped_m300, 'ATIVIDADE GERAL')

        df_sped_m350 = df_sped[df_sped[0] == 'M350'].reset_index(drop=True)
        df_sped_m350 = self.classificaPeriodoDeApuracao(df_sped_m350, 'ATIVIDADE GERAL')

        df_sped_n630 = df_sped[df_sped[0] == 'N630'].reset_index(drop=True)
        df_sped_n630['Período Apuração'] = 'A00 – Receita Bruta/Balanço de Suspensão e Redução Anual'

        df_sped_n670 = df_sped[df_sped[0] == 'N670'].reset_index(drop=True)
        df_sped_n670['Período Apuração'] = 'A00 – Receita Bruta/Balanço de Suspensão e Redução Anual'

        return df_sped_l100, df_sped_l300, df_sped_m300, df_sped_m350, df_sped_n630, df_sped_n670

    def processar_arquivos(self):
        for file_path in self.file_paths:
            df_sped_l100, df_sped_l300, df_sped_m300, df_sped_m350, df_sped_n630, df_sped_n670 = self.gerandoArquivosECF(file_path)
            self.listaL100.append(df_sped_l100)
            self.listaL300.append(df_sped_l300)
            self.listaM300.append(df_sped_m300)
            self.listaM350.append(df_sped_m350)
            self.listaN630.append(df_sped_n630)
            self.listaN670.append(df_sped_n670)
    @functools.cache
    def concatenar_dfs(self):
        L100_final = pd.concat(self.listaL100).reset_index(drop=True).rename(columns={
            1: 'Conta Referencial', 2: 'Descrição Conta Referencial', 3: "Tipo Conta", 4: 'Nível Conta',
            5: 'Natureza Conta', 6: 'Conta Superior', 8: 'D/C Saldo Final', 11: 'Vlr Saldo Final'}).drop(columns=[7, 9, 10, 0])
        L100_final = L100_final[['CNPJ', 'Data Inicial', 'Data Final', 'Ano', 'Período Apuração','Período Apuração Trimestral',
                                 'Conta Referencial', 'Conta Superior', 'Descrição Conta Referencial',
                                 'Natureza Conta', 'Tipo Conta', 'Nível Conta', 'Vlr Saldo Final', 'D/C Saldo Final']]

        L300_final = pd.concat(self.listaL300).reset_index(drop=True).rename(columns={
            1: "Conta Referencial", 2: 'Descrição Conta Referencial', 3: 'Tipo Conta', 4: "Nível Conta",
            5: 'Natureza Conta', 6: 'Conta Superior', 7: 'Vlr Saldo Final', 8: 'D/C Saldo Final'})
        L300_final = L300_final[['CNPJ', 'Data Inicial', 'Data Final', 'Ano', 'Período Apuração','Período Apuração Trimestral',
                                 'Conta Referencial', 'Conta Superior', 'Descrição Conta Referencial',
                                 'Natureza Conta', 'Tipo Conta', 'Nível Conta', 'Vlr Saldo Final', 'D/C Saldo Final']]

        M300_final = pd.concat(self.listaM300).reset_index(drop=True).rename(columns={
            1: 'Código Lançamento e-Lalur', 2: 'Descrição Lançamento e-Lalur', 3: 'Tipo Lançamento',
            4: 'Indicador Relação Parte A', 5: 'Vlr Lançamento e-Lalur', 6: 'Histórico e-Lalur'})
        M300_final = M300_final[['CNPJ', 'Data Inicial', 'Data Final', 'Ano', 'Período Apuração','Período Apuração Trimestral',
                                 'Código Lançamento e-Lalur', 'Descrição Lançamento e-Lalur', 'Tipo Lançamento',
                                 'Indicador Relação Parte A', 'Vlr Lançamento e-Lalur']]

        M350_final = pd.concat(self.listaM350).reset_index(drop=True).rename(columns={
            1: 'Código Lançamento e-Lacs', 2: 'Descrição Lançamento e-Lacs', 4: 'Indicador Relação Parte A',
            5: 'Vlr Lançamento e-Lacs', 6: 'Histórico e-Lacs'})
        M350_final = M350_final[['CNPJ', 'Data Inicial', 'Data Final', 'Ano', 'Período Apuração','Período Apuração Trimestral',
                                 'Código Lançamento e-Lacs', 'Descrição Lançamento e-Lacs',
                                 'Indicador Relação Parte A', 'Vlr Lançamento e-Lacs', 'Histórico e-Lacs']]

        N630_final = pd.concat(self.listaN630).reset_index(drop=True).rename(columns={
            1: 'Código Lançamento', 2: "Descrição Lançamento", 3: 'Vlr Lançamento'})
        N630_final = N630_final[['CNPJ', 'Data Inicial', 'Data Final', 'Ano', 'Período Apuração','Período Apuração Trimestral',
                                 'Código Lançamento', 'Descrição Lançamento', 'Vlr Lançamento']]

        N670_final = pd.concat(self.listaN670).reset_index(drop=True).rename(columns={
            1: 'Código Lançamento', 2: 'Descrição Lançamento', 3: "Vlr Lançamento"})
        N670_final = N670_final[['CNPJ', 'Data Inicial', 'Data Final', 'Ano', 'Período Apuração','Período Apuração Trimestral',
                                 'Código Lançamento', 'Descrição Lançamento', 'Vlr Lançamento']]

        return {
            "L100": L100_final,
            "L300": L300_final,
            "M300": M300_final,
            "M350": M350_final,
            "N630": N630_final,
            "N670": N670_final
        }

# #Exemplo de uso da classe
# if __name__=='__main__':

#     st.title('Processamento de Arquivos SPED')
#     anualOuTrimestral = st.sidebar.selectbox("Anual ou Trimestral", ["Ano", 'Trimestre'])  
#     uploaded_files = st.file_uploader("Escolha os arquivos SPED", type=['txt'], accept_multiple_files=True)

#     if uploaded_files:
#         file_paths = []
#         for uploaded_file in uploaded_files:
#             file_path = uploaded_file.name
#             with open(file_path, 'wb') as f:
#                 f.write(uploaded_file.getbuffer())
#             file_paths.append(file_path)

#         sped_processor = SpedProcessor(file_paths)
#         sped_processor.processar_arquivos()
#         dfs_concatenados = sped_processor.concatenar_dfs()

#         # Acesso aos DataFrames processados
#         L100_final = dfs_concatenados["L100"]
#         L300_final = dfs_concatenados["L300"]
#         M300_final = dfs_concatenados["M300"]
#         M350_final = dfs_concatenados["M350"]
#         N630_final = dfs_concatenados["N630"]
#         N670_final = dfs_concatenados["N670"]

#         st.dataframe(L100_final)
#         st.dataframe(L300_final)
#         st.dataframe(M300_final)
#         st.dataframe(M350_final)
#         st.dataframe(N630_final)
#         st.dataframe(N670_final)
#         #Adicione exibição dos outros DataFrames se necessário






