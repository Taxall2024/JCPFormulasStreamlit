
import pandas as pd
import streamlit as st
import numpy as np
from bs4 import BeautifulSoup
import xlsxwriter
from xlsxwriter import Workbook

from baseJPC.tratamentosDosDadosParaCalculo import FiltrandoDadosParaCalculo
from scrapping import ScrappingTJPL


import requests
import functools
import time




start_time = time.time()

tempoProcessamentoDasFuncoes = []

def timing(f):
    @functools.wraps(f)
    def wrap(*args, **kw):
        start_time = time.time()
        result = f(*args, **kw)
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Adiciona os resultados à lista
        tempoProcessamentoDasFuncoes.append({
            "Function": f.__name__,
            "Execution Time (s)": execution_time
        })
        
        print(f'Function {f.__name__} took {execution_time:.2f} seconds')
        return result
    return wrap



def fetch_tjlp_data():
    url = 'https://www.gov.br/receitafederal/pt-br/assuntos/orientacao-tributaria/pagamentos-e-parcelamentos/taxa-de-juros-de-longo-prazo-tjlp'
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    table_container = soup.find('table')
    dataframe = pd.read_html(str(table_container), index_col=False)[0]
    dataframe = dataframe.transpose().reset_index(drop=True).set_index(dataframe.columns[0])
    dataframe.columns = dataframe.iloc[0]
    dataframe = dataframe.iloc[1:, :].applymap(lambda x: str(x)[:-1]).applymap(lambda x: x.replace(',', '.')).applymap(lambda x: '0' if x == '' else x).replace('na', np.nan).astype(float)
    dataframe['1º Tri'] = round(dataframe[['Janeiro', 'Fevereiro', 'Março']].sum(axis=1), 2)
    dataframe['2º Tri'] = round(dataframe[['Abril', 'Maio', 'Junho']].sum(axis=1), 2)
    dataframe['3º Tri'] = round(dataframe[['Julho', 'Agosto', 'Setembro']].sum(axis=1), 2)
    dataframe['4º Tri'] = round(dataframe[['Outubro', 'Novembro', 'Dezembro']].sum(axis=1), 2)
    dataframe['Ano'] = round(dataframe[['1º Tri', '2º Tri', '3º Tri', '4º Tri']].sum(axis=1), 2)
    return dataframe


class Calculo(FiltrandoDadosParaCalculo):
    _widget_counter = 0

    @timing
    def __init__(self, data, lacs_file, lalur_file, ecf670_file, ec630_file, l100_file, l300_file):
        super().__init__(data, lacs_file, lalur_file, ecf670_file, ec630_file, l100_file, l300_file)
        
        
        self.data = data
        self.resultadoJPC = pd.DataFrame(columns=["Operation", "Value"])
        self.resultadoLimiteDedu = pd.DataFrame(columns=["Operation", "Value"])
        self.resultadoEconomiaGerada = pd.DataFrame(columns=["Operation", "Value"])
        self.csllAposInovacoes = pd.DataFrame(columns=["Operation", "Value"])

        self.dataframe = ScrappingTJPL.fetch_tjlp_data()
        self.valorJPC = 0.0

    @timing
    def valorJPCRetroativo(self):
        key = f'retroativoJCP{self.data}'

        if key not in st.session_state:
            st.session_state[key] = 0.0

        st.session_state[key] = st.session_state[key]
        self.jcpRetroativo = st.number_input('Digite o valor de JCP ja utilizado pelo cliente', key=key, value=st.session_state[key])


    @timing
    def calculandoJPC(self, data):

        lucroLiquid50 = self.lucroAntIRPJ * 0.5
        lucroAcuEReserva = (self.reservLucro + self.lucroAcumulado) * 0.5

        if data in self.dataframe.index:
            self.taxaJuros = self.dataframe.loc[data, 'Ano']
            
            if self.totalJSPC<0:
                self.valorJPC = 0
            else:    
                self.valorJPC = round(self.totalJSPC * (self.dataframe.loc[data, 'Ano'] / 100), 2)-self.jcpRetroativo
            
            # '''Formula que faz checagem se o valor de JSCP não esta passando certos limites, optei for fazer utilizando np.where porem
            # o reultado esta muito distorcido, com valores muito acima do esperado, entao vou deixar a formula de calculo simples por enquanto
            # e retornar eventualmente para implementar a formula'''

            # maior_valor = max(lucroLiquid50, lucroAcuEReserva)

            # #self.valorJPC = 0

            # if lucroLiquid50 * self.totalJSPC > 0:

            #     if self.totalJSPC * self.dataframe.loc[data, 'Ano'] > maior_valor:
            #         self.valorJPC = maior_valor
            #     else:
            #         self.valorJPC = round(self.totalJSPC * (self.dataframe.loc[data, 'Ano'] / 100), 2) - self.jcpRetroativo

            self.irrfJPC = round(self.valorJPC * 0.15, 2)
            self.valorApropriar = round(self.valorJPC - self.irrfJPC, 2)

            results = [
                {"Operation": "Base de Cálculo do JSPC", "Value": self.totalJSPC},
                {"Operation": "TJLP", "Value": self.taxaJuros},
                {"Operation": "Valor do JSCP", "Value": self.valorJPC},
                {"Operation": "IRRFs/ JSPC", "Value": self.irrfJPC},
                {"Operation": "Valor do JSCP", "Value": self.valorApropriar}
            ]
            self.resultadoJPC = pd.concat([self.resultadoJPC, pd.DataFrame(results)], ignore_index=True)
            self.LacsLalurAposInovacoes = pd.concat([self.LacsLalurAposInovacoes, pd.DataFrame([{"Operation": "Valor JSCP", "Value": self.valorJPC}])], ignore_index=True)
            st.dataframe(self.resultadoJPC, use_container_width=True)
        else:
            st.error("Data not found in the DataFrame")
                
    @timing
    def limiteDedutibilidade(self,data):

        key = f'retirar_multa_{data}'
        if key not in st.session_state:
            st.session_state[key] = False

        retirarMulta = st.toggle('Retirar valor de multa da conta', key=key)
        

        self.lucroLiquid50 = self.lucroAntIRPJ * 0.5
        self.lucroAcuEReserva = (self.reservLucro + self.lucroAcumulado) * 0.5
        if retirarMulta :
            self.darf = self.irrfJPC + (self.irrfJPC*0.2*0)
        else:            
            self.darf = self.irrfJPC + (self.irrfJPC*0.2)


        results = [
                {"Operation": "50% do Lucro Líquido antes do IRPJ e após a CSLL", "Value": self.lucroLiquid50},
                {"Operation": "50% do Lucro acumulado + reserva de Lucro", "Value": self.lucroAcuEReserva},
                {"Operation": "DARF Cód. 5706 IRRF s/ JSCP", "Value": self.darf},
            ]
        self.resultadoLimiteDedu = pd.concat([self.resultadoLimiteDedu, pd.DataFrame(results)], ignore_index=True)
        st.dataframe(self.resultadoLimiteDedu, use_container_width=True)   
    
    @timing
    def tabelaEconomia(self,data):
        year = data
        key = f'alterarAliquota{year}'
        if key not in st.session_state:
            st.session_state[key] = False

        alterarAliquiota = st.toggle('Alterar IRPJ/CSLL - 34% para 24%', key=key)
        if alterarAliquiota:
            valorAliquota = 24
            self.reducaoIRPJCSLL = self.valorJPC * 0.24
        else:
            self.reducaoIRPJCSLL = self.valorJPC * 0.34
            valorAliquota = 34 

        self.economia = self.reducaoIRPJCSLL - self.darf

        results = [
                {"Operation": f"REDUÇÃO NO IRPJ/CSLL - {valorAliquota}%", 'Value': self.reducaoIRPJCSLL},
                {"Operation": "Economia", "Value": self.economia},
            ]
        
        self.resultadoEconomiaGerada = pd.concat([self.resultadoEconomiaGerada, pd.DataFrame(results)], ignore_index=True)
        st.dataframe(self.resultadoEconomiaGerada, use_container_width=True)
        
        st.metric("Economia Gerada", f"R$ {self.economia:,.2f}".replace(',','_').replace('.',',').replace('_','.'))

    @timing
    @functools.cache
    def pipeCalculo(self, data):
        self.set_date(data)
        self.lucrosAcumulados()
        self.valorJPCRetroativo()
        self.TotalFinsCalcJSPC()
        self.calculandoJPC(self.data)
        self.limiteDedutibilidade(data)
        self.tabelaEconomia(data)
        return self.resultadoEconomiaGerada
        
    





