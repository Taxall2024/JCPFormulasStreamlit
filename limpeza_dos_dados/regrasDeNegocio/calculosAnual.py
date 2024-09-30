
import pandas as pd
import streamlit as st
import numpy as np
from bs4 import BeautifulSoup
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


class Calculo(FiltrandoDadosParaCalculo):
    _widget_counter = 0

    @timing
    def __init__(self, data, lacs_file, lalur_file, ecf670_file, ec630_file, l100_file, l300_file):
        super().__init__(data, lacs_file, lalur_file, ecf670_file, ec630_file, l100_file, l300_file)
        
        self.cnpj
        self.data = data
        self.resultadoJPC = pd.DataFrame(columns=["CNPJ","Operation", "Value","Ano"])
        self.resultadoLimiteDedu = pd.DataFrame(columns=["CNPJ","Operation", "Value","Ano"])
        self.resultadoEconomiaGerada = pd.DataFrame(columns=["CNPJ","Operation", "Value","Ano"])
        self.csllAposInovacoes = pd.DataFrame(columns=["CNPJ","Operation", "Value","Ano"])

        self.dataframe = ScrappingTJPL.fetch_tjlp_data()
        self.valorJPC = 0.0

    @timing
    def valorJPCRetroativo(self):

        self.jcpRetroativo = 0.0


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
                {"Ano":self.data,"CNPJ":self.cnpj,"Operation": "Base de Cálculo do JSPC", "Value": self.totalJSPC},
                {"Ano":self.data,"CNPJ":self.cnpj,"Operation": "TJLP", "Value": self.taxaJuros},
                {"Ano":self.data,"CNPJ":self.cnpj,"Operation": "Valor do JSCP", "Value": self.valorJPC},
                {"Ano":self.data,"CNPJ":self.cnpj,"Operation": "IRRFs/ JSPC", "Value": self.irrfJPC},
                {"Ano":self.data,"CNPJ":self.cnpj,"Operation": "Valor do JSCP Apropriar", "Value": self.valorApropriar}
            ]
            self.resultadoEconomiaGerada = pd.concat([self.resultadoEconomiaGerada, pd.DataFrame(results)], ignore_index=True)

        else:
            st.error("Data not found in the DataFrame")
                
    @timing
    def limiteDedutibilidade(self,data):


        self.lucroLiquid50 = self.lucroAntIRPJ * 0.5
        self.lucroAcuEReserva = (self.reservLucro + self.lucroAcumulado) * 0.5
         
        self.darf = self.irrfJPC + (self.irrfJPC*0.2)


        results = [
                {"Ano":self.data,"CNPJ":self.cnpj,"Operation": "50% do Lucro Líquido antes do IRPJ e após a CSLL", "Value": self.lucroLiquid50},
                {"Ano":self.data,"CNPJ":self.cnpj,"Operation": "50% do Lucro acumulado + reserva de Lucro", "Value": self.lucroAcuEReserva},
                {"Ano":self.data,"CNPJ":self.cnpj,"Operation": "DARF Cód. 5706 IRRF s/ JSCP", "Value": self.darf},
            ]
        self.resultadoEconomiaGerada = pd.concat([self.resultadoEconomiaGerada, pd.DataFrame(results)], ignore_index=True)
    
    @timing
    def tabelaEconomia(self,data):
        
        
        self.reducaoIRPJCSLL = self.valorJPC * 0.34
        valorAliquota = 34 

        self.economia = self.reducaoIRPJCSLL - self.darf

        results = [
                {"Ano":self.data,"CNPJ":self.cnpj,"Operation": f"REDUÇÃO NO IRPJ/CSLL - {valorAliquota}%", 'Value': self.reducaoIRPJCSLL},
                {"Ano":self.data,"CNPJ":self.cnpj,"Operation": "Economia", "Value": self.economia},
            ]
        
        self.resultadoEconomiaGerada = pd.concat([self.resultadoEconomiaGerada, pd.DataFrame(results)], ignore_index=True)

    @timing
    @functools.cache
    def pipeCalculo(self, data):
        
        self.set_date(data)
        self.valorJPCRetroativo()
        self.TotalFinsCalcJSPC()
        self.calculandoJPC(self.data)
        self.limiteDedutibilidade(data)
        self.tabelaEconomia(data)
        return self.resultadoEconomiaGerada
        
    





