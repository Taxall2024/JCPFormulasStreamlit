import pandas as pd
import streamlit as st
import numpy as np
import openpyxl as op
import sys
import os
import base64
import requests
from bs4 import BeautifulSoup
import functools
import time
import gc


# Adicione o caminho do diretório onde o módulo 'LacsLalur' está localizado
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from LacsLalur.trimestralLacsLalur import LacsLalurCSLLTrimestral
from scrapping import ScrappingTJPL



class trimestralFiltrandoDadosParaCalculo():
    _widget_counter = 0

    @st.cache_data(ttl='5m',persist=False)
    @staticmethod
    def load_excel_file(file_path):
        return pd.read_excel(file_path)
    
    def __init__(self, trimestre,ano,mes_inicio,mes_fim,l100_file, l300_file,lacs_file, lalur_file, ecf670_file, ec630_file):
        self.data = ano
        self.reservEstatuaria = 0.0
        self.resContingencia = 0.0
        self.reserExp = 0.0
        self.outrasResLuc = 0.0
        self.lucroAcumulado = 0.0
        self.reservLucro = 0.0
        self.taxaJuros = 0.0
        self.resultado = 0.0

        self.resultadoJPC = pd.DataFrame(columns=["Operation", "Value"])
        self.resultadoLimiteDedu = pd.DataFrame(columns=["Operation", "Value"])
        self.resultadoEconomiaGerada = pd.DataFrame(columns=["Operation", "Value"])

        self.dataframe = ScrappingTJPL.fetch_tjlp_data()
  
        self.ano = ano
        self.mes_inicio = mes_inicio
        self.mes_fim = mes_fim
        self.trimestre = trimestre
        self.LacsLalurTrimestral = LacsLalurCSLLTrimestral(self.trimestre, self.ano, 1, 12,lacs_file, lalur_file, ecf670_file, ec630_file)
        self.trimestralLacsLalurAposInovacoes = pd.DataFrame(columns=["Operation", "Value"])

        self.l100 = trimestralFiltrandoDadosParaCalculo.load_excel_file(l100_file)
        self.l300 = trimestralFiltrandoDadosParaCalculo.load_excel_file(l300_file)

  
        #-- Transforma as colunas de data em datetime, e agrega o trimestre correspondente aquele dado, afim de garantir que os dados estão no formato correto
        dados = [self.l100, self.l300]
        for i in dados:
            i['Data Inicial'] = pd.to_datetime(i['Data Inicial'], errors='coerce')
            i['Data Final'] = pd.to_datetime(i['Data Final'], errors='coerce')

        for df in dados:
            df['Data Inicial'] = pd.to_datetime(df['Data Inicial'])
            df['Data Final'] = pd.to_datetime(df['Data Final'])
            df['Trimestre'] = ''
            conditions = [
                df['Período Apuração Trimestral'] == 'T01 – 1º Trimestre',
                df['Período Apuração Trimestral'] == 'T02 – 2º Trimestre',
                df['Período Apuração Trimestral'] == 'T03 – 3º Trimestre',
                df['Período Apuração Trimestral'] == 'T04 – 4º Trimestre'
            ]
            choices = ['1º Trimestre', '2º Trimestre', '3º Trimestre', '4º Trimestre']
            df['Trimestre'] = np.select(conditions, choices, default='')            

        gc.collect()
        print("GARBAGE COLECTOR,GARBAGE COLECTOR,GARBAGE COLECTOR,GARBAGE COLECTOR,GARBAGE COLECTOR,GARBAGE COLECTOR,GARBAGE COLECTOR")
        print(gc.get_stats())

        self.resultsCalcJcp = pd.DataFrame(columns=["Operation", "Value"])
        self.resultsTabelaFinal = pd.DataFrame(columns=["Operation", "Value"])
        self.lucro_periodo_value = 0

    #-- Função que retorna o nome da empresa, deve ser substituida por uma função que busca o nome da empresa no banco de dados

    def set_date(self, data):
        self.data = data   


    def capitalSocial(self):
        l100 = self.l100
        l100 = l100[(l100['Descrição Conta Referencial']=='CAPITAL REALIZADO - DE RESIDENTE NO PAÍS')&
            (l100['Data Inicial'].dt.year == self.ano) &
            (l100['Data Inicial'].dt.month >= self.mes_inicio) &
            (l100['Data Inicial'].dt.month <= self.mes_fim)&
            (l100['Trimestre'] == self.trimestre)]
        self.capSocial = np.sum(l100['Vlr Saldo Final'].values)
        key = f'capitalSoc{self.data,self.trimestre,self.mes_fim}'

        if key not in st.session_state:
            st.session_state[key] = self.capSocial
        
        st.session_state[key] = st.session_state[key]

        self.capSocial = st.number_input('Ajuste Capital Social',key=key,value=st.session_state[key])

        self.resultsCalcJcp = pd.concat([self.resultsCalcJcp, pd.DataFrame([{"Operation": "Capital Social", "Value": self.capSocial}])], ignore_index=True)


    def capitalIntegralizador(self):


        l100 = self.l100
        l100 = l100[(l100['Conta Referencial']=='2.03.01.01.21')|(l100['Conta Referencial']=='2.03.01.02.10')&
            (l100['Data Inicial'].dt.year == self.ano) &
            (l100['Data Inicial'].dt.month >= self.mes_inicio) &
            (l100['Data Inicial'].dt.month <= self.mes_fim)&
            (l100['Trimestre'] == self.trimestre)]
        self.capitalIntegra = np.sum(l100['Vlr Saldo Final'].values)
    
        key = f'capitalIntregalizador{self.ano,self.mes_inicio,self.trimestre}'
        if key not in st.session_state:
            st.session_state[key] = self.capitalIntegra
        st.session_state[key] = st.session_state[key]    
        
        self.capitalIntegra = st.number_input('Digite o valor do Capital Integralizador', key=key, value=st.session_state[key])
         
        self.resultsCalcJcp = pd.concat([self.resultsCalcJcp, pd.DataFrame([{"Operation": "Capital Integralizador", "Value": self.capitalIntegra}])], ignore_index=True)
    

    def ReservasDeCapital(self):

        l100 = self.l100
        l100 = l100[(l100['Conta Referencial']=='2.03.02.01')&
            (l100['Data Inicial'].dt.year == self.ano) &
            (l100['Data Inicial'].dt.month >= self.mes_inicio) &
            (l100['Data Inicial'].dt.month <= self.mes_fim)&
            (l100['Trimestre'] == self.trimestre)]
        self.reservaCapital = np.sum(l100['Vlr Saldo Final'].values)
    
        key = f'reservasDeCapital{self.ano,self.mes_inicio,self.trimestre}'
        if key not in st.session_state:
            st.session_state[key] = self.reservaCapital
        st.session_state[key] = st.session_state[key]    
        
        self.reservaCapital = st.number_input('Digite o valor das Reservas de Capital', key=key, value=st.session_state[key])
         
        self.resultsCalcJcp = pd.concat([self.resultsCalcJcp, pd.DataFrame([{"Operation": "Reservas de Capital", "Value": self.reservaCapital}])], ignore_index=True)

            
    def ajustesAvalPatrimonial(self):
        l100 = self.l100
        l100 = l100[(l100['Conta Referencial']=='2.03.03')&
            (l100['Data Inicial'].dt.year == self.ano) &
            (l100['Data Inicial'].dt.month >= self.mes_inicio) &
            (l100['Data Inicial'].dt.month <= self.mes_fim)&
            (l100['Trimestre'] == self.trimestre)]
        self.ajusteAvaPatrimonial = np.sum(l100['Vlr Saldo Final'].values)

        key = f'ajustesPatrimonial{self.ano,self.mes_inicio,self.trimestre}'
        if key not in st.session_state:
            st.session_state[key] = self.ajusteAvaPatrimonial
        st.session_state[key] = st.session_state[key]    
        
        self.ajusteAvaPatrimonial = st.number_input('Digite o valor dos Ajustes de Avaliação Patrimonial', key=key, value=st.session_state[key])
         
        self.resultsCalcJcp = pd.concat([self.resultsCalcJcp, pd.DataFrame([{"Operation": "Ajustes Avaliação Patrimonial", "Value": self.ajusteAvaPatrimonial}])], ignore_index=True)

                    
    def lucrosAcumulados(self):

        lucroperiodoParaFun = self.l300
        lucroperiodoParaFun = lucroperiodoParaFun[(lucroperiodoParaFun['Conta Referencial']=='3')&
            (lucroperiodoParaFun['Data Inicial'].dt.year == self.ano) &
            (lucroperiodoParaFun['Data Inicial'].dt.month >= self.mes_inicio) &
            (lucroperiodoParaFun['Data Inicial'].dt.month <= self.mes_fim)&
            (lucroperiodoParaFun['Trimestre'] == self.trimestre)]
        self.lucroperiodoParaFun = sum(lucroperiodoParaFun['Vlr Saldo Final'])

        
        l100 = self.l100
        l100 = l100[(l100['Conta Referencial']=='2.03.04.01.01')&
            (l100['Data Inicial'].dt.year == self.ano) &
            (l100['Data Inicial'].dt.month >= self.mes_inicio) &
            (l100['Data Inicial'].dt.month <= self.mes_fim)&
            (l100['Trimestre'] == self.trimestre)]
        self.lucroAcumulado = sum(l100['Vlr Saldo Final'])  

        if self.lucroAcumulado == 0:
            pass
        else:
            if (lucroperiodoParaFun['D/C Saldo Final'] == 'C').any():
                
                self.resultado = self.lucroAcumulado - self.lucroperiodoParaFun
            else:
                self.resultado = self.lucroAcumulado          

        key = f'lucrosAcumulados{self.ano,self.mes_inicio,self.trimestre}'
        if key not in st.session_state:
            st.session_state[key] = self.lucroAcumulado 
        st.session_state[key] = st.session_state[key]    
        
        #self.lucroAcumulado = st.number_input('Digite o valor dos Lucros Acumulados', key=key, value=st.session_state[key])
         
        self.resultsCalcJcp = pd.concat([self.resultsCalcJcp, pd.DataFrame([{"Operation": "Lucros Acumulados", "Value": self.resultado}])], ignore_index=True)
        self.resultsTabelaFinal = pd.concat([self.resultsTabelaFinal, pd.DataFrame([{"Operation": "Lucros Acumulados", "Value": self.resultado}])], ignore_index=True)
      
    
    def ajustesExerAnteriores(self):
        l100 = self.l100
        l100 = l100[(l100['Conta Referencial']=='2.03.04.01.10')&
            (l100['Data Inicial'].dt.year == self.ano) &
            (l100['Data Inicial'].dt.month >= self.mes_inicio) &
            (l100['Data Inicial'].dt.month <= self.mes_fim)&
            (l100['Trimestre'] == self.trimestre)]
        self.ajustExercAnt = np.sum(l100['Vlr Saldo Final'].values)        

        key = f'ajustesExerAnteirores{self.ano,self.mes_inicio,self.trimestre}'
        if key not in st.session_state:
            st.session_state[key] = self.ajustExercAnt
        st.session_state[key] = st.session_state[key]    
        
        self.ajustExercAnt = st.number_input('Ajustes de Exercícios Anteriores', key=key, value=st.session_state[key])
         
        self.resultsCalcJcp = pd.concat([self.resultsCalcJcp, pd.DataFrame([{"Operation": "Ajustes Exercícios Anteriores", "Value": self.ajustExercAnt}])], ignore_index=True)


    def TotalFinsCalcJSPC(self):

        self.totalJSPC =  sum((self.capSocial,self.reservLucro,self.lucroAcumulado,self.ajustExercAnt,self.reservaCapital)) - (self.contaPatriNClassifica + self.prejuizoPeirod) 
        
        self.resultsCalcJcp = pd.concat([self.resultsCalcJcp, pd.DataFrame([{"Operation": "Total Fins Calc JSPC", "Value": self.totalJSPC}])], ignore_index=True)
        self.trimestralLacsLalurAposInovacoes = pd.concat([self.LacsLalurTrimestral.trimestralLacsLalurAposInovacoes, pd.DataFrame([{"Operation": "Total Fins Calc JSPC", "Value": self.totalJSPC}])], ignore_index=True)


    def update_reservas(self):
        self.reservLucro = self.reservLegal + self.reservEstatuaria + self.resContingencia + self.reserExp + self.outrasResLuc
        self.resultsTabelaFinal.loc[self.resultsTabelaFinal['Operation'] == 'Reservas de Lucros', 'Value'] = self.reservLucro


    def ReservaLegal(self):
        l100 = self.l100
        l100 = l100[(l100['Conta Referencial']=='2.03.02.03.01')&
            (l100['Data Inicial'].dt.year == self.ano) &
            (l100['Data Inicial'].dt.month >= self.mes_inicio) &
            (l100['Data Inicial'].dt.month <= self.mes_fim)&
            (l100['Trimestre'] == self.trimestre)]
        self.reservLegal = np.sum(l100['Vlr Saldo Final'].values)
        
        key = f'reservaLegal{self.ano,self.mes_inicio,self.trimestre}'

        if key not in st.session_state:
            st.session_state[key] = self.reservLegal

        st.session_state[key] = st.session_state[key]
        self.reservLegal = st.number_input('Digite o valor da Reserva Legal', key=key, value=st.session_state[key])
         
        self.resultsCalcJcp = pd.concat([self.resultsCalcJcp, pd.DataFrame([{"Operation": "Reserva legal", "Value": self.reservLegal}])], ignore_index=True)
   
    
    def ReservasLucros(self):

        l100 = self.l100
        l100 = l100[(l100['Conta Referencial']=='2.03.02.03')&
            (l100['Data Inicial'].dt.year == self.ano) &
            (l100['Data Inicial'].dt.month >= self.mes_inicio) &
            (l100['Data Inicial'].dt.month <= self.mes_fim)&
            (l100['Trimestre'] == self.trimestre)]
        self.reservLucro = np.sum(l100['Vlr Saldo Final'].values)

        key = f'reservaSDElucrosOutras{self.ano,self.mes_inicio,self.trimestre}'

        if key not in st.session_state:
            st.session_state[key] = self.reservLucro
        
        st.session_state[key] = st.session_state[key]

        self.reservLucro = st.number_input('Digite o valor  Reservas de Lucros',key=key,value=st.session_state[key])
        self.resultsCalcJcp = pd.concat([self.resultsCalcJcp, pd.DataFrame([{"Operation": "Reservas de Lucros", "Value": self.reservLucro}])], ignore_index=True)
    
    
    def acoesTesouraria(self):

        l100 = self.l100
        l100 = l100[(l100['Conta Referencial']=='2.03.04.01.12')&
            (l100['Data Inicial'].dt.year == self.ano) &
            (l100['Data Inicial'].dt.month >= self.mes_inicio) &
            (l100['Data Inicial'].dt.month <= self.mes_fim)&
            (l100['Trimestre'] == self.trimestre)]
        self.acosTesouraria = np.sum(l100['Vlr Saldo Final'].values)
        self.resultsCalcJcp = pd.concat([self.resultsCalcJcp, pd.DataFrame([{"Operation": "Ações em Tesouraria", "Value": self.acosTesouraria}])], ignore_index=True)
    
    
    def contPatrimonioNaoClass(self):

        l100 = self.l100
        l100 = l100[(l100['Conta Referencial']=='2.03.04.01.90')&
            (l100['Data Inicial'].dt.year == self.ano) &
            (l100['Data Inicial'].dt.month >= self.mes_inicio) &
            (l100['Data Inicial'].dt.month <= self.mes_fim)&
            (l100['Trimestre'] == self.trimestre)]
        self.contaPatriNClassifica = np.sum(l100['Vlr Saldo Final'].values)
        self.resultsCalcJcp = pd.concat([self.resultsCalcJcp, pd.DataFrame([{"Operation": "Contas do Patrimônio Líquido Não Classificadas ", "Value": self.contaPatriNClassifica}])], ignore_index=True)
    

    def PrejuizoPeriodo(self):
        l100 = self.l300
        l100 = l100[(l100['Conta Referencial']=='3')&
            (l100['Data Inicial'].dt.year == self.ano) &
            (l100['Data Inicial'].dt.month >= self.mes_inicio) &
            (l100['Data Inicial'].dt.month <= self.mes_fim)&
            (l100['Trimestre'] == self.trimestre)]
        self.prejuizoPeirod = np.sum(l100['Vlr Saldo Final'].values)

        if (l100['D/C Saldo Final'] == 'C').any():
            lucroPrejuizo = 'Lucro do Período'
        else:
            lucroPrejuizo = 'Prejuízo do Período'    
        key = f'PrejuAcumulado{self.ano,self.mes_inicio,self.trimestre}'   

        if key not in st.session_state:
            st.session_state[key] = self.prejuizoPeirod
        
        st.session_state[key] = st.session_state[key]
        self.prejuizoPeirod = st.number_input(f'Digite o valor do {lucroPrejuizo}',key=key,value=st.session_state[key])
  
        self.resultsCalcJcp = pd.concat([self.resultsCalcJcp, pd.DataFrame([{"Operation": f"{lucroPrejuizo} ", "Value": self.prejuizoPeirod}])], ignore_index=True)

        
    def prejuizosAcumulados(self):
        prejuPeriodo = self.l300
        prejuPeriodo = prejuPeriodo[(prejuPeriodo['Conta Referencial']=='3')&
            (prejuPeriodo['Data Inicial'].dt.year == self.ano) &
            (prejuPeriodo['Data Inicial'].dt.month >= self.mes_inicio) &
            (prejuPeriodo['Data Inicial'].dt.month <= self.mes_fim)&
            (prejuPeriodo['Trimestre'] == self.trimestre)]
        self.prejuizoPeirodo = np.sum(prejuPeriodo['Vlr Saldo Final'].values)

        l100 = self.l100
        l100 = l100[(l100['Conta Referencial']=='2.03.04.01.11')&
            (l100['Data Inicial'].dt.year == self.ano) &
            (l100['Data Inicial'].dt.month >= self.mes_inicio) &
            (l100['Data Inicial'].dt.month <= self.mes_fim)&
            (l100['Trimestre'] == self.trimestre)]
        self.contaPatriNClassifica = np.sum(l100['Vlr Saldo Final'].values)

        if self.contaPatriNClassifica == 0:
            pass
        else:
            if (prejuPeriodo['D/C Saldo Final'] == 'C').any():
                self.contaPatriNClassifica = self.contaPatriNClassifica
            else:
                self.contaPatriNClassifica =  self.contaPatriNClassifica - self.prejuizoPeirod 

        self.resultsCalcJcp = pd.concat([self.resultsCalcJcp, pd.DataFrame([{"Operation": "Prejuízos Acumulados", "Value": self.contaPatriNClassifica}])], ignore_index=True)
        
        key = f'prejuizoAcumulado{self.data,self.trimestre,self.mes_fim}'

        if key not in st.session_state:
            st.session_state[key] = self.contaPatriNClassifica
        
        st.session_state[key] = st.session_state[key]

        self.contaPatriNClassifica = st.number_input('Ajuste Prejuízos Acumulados',key=key,value=st.session_state[key])

    def calculandoJPC(self,data,trimestre):

        if trimestre == '1º Trimestre':
            trimestre = '1º Tri'
        elif trimestre == '2º Trimestre':
            trimestre = '2º Tri'   
        elif trimestre == '3º Trimestre':
            trimestre = '3º Tri'                                               
        elif trimestre == '4º Trimestre':  
            trimestre = '4º Tri'

       
        self.taxaJuros = self.dataframe.loc[data, trimestre]
        
        if self.totalJSPC < 0:
            self.valorJPC = 0
        else:     
            self.valorJPC = round(self.totalJSPC * (self.taxaJuros / 100), 2)
        self.irrfJPC = round(self.valorJPC * 0.15, 2)
        self.valorApropriar = round(self.valorJPC - self.irrfJPC, 2)

        results = [
            {"Operation": "Base de Cálculo do JSPC", "Value": self.totalJSPC},
            {"Operation": "TJLP", "Value": self.taxaJuros},
            {"Operation": "Valor do JSCP", "Value": self.valorJPC},
            {"Operation": "IRRFs/ JSPC", "Value": self.irrfJPC},
            {"Operation": "Valor do JSCP", "Value": self.valorApropriar}]
        

        self.resultadoJPC = pd.concat([self.resultadoJPC, pd.DataFrame(results)], ignore_index=True)


    def limiteDedutibilidade(self):

        key = f'retirar_multa_{self.ano,self.trimestre,self.mes_fim}'
        if key not in st.session_state:
            st.session_state[key] = False

        retirarMulta = st.toggle('Retirar valor de multa da conta', key=key)
        
         
        self.LacsLalurTrimestral.LucroLiquidoAntesIRPJ()
        self.lucroLiquid50 = self.LacsLalurTrimestral.lucroAntIRPJ * 0.5
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


    def tabelaEconomia(self):

        year = self.data,self.trimestre
        key = f'alterarAliquota{year}'
        if key not in st.session_state:
            st.session_state[key] = False

        alterarAliquiota = st.toggle('Alterar IRPJ/CSLL - 34% para 24%', key=key)

        if alterarAliquiota:
            self.reducaoIRPJCSLL = self.valorJPC * 0.24
            self.valor = 0.24
        else:
            self.reducaoIRPJCSLL = self.valorJPC * 0.34
            self.valor = 0.34

        self.economia = self.reducaoIRPJCSLL - self.darf

        results = [
                {"Operation": f"REDUÇÃO NO IRPJ/CSLL - {self.valor}%", "Value": self.reducaoIRPJCSLL},
                {"Operation": "Economia", "Value": self.economia},
            ]
        
        self.resultadoEconomiaGerada = pd.concat([self.resultadoEconomiaGerada, pd.DataFrame(results)], ignore_index=True)

    @functools.cache
    def runPipe(self):
        with st.expander("Adicionar valores :"):
            self.capitalSocial()
            self.capitalIntegralizador()
            self.ReservasDeCapital()
            self.ajustesAvalPatrimonial()

            self.ReservaLegal()
            self.ReservasLucros()

            self.acoesTesouraria()
            self.contPatrimonioNaoClass()
            self.PrejuizoPeriodo()
            self.prejuizosAcumulados()

            self.acoesTesouraria()
            self.lucrosAcumulados()
            self.ajustesExerAnteriores()
            self.TotalFinsCalcJSPC()

            #-- Metódos que fazer calculos dos valores finais do JCP

            self.calculandoJPC(str(self.ano), self.trimestre)
            self.limiteDedutibilidade()
            self.tabelaEconomia()
            
        
        self.resultsCalcJcp['Value'] = self.resultsCalcJcp['Value'].apply(lambda x: "{:,.2f}".format(x)).str.replace('.','_').str.replace(',','.').str.replace('_',',')
        self.resultadoEconomiaGerada['Value'] = self.resultadoEconomiaGerada['Value'].apply(lambda x: "{:,.2f}".format(x).replace(',','_').replace('.',',').replace('_','.'))
        self.resultadoJPC['Value'] = self.resultadoJPC['Value'].apply(lambda x: "{:,.2f}".format(x).replace(',','_').replace('.',',').replace('_','.'))
        self.resultadoLimiteDedu['Value'] = self.resultadoLimiteDedu['Value'].apply(lambda x: "{:,.2f}".format(x).replace(',','_').replace('.',',').replace('_','.'))
        
    
        self.dataframeFinal = pd.DataFrame(self.resultsCalcJcp)
        self.dataframJCP = pd.DataFrame(self.resultadoJPC)
        self.dfLacsLalurApos = pd.DataFrame(self.trimestralLacsLalurAposInovacoes)
    
    @functools.cache
    def runPipeFinalTable(self):

        self.lucrosAcumulados()
        self.LacsLalurTrimestral.exclusoes()
        self.LacsLalurTrimestral.calcAdicoes()
        self.LacsLalurTrimestral.lucroAntesCSLL()
        self.LacsLalurTrimestral.baseDeCalculo()
        self.LacsLalurTrimestral.compensacaoPrejuizo()   
        self.LacsLalurTrimestral.LucroLiquidoAntesIRPJ()
        self.LacsLalurTrimestral.baseCSLL()

        self.resultsTabelaFinal['Value'] = self.resultsTabelaFinal['Value'].apply(lambda x: "{:,.2f}".format(x).replace(',','_').replace('.',',').replace('_','.'))
        st.dataframe(self.resultsTabelaFinal)
    




