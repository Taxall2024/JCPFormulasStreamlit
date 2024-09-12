import pandas as pd
import numpy as np
import streamlit as st
import functools
from dataclasses import dataclass
import gc


class LacsLalurCSLLTrimestral():

    @st.cache_data(ttl='5m',persist=False)
    @staticmethod
    def load_file(df):
            return df
    
    def __init__(self,trimestre,ano,mes_inicio,mes_fim,lacs_file, lalur_file, ecf670_file, ec630_file):
        print('hello world')

       
        self.lacs = LacsLalurCSLLTrimestral.load_file(lacs_file)
        self.lalur = LacsLalurCSLLTrimestral.load_file(lalur_file)
        self.ecf670 = LacsLalurCSLLTrimestral.load_file(ecf670_file)
        self.ec630 = LacsLalurCSLLTrimestral.load_file(ec630_file)

        self.dfs = [self.lacs, self.lalur, self.ecf670, self.ec630]

        for df in self.dfs:
            df['Data Inicial'] = pd.to_datetime(df['Data Inicial'])
            df['Data Final'] = pd.to_datetime(df['Data Final'])
            df['Trimestre'] = ''

                     
            conditions = [
                df['Período Apuração Trimestral'] == 'T01 – 1º Trimestre',
                df['Período Apuração Trimestral'] == 'T02 – 2º Trimestre',
                df['Período Apuração Trimestral'] == 'T03 – 3º Trimestre',
                df['Período Apuração Trimestral'] == 'T04 – 4º Trimestre']
            
            choices = ['1º Trimestre', '2º Trimestre', '3º Trimestre', '4º Trimestre']
            df['Trimestre'] = np.select(conditions, choices, default='')  
        
        self.ano = ano
        self.mes_inicio = mes_inicio
        self.mes_fim = mes_fim
        self.trimestre = trimestre

        self.resultsLacs = pd.DataFrame(columns=["Operation", "Value"])
        self.resultsTabelaFinal = pd.DataFrame(columns=["Operation", "Value"])
        self.results = pd.DataFrame(columns=["Operation", "Value"]) 
        self.trimestralLacsLalurAposInovacoes = pd.DataFrame(columns=["Operation", "Value"])

        gc.collect()
        print("GARBAGE COLECTOR,GARBAGE COLECTOR,GARBAGE COLECTOR,GARBAGE COLECTOR,GARBAGE COLECTOR,GARBAGE COLECTOR,GARBAGE COLECTOR")
        print(gc.get_stats())


        self.lucroAntCSLL = 0 
        self.adicoes = 0
        self.exclusao = 0
        self.baseCalculoCls = 0
        self.compensacao = 0
        self.basecSLL = 0
        self.valorcSLL = 0
        self.retencoes = 0
        self.retencoesOrgPub = 0
        self.impostoPorEstim = 0
        self.subTotalcl = 0
    
    # -- Funções auxiliares para limpeza dos código, no processo de debug alguns calculos não receberam essas funções e nescessitam 
    #       de re-implementação, mas para uma primeira sprint e POC esta ok

    def filtro_dados(self, df, codigo, col='Código Lançamento e-Lacs'):
        return df[
                (df[col] == codigo) &
                (df['Data Inicial'].dt.year == self.ano) &
                (df['Data Inicial'].dt.month >= self.mes_inicio) &
                (df['Data Inicial'].dt.month <= self.mes_fim) &
                (df['Trimestre'] == self.trimestre)]
    
    def calcular_soma(self, df, codigo, col='Código Lançamento e-Lacs'):
        filtro = self.filtro_dados(df, codigo, col)
        return np.sum(filtro['Vlr Lançamento e-Lacs'].values)
    
    def filter_data(self, df, code):
        return df[
                (df['Código Lançamento e-Lalur'] == code) &
                (df['Data Inicial'].dt.year == self.ano) &
                (df['Data Inicial'].dt.month >= self.mes_inicio) &
                (df['Data Inicial'].dt.month <= self.mes_fim) &
                (df['Trimestre'] == self.trimestre)]

    def add_result(self, operation, value):
        self.results = pd.concat(
            [self.results, pd.DataFrame([{"Operation": operation, "Value": value}])],
            ignore_index=True
        )
    
    def add_final_result(self, operation, value):
        self.resultsTabelaFinal = pd.concat(
            [self.resultsTabelaFinal, pd.DataFrame([{"Operation": operation, "Value": value}])],
            ignore_index=True
        )



        # --- --- Cada função abaixo representa um calculo da planilha de calculos para Lacs e Lalur, as funções recebem como variaveis
        #           ano, mes de incio do periodo, mes final do periodo de analise e o trimestre, as variaveis de mes de inicio e mes final foram adicionadas com 
        #             com intuito de separar em trimestres para fazer análise trimestral dos dados, porém a ideia inicial não funcionou e encontrei outra maneira de separar o trimestre
        #               mas resolvi manter as variaveis em caso de haver a nescessidade de filtragem com utilização dessas informações no futuro 


    #      As funções abaixo sao referentes a parte da tabela Lacs e Lalur que representa os calculos de CSLL
    def lucroAntesCSLL(self):
        
        lacs = self.lacs   
        lacs = lacs[(self.lacs['Código Lançamento e-Lacs']== 2)&
            (lacs['Data Inicial'].dt.year == self.ano) &
            (lacs['Data Inicial'].dt.month >= self.mes_inicio) &
            (lacs['Data Inicial'].dt.month <= self.mes_fim)&
            (lacs['Trimestre'] == self.trimestre)]
        
        self.lucroAntCSLL = np.sum(lacs['Vlr Lançamento e-Lacs'].values)
        self.resultsLacs = pd.concat([self.resultsLacs, pd.DataFrame([{"Operation": "Lucro antes CSLL", "Value": self.lucroAntCSLL}])], ignore_index=True)
        self.trimestralLacsLalurAposInovacoes = pd.concat([self.trimestralLacsLalurAposInovacoes, pd.DataFrame([{"Operation": "Lucro antes CSLL", "Value": self.lucroAntCSLL}])], ignore_index=True)
    

    def calcAdicoes(self):
        self.adicoesValue = self.calcular_soma(self.lacs, 93)
        self.resultsLacs = pd.concat([self.resultsLacs, pd.DataFrame([{"Operation": "Adições", "Value": self.adicoesValue}])], ignore_index=True)
        self.trimestralLacsLalurAposInovacoes = pd.concat([self.trimestralLacsLalurAposInovacoes, pd.DataFrame([{"Operation": "Adições", "Value": self.adicoesValue}])], ignore_index=True)
       
    def exclusoes(self):
        self.exclusao = self.calcular_soma(self.lacs, 168)
        self.resultsLacs = pd.concat([self.resultsLacs, pd.DataFrame([{"Operation": "Exclusões", "Value": self.exclusao}])], ignore_index=True)
        self.trimestralLacsLalurAposInovacoes = pd.concat([self.trimestralLacsLalurAposInovacoes, pd.DataFrame([{"Operation": "Exclusões", "Value": self.exclusao}])], ignore_index=True)
        
    def baseDeCalculo(self):
        self.baseCalculoCls = self.lucroAntCSLL + self.adicoesValue - self.exclusao
        self.resultsLacs = pd.concat([self.resultsLacs, pd.DataFrame([{"Operation": "Base de Cálculo", "Value": self.baseCalculoCls}])], ignore_index=True)
        self.trimestralLacsLalurAposInovacoes = pd.concat([self.trimestralLacsLalurAposInovacoes, pd.DataFrame([{"Operation": "Base de Cálculo", "Value": self.baseCalculoCls}])], ignore_index=True)
 
    def compensacaoPrejuizo(self):
        lalur = self.lalur
        lalur = lalur[
            (lalur['Código Lançamento e-Lalur']== 173)&
            (lalur['Data Inicial'].dt.year == self.ano) &
            (lalur['Data Inicial'].dt.month >= self.mes_inicio) &
            (lalur['Data Inicial'].dt.month <= self.mes_fim)&
            (lalur['Trimestre'] == self.trimestre)]
        self.compensacao = np.sum(lalur['Vlr Lançamento e-Lalur'].values)

        self.resultsLacs = pd.concat([self.resultsLacs, pd.DataFrame([{"Operation": "Compensação de Prejuízo", "Value": self.compensacao}])], ignore_index=True)
        self.trimestralLacsLalurAposInovacoes = pd.concat([self.trimestralLacsLalurAposInovacoes, pd.DataFrame([{"Operation": "Compensação de Prejuízo", "Value": self.compensacao}])], ignore_index=True)

    def baseCSLL(self):
        self.basecSLL = self.baseCalculoCls - self.compensacao
        self.resultsLacs = pd.concat([self.resultsLacs, pd.DataFrame([{"Operation": "Base CSLL", "Value": self.basecSLL}])], ignore_index=True)
        self.resultsTabelaFinal = pd.concat([self.resultsTabelaFinal, pd.DataFrame([{"Operation": "Base CSLL", "Value": self.basecSLL}])], ignore_index=True)
        self.trimestralLacsLalurAposInovacoes = pd.concat([self.trimestralLacsLalurAposInovacoes, pd.DataFrame([{"Operation": "Base CSLL", "Value": self.basecSLL}])], ignore_index=True)
    
    def valorCSLL(self):
        self.valorcSLL = max(0, self.basecSLL * 0.09)
        self.resultsLacs = pd.concat([self.resultsLacs, pd.DataFrame([{"Operation": "Valor CSLL", "Value": self.valorcSLL}])], ignore_index=True)
        self.trimestralLacsLalurAposInovacoes = pd.concat([self.trimestralLacsLalurAposInovacoes, pd.DataFrame([{"Operation": "Valor CSLL", "Value": self.valorcSLL}])], ignore_index=True)
    
    def retencoesFonte(self):

        lalur = self.lalur
        lalur = lalur[
            (lalur['Código Lançamento e-Lalur']== 17)&
            (lalur['Data Inicial'].dt.year == self.ano) &
            (lalur['Data Inicial'].dt.month >= self.mes_inicio) &
            (lalur['Data Inicial'].dt.month <= self.mes_fim)&
            (lalur['Trimestre'] == self.trimestre)]
        self.retencoes = np.sum(lalur['Vlr Lançamento e-Lalur'].values)
        self.resultsLacs = pd.concat([self.resultsLacs, pd.DataFrame([{"Operation": "Valor CSLL", "Value": self.retencoes}])], ignore_index=True)
        self.trimestralLacsLalurAposInovacoes = pd.concat([self.trimestralLacsLalurAposInovacoes, pd.DataFrame([{"Operation": "Valor CSLL", "Value": self.retencoes}])], ignore_index=True)
    
    def retencoesOrgPublicos(self):

        lalur = self.ecf670
        filtroUm = lalur[
            (lalur['Código Lançamento']== 15)|(lalur['Código Lançamento']== 16)|(lalur['Código Lançamento']== 18)&
            (lalur['Data Inicial'].dt.year == self.ano) &
            (lalur['Data Inicial'].dt.month >= self.mes_inicio) &
            (lalur['Data Inicial'].dt.month <= self.mes_fim)&
            (lalur['Trimestre'] == self.trimestre)]

        filtroDois = lalur[
            (lalur['Código Lançamento']== 16)&
            (lalur['Data Inicial'].dt.year == self.ano) &
            (lalur['Data Inicial'].dt.month >= self.mes_inicio) &
            (lalur['Data Inicial'].dt.month <= self.mes_fim)&
            (lalur['Trimestre'] == self.trimestre)]

        filtroTres = lalur[
            (lalur['Código Lançamento']== 18)&
            (lalur['Data Inicial'].dt.year == self.ano) &
            (lalur['Data Inicial'].dt.month >= self.mes_inicio) &
            (lalur['Data Inicial'].dt.month <= self.mes_fim)&
            (lalur['Trimestre'] == self.trimestre)]
        
                                
        self.retencoesOrgPub = sum([filtroUm['Vlr Lançamento'].sum(),
                                filtroDois['Vlr Lançamento'].sum(),
                                filtroTres['Vlr Lançamento'].sum()])

        self.resultsLacs = pd.concat([self.resultsLacs, pd.DataFrame([{"Operation": "Retenções orgãos publicos", "Value": self.retencoesOrgPub}])], ignore_index=True)
        self.trimestralLacsLalurAposInovacoes = pd.concat([self.trimestralLacsLalurAposInovacoes, pd.DataFrame([{"Operation": "Retenções orgãos publicos", "Value": self.retencoesOrgPub}])], ignore_index=True)

    def impostoPorEstimativa(self):
        ecf760 = self.ecf670
        ecf760 = ecf760[
            (ecf760['Código Lançamento']== 19)&
            (ecf760['Data Inicial'].dt.year == self.ano) &
            (ecf760['Data Inicial'].dt.month >= self.mes_inicio) &
            (ecf760['Data Inicial'].dt.month <= self.mes_fim)&
            (ecf760['Trimestre'] == self.trimestre)]
        
        self.impostoPorEstim = np.sum(ecf760['Vlr Lançamento'].values)
        self.resultsLacs = pd.concat([self.resultsLacs, pd.DataFrame([{"Operation": "Imposto por estimativa", "Value": self.impostoPorEstim}])], ignore_index=True)
        self.trimestralLacsLalurAposInovacoes = pd.concat([self.trimestralLacsLalurAposInovacoes, pd.DataFrame([{"Operation": "Imposto por estimativa", "Value": self.impostoPorEstim}])], ignore_index=True)

    def subTotalCSLLRecolher(self):
        self.subTotalcl = self.valorcSLL - self.retencoes - self.retencoesOrgPub - self.impostoPorEstim
        self.resultsLacs = pd.concat([self.resultsLacs, pd.DataFrame([{"Operation": "Subtotal CSLL a Recolher", "Value": self.subTotalcl}])], ignore_index=True)
        self.trimestralLacsLalurAposInovacoes = pd.concat([self.trimestralLacsLalurAposInovacoes, pd.DataFrame([{"Operation": "Subtotal CSLL a Recolher", "Value": self.subTotalcl}])], ignore_index=True)
    
    @functools.cache
    def runPipeLacsLalurCSLL(self):
        self.lucroAntesCSLL()
        self.calcAdicoes()
        self.exclusoes()
        self.baseDeCalculo()
        self.compensacaoPrejuizo()
        self.baseCSLL()
        self.valorCSLL()
        self.retencoesFonte()
        self.retencoesOrgPublicos()
        self.impostoPorEstimativa()
        self.subTotalCSLLRecolher()

        self.dataframeFinal = pd.DataFrame(self.resultsLacs)
        
        return self.dataframeFinal

    
    #     As funções abaixo sao referentes a parte da tabela Lacs e Lalur que representa os calculos de IRPJ



    def LucroLiquidoAntesIRPJ(self):
        lalur_filtered = self.filter_data(self.lalur, 2)
        self.lucroAntIRPJ = np.sum(lalur_filtered['Vlr Lançamento e-Lalur'].values)
        self.add_result("Lucro antes IRPJ", self.lucroAntIRPJ)
        self.add_final_result("Lucro antes IRPJ", self.lucroAntIRPJ)
        self.trimestralLacsLalurAposInovacoes = pd.concat([self.trimestralLacsLalurAposInovacoes, pd.DataFrame([{"Operation": "Lucro antes IRPJ", "Value": self.lucroAntIRPJ}])], ignore_index=True)
    
    def clss(self):
        lalur_filtered = self.filter_data(self.lalur, 9)
        self.contrilss = np.sum(lalur_filtered['Vlr Lançamento e-Lalur'].values)
        self.add_result("Contribuição Social Sobre o Lucro Líquido - CSLL", self.contrilss)
        self.trimestralLacsLalurAposInovacoes = pd.concat([self.trimestralLacsLalurAposInovacoes, pd.DataFrame([{"Operation": "Contribuição Social Sobre o Lucro Líquido - CSLL", "Value": self.contrilss}])], ignore_index=True)
    
    def demaisAdicoes(self):
        filtroUm = self.filter_data(self.lalur, 93)
        filtroDois = self.filter_data(self.lalur, 9)
        self.demaisAd = filtroUm['Vlr Lançamento e-Lalur'].sum() - filtroDois['Vlr Lançamento e-Lalur'].sum()
        self.add_result("Demais Adições", self.demaisAd)
        self.trimestralLacsLalurAposInovacoes = pd.concat([self.trimestralLacsLalurAposInovacoes, pd.DataFrame([{"Operation": "Demais Adições", "Value": self.demaisAd}])], ignore_index=True)
    
    def adicoesIRPJ(self):
        self.clss()
        self.demaisAdicoes()
        self.adicoesIRPj = self.contrilss + self.demaisAd
        self.add_result("Adições IRPJ", self.adicoesIRPj)
        self.trimestralLacsLalurAposInovacoes = pd.concat([self.trimestralLacsLalurAposInovacoes, pd.DataFrame([{"Operation": "Adições IRPJ", "Value": self.adicoesIRPj}])], ignore_index=True)
    
    def exclusoesIRPJ(self):
        lalur_filtered = self.filter_data(self.lalur, 168)
        self.exclusoeS = np.sum(lalur_filtered['Vlr Lançamento e-Lalur'].values)
        self.add_result("Exclusões", self.exclusoeS)
        self.trimestralLacsLalurAposInovacoes = pd.concat([self.trimestralLacsLalurAposInovacoes, pd.DataFrame([{"Operation": "Exclusões", "Value": self.exclusoeS}])], ignore_index=True)
   
    def baseCalculoIRPJ(self):
        self.baseCalIRPJ = self.lucroAntIRPJ + self.adicoesIRPj - self.exclusoeS
        self.add_result("Base de cálculo", self.baseCalIRPJ)
        self.trimestralLacsLalurAposInovacoes = pd.concat([self.trimestralLacsLalurAposInovacoes, pd.DataFrame([{"Operation": "Base de cálculo", "Value": self.baseCalIRPJ}])], ignore_index=True)
   
    def CompPrejuFiscal(self):
        lalur_filtered = self.filter_data(self.lalur, 173)
        self.compPrejFiscal = np.sum(lalur_filtered['Vlr Lançamento e-Lalur'].values)
        self.add_result("Compensação Prejuízo fiscal", self.compPrejFiscal)
        self.trimestralLacsLalurAposInovacoes = pd.concat([self.trimestralLacsLalurAposInovacoes, pd.DataFrame([{"Operation": "Compensação Prejuízo fiscal", "Value": self.compPrejFiscal}])], ignore_index=True)
   
    def lucroReal(self):
        self.lucroRel = self.baseCalIRPJ - self.compPrejFiscal
        self.add_result("Lucro Real", self.lucroRel)
        self.trimestralLacsLalurAposInovacoes = pd.concat([self.trimestralLacsLalurAposInovacoes, pd.DataFrame([{"Operation": "Lucro Real", "Value": self.lucroRel}])], ignore_index=True)
   
    def valorIRPJ(self):
        self.valorIRPj = np.where(self.lucroRel < 0, 0, self.lucroRel * 0.15)
        self.add_result("Valor IRPJ", self.valorIRPj)
        self.trimestralLacsLalurAposInovacoes = pd.concat([self.trimestralLacsLalurAposInovacoes, pd.DataFrame([{"Operation": "Valor IRPJ", "Value": self.valorIRPj}])], ignore_index=True)
  
    def valorIRPJadicionais(self):
        self.valorIRPJAd = np.where(self.lucroRel > 60000, (self.lucroRel - 60000) * 0.10, 0)
        self.add_result("Valor IRPJ Adicionais", self.valorIRPJAd)
        self.trimestralLacsLalurAposInovacoes = pd.concat([self.trimestralLacsLalurAposInovacoes, pd.DataFrame([{"Operation": "Valor IRPJ Adicionais", "Value": self.valorIRPJAd}])], ignore_index=True)
  
    def totalDevidoIRPJantesRetencao(self):
        self.totalDevido = self.valorIRPj + self.valorIRPJAd
        self.add_result("Total devido IRPJ antes da retenção", self.totalDevido)
        self.trimestralLacsLalurAposInovacoes = pd.concat([self.trimestralLacsLalurAposInovacoes, pd.DataFrame([{"Operation": "Total devido IRPJ antes da retenção", "Value": self.totalDevido}])], ignore_index=True)
  
    def pat(self):

        lalur = self.ec630
        lalur = lalur[
            (lalur['Código Lançamento'] == 8)&
            (lalur['Data Inicial'].dt.year == self.ano) &
            (lalur['Data Inicial'].dt.month >= self.mes_inicio) &
            (lalur['Data Inicial'].dt.month <= self.mes_fim)&
            (lalur['Trimestre'] == self.trimestre)]
        
        self.PAT = np.sum(lalur['Vlr Lançamento'].values)

        self.results = pd.concat([self.results, pd.DataFrame([{"Operation": "PAT", "Value": self.PAT}])], ignore_index=True) 
        self.trimestralLacsLalurAposInovacoes = pd.concat([self.trimestralLacsLalurAposInovacoes, pd.DataFrame([{"Operation": "PAT", "Value": self.PAT}])], ignore_index=True) 


    def operacoesCulturalArtistico(self):

        lalur = self.ec630
        lalur = lalur[
            (lalur['Código Lançamento'] == 6)&
            (lalur['Data Inicial'].dt.year == self.ano) &
            (lalur['Data Inicial'].dt.month >= self.mes_inicio) &
            (lalur['Data Inicial'].dt.month <= self.mes_fim)&
            (lalur['Trimestre'] == self.trimestre)]
        
        self.operCultuArtistico = np.sum(lalur['Vlr Lançamento'].values)

        self.results = pd.concat([self.results, pd.DataFrame([{"Operation": "(-)Operações de Caráter Cultural e Artístico", "Value": self.operCultuArtistico}])], ignore_index=True )      
        self.trimestralLacsLalurAposInovacoes = pd.concat([self.trimestralLacsLalurAposInovacoes, pd.DataFrame([{"Operation": "(-)Operações de Caráter Cultural e Artístico", "Value": self.operCultuArtistico}])], ignore_index=True )      
      
    def insencaoRedImposto(self):

        lalur = self.ec630
        filtro1 = lalur[
            (lalur['Código Lançamento'] == 17)&
            (lalur['Data Inicial'].dt.year == self.ano) &
            (lalur['Data Inicial'].dt.month >= self.mes_inicio) &
            (lalur['Data Inicial'].dt.month <= self.mes_fim)&
            (lalur['Trimestre'] == self.trimestre)]
        filtro2 = lalur[
            (lalur['Código Lançamento'] == 16)&
            (lalur['Data Inicial'].dt.year == self.ano) &
            (lalur['Data Inicial'].dt.month >= self.mes_inicio) &
            (lalur['Data Inicial'].dt.month <= self.mes_fim)&
            (lalur['Trimestre'] == self.trimestre)]
        self.reducaoImposto = sum([filtro1['Vlr Lançamento'].sum(),filtro2['Vlr Lançamento'].sum()])

        self.results = pd.concat([self.results, pd.DataFrame([{"Operation": "(-)Isenção e Redução do Imposto", "Value": self.reducaoImposto}])], ignore_index=True )      
        self.trimestralLacsLalurAposInovacoes = pd.concat([self.trimestralLacsLalurAposInovacoes, pd.DataFrame([{"Operation": "(-)Isenção e Redução do Imposto", "Value": self.reducaoImposto}])], ignore_index=True )      

    
    def impostoRetFonte(self):

        lalur = self.ec630
        lalur = lalur[
            (lalur['Código Lançamento'] == 20)&
            (lalur['Data Inicial'].dt.year == self.ano) &
            (lalur['Data Inicial'].dt.month >= self.mes_inicio) &
            (lalur['Data Inicial'].dt.month <= self.mes_fim)&
            (lalur['Trimestre'] == self.trimestre)]
        
        self.impostRetFonte = np.sum(lalur['Vlr Lançamento'].values)

        self.results = pd.concat([self.results, pd.DataFrame([{"Operation": "(-)Imposto de Renda Retido na Fonte", "Value": self.impostRetFonte}])], ignore_index=True )      
        self.trimestralLacsLalurAposInovacoes = pd.concat([self.trimestralLacsLalurAposInovacoes, pd.DataFrame([{"Operation": "(-)Imposto de Renda Retido na Fonte", "Value": self.impostRetFonte}])], ignore_index=True )      

    
    def impostoRetFonteOrgsAutarquias(self):

        lalur = self.ec630
        lalur = lalur[
            (lalur['Código Lançamento'] == 21)&
            (lalur['Data Inicial'].dt.year == self.ano) &
            (lalur['Data Inicial'].dt.month >= self.mes_inicio) &
            (lalur['Data Inicial'].dt.month <= self.mes_fim)&
            (lalur['Trimestre'] == self.trimestre)]
        
        self.impostRetFonteOrgAut = np.sum(lalur['Vlr Lançamento'].values)

        self.results = pd.concat([self.results, pd.DataFrame([{"Operation": "(-)Imposto de Renda Retido na Fonte por Órgãos, Autarquias e Fundações Federais (Lei nº 9.430/1996, art. 64)", "Value": self.impostRetFonteOrgAut}])],
                                  ignore_index=True )      
        self.trimestralLacsLalurAposInovacoes = pd.concat([self.trimestralLacsLalurAposInovacoes, pd.DataFrame([{"Operation": "(-)Imposto de Renda Retido na Fonte por Órgãos, Autarquias e Fundações Federais (Lei nº 9.430/1996, art. 64)", "Value": self.impostRetFonteOrgAut}])],
                                  ignore_index=True )      

    
    def impostoRetFonteDemaisEntidades(self):

        lalur = self.ec630
        lalur = lalur[
            (lalur['Código Lançamento'] == 22)&
            (lalur['Data Inicial'].dt.year == self.ano) &
            (lalur['Data Inicial'].dt.month >= self.mes_inicio) &
            (lalur['Data Inicial'].dt.month <= self.mes_fim)&
            (lalur['Trimestre'] == self.trimestre)]
        
        self.impostRetFonteDemEnti = np.sum(lalur['Vlr Lançamento'].values)

        self.results = pd.concat([self.results, pd.DataFrame([{"Operation": "(-)Imposto de Renda Retido na Fonte pelas Demais Entidades da Administração Pública Federal (Lei n° 10.833/2003, art. 34)",
                                                                "Value": self.impostRetFonteDemEnti}])], ignore_index=True )      
        self.trimestralLacsLalurAposInovacoes = pd.concat([self.trimestralLacsLalurAposInovacoes, pd.DataFrame([{"Operation": "(-)Imposto de Renda Retido na Fonte pelas Demais Entidades da Administração Pública Federal (Lei n° 10.833/2003, art. 34)",
                                                                "Value": self.impostRetFonteDemEnti}])], ignore_index=True )      
     
    
    def impostoRendaRV(self):

        lalur = self.ec630
        lalur = lalur[
            (lalur['Código Lançamento'] == 23)&
            (lalur['Data Inicial'].dt.year == self.ano) &
            (lalur['Data Inicial'].dt.month >= self.mes_inicio) &
            (lalur['Data Inicial'].dt.month <= self.mes_fim)&
            (lalur['Trimestre'] == self.trimestre)]
        
        self.impostRV = np.sum(lalur['Vlr Lançamento'].values)

        self.results = pd.concat([self.results, pd.DataFrame([{"Operation": "(-)Imposto Pago Incidente sobre Ganhos no Mercado de Renda Variável",
                                                                "Value": self.impostRV}])], ignore_index=True )      
        self.trimestralLacsLalurAposInovacoes = pd.concat([self.trimestralLacsLalurAposInovacoes, pd.DataFrame([{"Operation": "(-)Imposto Pago Incidente sobre Ganhos no Mercado de Renda Variável",
                                                                "Value": self.impostRV}])], ignore_index=True )      

    
    def impostoRendPagoEfe(self):

        lalur = self.ec630
        lalur = lalur[
            (lalur['Código Lançamento'] == 24)&
            (lalur['Data Inicial'].dt.year == self.ano) &
            (lalur['Data Inicial'].dt.month >= self.mes_inicio) &
            (lalur['Data Inicial'].dt.month <= self.mes_fim)&
            (lalur['Trimestre'] == self.trimestre)]
        
        self.impostRendaPago = np.sum(lalur['Vlr Lançamento'].values)

        self.results = pd.concat([self.results, pd.DataFrame([{"Operation": "(-)Imposto de Renda Mensal Efetivamente Pago por Estimativa",
                                                                "Value": self.impostRendaPago}])], ignore_index=True )      
        self.trimestralLacsLalurAposInovacoes = pd.concat([self.trimestralLacsLalurAposInovacoes, pd.DataFrame([{"Operation": "(-)Imposto de Renda Mensal Efetivamente Pago por Estimativa",
                                                                "Value": self.impostRendaPago}])], ignore_index=True )      

    def subTotal(self):
        self.subtotal = (self.totalDevido - self.PAT - 
                         self.operCultuArtistico - self.reducaoImposto - 
                         self.impostRetFonte - self.impostRetFonteOrgAut - 
                         self.impostRetFonteDemEnti - self.impostRV - 
                         self.impostRendaPago)
        
        self.add_result("Sub total IRPJ a Recolher", self.subtotal)
        self.trimestralLacsLalurAposInovacoes = pd.concat([self.trimestralLacsLalurAposInovacoes, pd.DataFrame([{"Operation": "Sub total IRPJ a Recolher",
                                                                "Value": self.subtotal}])], ignore_index=True )      
 
    @functools.cache
    def runPipeLacsLalurIRPJ(self):
        self.LucroLiquidoAntesIRPJ()
        self.adicoesIRPJ()
        self.clss()
        self.demaisAdicoes()
        self.exclusoesIRPJ()
        self.baseCalculoIRPJ()
        self.CompPrejuFiscal()
        self.lucroReal()
        self.valorIRPJ()
        self.valorIRPJadicionais()
        self.totalDevidoIRPJantesRetencao()
        self.pat()
        self.operacoesCulturalArtistico()
        self.insencaoRedImposto()
        self.impostoRetFonte()
        self.impostoRetFonteOrgsAutarquias()
        self.impostoRetFonteDemaisEntidades()
        self.impostoRendaRV()
        self.impostoRendPagoEfe()
        self.subTotal()

        self.dataframeFinalIRPJ = pd.DataFrame(self.results)
        
        return self.dataframeFinalIRPJ


    def runPipeFinalTabelLacsLalur(self):
        self.baseCSLL()
        self.LucroLiquidoAntesIRPJ()

    @functools.cache
    def trimestralLacsLalurAposInovacoesFn(self):
        self.lucroAntesCSLL()
        self.calcAdicoes()
        self.exclusoes()
        self.baseDeCalculo()
        self.compensacaoPrejuizo()
        self.baseCSLL()
        self.valorCSLL()
        self.retencoesFonte()
        self.retencoesOrgPublicos()
        self.impostoPorEstimativa()
        self.subTotalCSLLRecolher()
        self.LucroLiquidoAntesIRPJ()
        self.adicoesIRPJ()
        self.clss()
        self.demaisAdicoes()
        self.exclusoesIRPJ()
        self.baseCalculoIRPJ()
        self.CompPrejuFiscal()
        self.lucroReal()
        self.valorIRPJ()
        self.valorIRPJadicionais()
        self.totalDevidoIRPJantesRetencao()
        self.pat()
        self.operacoesCulturalArtistico()
        self.insencaoRedImposto()
        self.impostoRetFonte()
        self.impostoRetFonteOrgsAutarquias()
        self.impostoRetFonteDemaisEntidades()
        self.impostoRendaRV()
        self.impostoRendPagoEfe()
        self.subTotal()
        
        if isinstance(self.trimestralLacsLalurAposInovacoes, pd.DataFrame):
            self.triLacsLalurFinal = self.trimestralLacsLalurAposInovacoes
        else:
            self.triLacsLalurFinal = pd.DataFrame({'Value': [self.trimestralLacsLalurAposInovacoes]})

        return self.trimestralLacsLalurAposInovacoes        
    



