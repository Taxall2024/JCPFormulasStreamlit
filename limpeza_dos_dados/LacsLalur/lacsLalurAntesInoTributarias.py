import pandas as pd
import streamlit as st
import numpy as np
import functools
from functools import wraps
import gc


class LacsLalurCSLL():
    
    @st.cache_data(ttl='1d', persist=False)
    @staticmethod
    def load_excel_file(file_path):
        return pd.read_excel(file_path)

    
    
    def __init__(self,data,lacs_file, lalur_file, ecf670_file, ec630_file):
        print('hello world')

        self.lacs = LacsLalurCSLL.load_excel_file(lacs_file)
        self.lalur = LacsLalurCSLL.load_excel_file(lalur_file)
        self.ecf670 = LacsLalurCSLL.load_excel_file(ecf670_file)
        self.ec630 = LacsLalurCSLL.load_excel_file(ec630_file)

        self.lacsFiltrado = self.lacs[self.lacs['Período Apuração']=='A00 – Receita Bruta/Balanço de Suspensão e Redução Anual']
        self.lalurFiltrado = self.lalur[self.lalur['Período Apuração']=='A00 – Receita Bruta/Balanço de Suspensão e Redução Anual']
        self.ec670Filtrado = self.ecf670[self.ecf670['Período Apuração']=='A00 – Receita Bruta/Balanço de Suspensão e Redução Anual']
        self.ec630Filtrado = self.ec630[self.ec630['Período Apuração']=='A00 – Receita Bruta/Balanço de Suspensão e Redução Anual']

        gc.collect()
        print("GARBAGE COLECTOR,GARBAGE COLECTOR,GARBAGE COLECTOR,GARBAGE COLECTOR,GARBAGE COLECTOR,GARBAGE COLECTOR,GARBAGE COLECTOR")
        print(gc.get_stats())

        self.resultsLacs = pd.DataFrame(columns=["Operation", "Value"])
        self.results = pd.DataFrame(columns=["Operation", "Value"])
        self.resultsTabelaFinal = pd.DataFrame(columns=["Operation", "Value"])
        self.LacsLalurAposInovacoes = pd.DataFrame(columns=["Operation", "Value"])

        self.lucro_periodo_value = 0 
        self.data = data

    #       CSLL ----

    #As funções abaixo utilizam como base para os calculos as a planilha LACS, 
    
    
    def lucroAntesCSLL(self):
        
        lacs = self.lacsFiltrado   
        lacs = lacs[(
            lacs['Código Lançamento e-Lacs']== 2)&
            (lacs['Data Inicial'].str.contains(self.data))]
        self.lucroAntCSLL = np.sum(lacs['Vlr Lançamento e-Lacs'].values)
        
        self.resultsLacs = pd.concat([self.resultsLacs, pd.DataFrame([{"Operation": "Lucro antes CSLL", "Value": self.lucroAntCSLL}])], ignore_index=True)
        self.LacsLalurAposInovacoes = pd.concat([self.LacsLalurAposInovacoes, pd.DataFrame([{"Operation": "Lucro antes CSLL", "Value": self.lucroAntCSLL}])], ignore_index=True)

    
    def adicoes(self):
        
        lacs = self.lacsFiltrado   
        lacs = lacs[(
            lacs['Código Lançamento e-Lacs']== 93)&
            (lacs['Data Inicial'].str.contains(self.data))]
        self.audicoes = np.sum(lacs['Vlr Lançamento e-Lacs'].values)

        self.resultsLacs = pd.concat([self.resultsLacs, pd.DataFrame([{"Operation": "Adições", "Value": self.audicoes}])], ignore_index=True)
        self.LacsLalurAposInovacoes = pd.concat([self.LacsLalurAposInovacoes, pd.DataFrame([{"Operation": "Adições", "Value": self.audicoes}])], ignore_index=True)
    
    
    def exclusoes(self):
        
        lacs = self.lacsFiltrado   
        lacs = lacs[(
            lacs['Código Lançamento e-Lacs']== 168)&
            (lacs['Data Inicial'].str.contains(self.data))]
        self.exclusao = np.sum(lacs['Vlr Lançamento e-Lacs'].values)

        self.resultsLacs = pd.concat([self.resultsLacs, pd.DataFrame([{"Operation": "Exclusões", "Value": self.exclusao}])], ignore_index=True)
        self.LacsLalurAposInovacoes = pd.concat([self.LacsLalurAposInovacoes, pd.DataFrame([{"Operation": "Exclusões", "Value": self.exclusao}])], ignore_index=True)

    
    def baseDeCalculo(self):
        self.baseCalculoCls = self.lucroAntCSLL + self.audicoes - self.exclusao
        self.resultsLacs = pd.concat([self.resultsLacs, pd.DataFrame([{"Operation": "Base de Cálculo", "Value": self.baseCalculoCls}])], ignore_index=True)         
        self.LacsLalurAposInovacoes = pd.concat([self.LacsLalurAposInovacoes, pd.DataFrame([{"Operation": "Base de Cálculo", "Value": self.baseCalculoCls}])], ignore_index=True)
    
    def compensacaoPrejuizo(self):
        lalur = self.lalurFiltrado
        lalur = lalur[(
            lalur['Código Lançamento e-Lalur'] == 173)&
            (lalur['Data Inicial'].str.contains(self.data))]
        self.compensacao = np.sum(lalur['Vlr Lançamento e-Lalur'].values)

        self.resultsLacs = pd.concat([self.resultsLacs, pd.DataFrame([{"Operation": "Compensação de Prejuízo", "Value": self.compensacao}])], ignore_index=True)
        self.LacsLalurAposInovacoes = pd.concat([self.LacsLalurAposInovacoes, pd.DataFrame([{"Operation": "Compensação de Prejuízo", "Value": self.compensacao}])], ignore_index=True)
    
    def baseCSLL(self):
        self.basecSLL = self.baseCalculoCls - self.compensacao
        self.resultsLacs = pd.concat([self.resultsLacs, pd.DataFrame([{"Operation": "Base CSLL", "Value": self.basecSLL}])], ignore_index=True)
        self.resultsTabelaFinal = pd.concat([self.resultsTabelaFinal, pd.DataFrame([{"Operation": "Base CSLL", "Value": self.basecSLL}])], ignore_index=True)
        self.LacsLalurAposInovacoes = pd.concat([self.LacsLalurAposInovacoes, pd.DataFrame([{"Operation": "Base CSLL", "Value": self.basecSLL}])], ignore_index=True)
    
    def valorCSLL(self):
        self.valorcSLL = np.where(self.basecSLL<0,0,self.basecSLL*0.09)
        self.resultsLacs = pd.concat([self.resultsLacs, pd.DataFrame([{"Operation": "Valor CSLL", "Value": self.valorcSLL}])], ignore_index=True)
        self.LacsLalurAposInovacoes = pd.concat([self.LacsLalurAposInovacoes, pd.DataFrame([{"Operation": "Valor CSLL", "Value": self.valorcSLL}])], ignore_index=True)
    
    def retencoesFonte(self):

        lalur = self.lalurFiltrado
        lalur = lalur[(
            lalur['Código Lançamento e-Lalur']== 17)&
            (lalur['Data Inicial'].str.contains(self.data))]
        self.retencoes = np.sum(lalur['Vlr Lançamento e-Lalur'].values)

        self.resultsLacs = pd.concat([self.resultsLacs, pd.DataFrame([{"Operation": "Renteções fonte", "Value": self.retencoes}])], ignore_index=True)
        self.LacsLalurAposInovacoes = pd.concat([self.LacsLalurAposInovacoes, pd.DataFrame([{"Operation": "Renteções fonte", "Value": self.retencoes}])], ignore_index=True)
    #As função abaixo utiliza como base para os calculos as planilhas do ECF 670
    
    def retencoesOrgPublicos(self):

        lalur = self.ec670Filtrado
        filtroUm = lalur[(
            lalur['Código Lançamento']== 15)&
            (lalur['Data Inicial'].str.contains(self.data))]

        filtroDois = lalur[(
            lalur['Código Lançamento']== 16)&
            (lalur['Data Inicial'].str.contains(self.data))]

        filtroTres = lalur[(
            lalur['Código Lançamento']== 18)&
            (lalur['Data Inicial'].str.contains(self.data))]
        
                                
        self.retencoesOrgPub = sum([filtroUm['Vlr Lançamento'].sum(),
                                filtroDois['Vlr Lançamento'].sum(),
                                filtroTres['Vlr Lançamento'].sum()])

        self.resultsLacs = pd.concat([self.resultsLacs, pd.DataFrame([{"Operation": "Retenções orgãos publicos", "Value": self.retencoesOrgPub}])], ignore_index=True)
        self.LacsLalurAposInovacoes = pd.concat([self.LacsLalurAposInovacoes, pd.DataFrame([{"Operation": "Retenções orgãos publicos", "Value": self.retencoesOrgPub}])], ignore_index=True)

    
    def impostoPorEstimativa(self):
        ecf760 = self.ec670Filtrado
        ecf760 = ecf760[(
            ecf760['Código Lançamento']== 19)&
            (ecf760['Data Inicial'].str.contains(self.data))]
        
        self.impostoPorEstim = ecf760['Vlr Lançamento'].sum()
        self.resultsLacs = pd.concat([self.resultsLacs, pd.DataFrame([{"Operation": "Imposto por estimativa", "Value": self.impostoPorEstim}])], ignore_index=True)
        self.LacsLalurAposInovacoes = pd.concat([self.LacsLalurAposInovacoes, pd.DataFrame([{"Operation": "Imposto por estimativa", "Value": self.impostoPorEstim}])], ignore_index=True)

    
    def subTotalCSLLRecolher(self):
        self.subTotalcl = self.valorcSLL - self.retencoes - self.retencoesOrgPub - self.impostoPorEstim
        self.resultsLacs = pd.concat([self.resultsLacs, pd.DataFrame([{"Operation": "Subtotal CSLL a recolher", "Value": self.subTotalcl}])], ignore_index=True)
        self.LacsLalurAposInovacoes = pd.concat([self.LacsLalurAposInovacoes, pd.DataFrame([{"Operation": "Subtotal CSLL a recolher", "Value": self.subTotalcl}])], ignore_index=True)
      
    
    def runPipeLacsLalurCSLL(self):

        self.lucroAntesCSLL()
        self.adicoes()
        self.exclusoes()
        self.baseDeCalculo()
        self.compensacaoPrejuizo()
        self.baseCSLL()
        self.valorCSLL()
        self.retencoesFonte()
        self.retencoesOrgPublicos()
        self.impostoPorEstimativa()
        self.subTotalCSLLRecolher()
        
        self.resultsLacs['Value'] =  self.resultsLacs['Value'].apply(lambda x: "{:,.2f}".format(x)).str.replace('.','_').str.replace(',','.').str.replace('_',',')
   
        st.dataframe(self.resultsLacs)

        return self.resultsLacs

        
    #       IRPJ ----
    
    def LucroLiquidoAntesIRPJ(self):

        lalur = self.lalurFiltrado

        lalur = lalur[(
            self.lalur['Código Lançamento e-Lalur'] == 2)&
            (lalur['Data Inicial'].str.contains(self.data))]
        
        self.lucroAntIRPJ = np.sum(lalur['Vlr Lançamento e-Lalur'].values)

        self.results = pd.concat([self.results, pd.DataFrame([{"Operation": "Lucro antes IRPJ", "Value": self.lucroAntIRPJ}])], ignore_index=True)
        self.resultsTabelaFinal = pd.concat([self.resultsTabelaFinal, pd.DataFrame([{"Operation": "Lucro antes IRPJ", "Value": self.lucroAntIRPJ}])], ignore_index=True)
        self.LacsLalurAposInovacoes = pd.concat([self.LacsLalurAposInovacoes, pd.DataFrame([{"Operation": "Lucro antes IRPJ", "Value": self.lucroAntIRPJ}])], ignore_index=True)

    
    def clss(self):

        lalur = self.lalurFiltrado  
        lalur = lalur[(
            self.lalur['Código Lançamento e-Lalur'] == 9)&
            (lalur['Data Inicial'].str.contains(self.data))]
        
        self.contrilss = np.sum(lalur['Vlr Lançamento e-Lalur'].values)

        self.results = pd.concat([self.results, pd.DataFrame([{"Operation": "Contribuição Social Sobre o Lucro Líquido - CSLL", "Value": self.contrilss}])], ignore_index=True)
        self.LacsLalurAposInovacoes = pd.concat([self.LacsLalurAposInovacoes, pd.DataFrame([{"Operation": "Contribuição Social Sobre o Lucro Líquido - CSLL", "Value": self.contrilss}])], ignore_index=True)

    
    def demaisAdicoes(self):

        lalur = self.lalurFiltrado  
        filtroUm = lalur[(
            self.lalur['Código Lançamento e-Lalur'] == 93)&
            (lalur['Data Inicial'].str.contains(self.data))]
        
        filtroDois = lalur[(
            self.lalur['Código Lançamento e-Lalur'] == 9)&
            (lalur['Data Inicial'].str.contains(self.data))]
        
        self.demaisAd = filtroUm['Vlr Lançamento e-Lalur'].sum() - filtroDois['Vlr Lançamento e-Lalur'].sum()

        self.results = pd.concat([self.results, pd.DataFrame([{"Operation": "Demais Adições", "Value": self.demaisAd}])], ignore_index=True)
        self.LacsLalurAposInovacoes = pd.concat([self.LacsLalurAposInovacoes, pd.DataFrame([{"Operation": "Demais Adições", "Value": self.demaisAd}])], ignore_index=True)

    
    def adicoesIRPJ(self):

        clss = self.lalurFiltrado  
        clss = clss[(
            clss['Código Lançamento e-Lalur'] == 9)&
            (clss['Data Inicial'].str.contains(self.data))]
        
        self.contrilss = clss['Vlr Lançamento e-Lalur'].sum()

        lalur = self.lalurFiltrado  
        filtroUm = lalur[(
            self.lalur['Código Lançamento e-Lalur'] == 93)&
            (lalur['Data Inicial'].str.contains(self.data))]
        
        filtroDois = lalur[(
            self.lalur['Código Lançamento e-Lalur'] == 9)&
            (lalur['Data Inicial'].str.contains(self.data))]
        
        self.demaisAd = filtroUm['Vlr Lançamento e-Lalur'].sum() - filtroDois['Vlr Lançamento e-Lalur'].sum()


        self.adicoesIRPj = self.contrilss + self.demaisAd

        self.results = pd.concat([self.results, pd.DataFrame([{"Operation": "Adições IRPJ", "Value": self.adicoesIRPj}])], ignore_index=True)
        self.LacsLalurAposInovacoes = pd.concat([self.LacsLalurAposInovacoes, pd.DataFrame([{"Operation": "Adições IRPJ", "Value": self.adicoesIRPj}])], ignore_index=True)

    
    def exclusoesIRPJ(self):

        lalur = self.lalurFiltrado  
        lalur = lalur[(
            self.lalur['Código Lançamento e-Lalur'] == 168)&
            (lalur['Data Inicial'].str.contains(self.data))]
        
        self.exclusoeS = np.sum(lalur['Vlr Lançamento e-Lalur'].values)

        self.results = pd.concat([self.results, pd.DataFrame([{"Operation": "Exclusoes", "Value": self.exclusoeS}])], ignore_index=True)
        self.LacsLalurAposInovacoes = pd.concat([self.LacsLalurAposInovacoes, pd.DataFrame([{"Operation": "Exclusoes", "Value": self.exclusoeS}])], ignore_index=True)

    
    def baseCalculoIRPJ(self):

        self.baseCalIRPJ = self.lucroAntIRPJ + self.adicoesIRPj - self.exclusoeS

        self.results = pd.concat([self.results, pd.DataFrame([{"Operation": "Base de cálculo", "Value": self.baseCalIRPJ}])], ignore_index=True)
        self.LacsLalurAposInovacoes = pd.concat([self.LacsLalurAposInovacoes, pd.DataFrame([{"Operation": "Base de cálculo", "Value": self.baseCalIRPJ}])], ignore_index=True)
    
    
    def CompPrejuFiscal(self):

        lalur = self.lalurFiltrado  
        lalur = lalur[(
                        lalur['Código Lançamento e-Lalur'] == 173)&
                        (lalur['Data Inicial'].str.contains(self.data))]
        
        self.compPrejFiscal = np.sum(lalur['Vlr Lançamento e-Lalur'].values)

        self.results = pd.concat([self.results, pd.DataFrame([{"Operation": "Compensação Prejuízo fiscal", "Value": self.compPrejFiscal}])], ignore_index=True)        
        self.LacsLalurAposInovacoes = pd.concat([self.LacsLalurAposInovacoes, pd.DataFrame([{"Operation": "Compensação Prejuízo fiscal", "Value": self.compPrejFiscal}])], ignore_index=True)        

    
    def lucroReal(self):
        self.lucroRel= self.baseCalIRPJ - self.compPrejFiscal
        self.results = pd.concat([self.results, pd.DataFrame([{"Operation": "Lucro Real", "Value": self.lucroRel}])], ignore_index=True)
        self.LacsLalurAposInovacoes = pd.concat([self.LacsLalurAposInovacoes, pd.DataFrame([{"Operation": "Lucro Real", "Value": self.lucroRel}])], ignore_index=True)

    
    def valorIRPJ(self):
        self.valorIRPj = np.where(self.lucroRel<0,0,self.lucroRel*0.15)
        self.results = pd.concat([self.results, pd.DataFrame([{"Operation": "Valor IRPJ", "Value": self.valorIRPj}])], ignore_index=True)
        self.LacsLalurAposInovacoes = pd.concat([self.LacsLalurAposInovacoes, pd.DataFrame([{"Operation": "Valor IRPJ", "Value": self.valorIRPj}])], ignore_index=True)

    
    def valorIRPJadicionais(self):
        self.valorIRPJAd = np.where(self.lucroRel>240000,(self.lucroRel-240000)*0.10,0)
        self.results = pd.concat([self.results, pd.DataFrame([{"Operation": "Valor IRPJ Adicionais", "Value": self.valorIRPJAd}])], ignore_index=True)
        self.LacsLalurAposInovacoes = pd.concat([self.LacsLalurAposInovacoes, pd.DataFrame([{"Operation": "Valor IRPJ Adicionais", "Value": self.valorIRPJAd}])], ignore_index=True)

    
    def totalDevidoIRPJantesRetencao(self):
        self.totalDevido = self.valorIRPj + self.valorIRPJAd
        self.results = pd.concat([self.results, pd.DataFrame([{"Operation": "Total devido IRPJ antes da retenção", "Value": self.totalDevido}])], ignore_index=True)    
        self.LacsLalurAposInovacoes = pd.concat([self.LacsLalurAposInovacoes, pd.DataFrame([{"Operation": "Total devido IRPJ antes da retenção", "Value": self.totalDevido}])], ignore_index=True)    

    #A função abaixo utiliza como base para os calculos as planilhas do ECF 630
    
    def pat(self):

        lalur = self.ec630Filtrado
        lalur = lalur[(
            lalur['Código Lançamento'] == 8)&
            (lalur['Data Inicial'].str.contains(self.data))]
        
        self.PAT = lalur['Vlr Lançamento'].sum()

        self.results = pd.concat([self.results, pd.DataFrame([{"Operation": "PAT", "Value": self.PAT}])], ignore_index=True) 
        self.LacsLalurAposInovacoes = pd.concat([self.LacsLalurAposInovacoes, pd.DataFrame([{"Operation": "PAT", "Value": self.PAT}])], ignore_index=True) 

    
    def operacoesCulturalArtistico(self):

        lalur = self.ec630Filtrado
        lalur = lalur[(
            lalur['Código Lançamento'] == 6)&
            (lalur['Data Inicial'].str.contains(self.data))]
        
        self.operCultuArtistico = lalur['Vlr Lançamento'].sum()

        self.results = pd.concat([self.results, pd.DataFrame([{"Operation": "(-)Operações de Caráter Cultural e Artístico", "Value": self.operCultuArtistico}])], ignore_index=True )      
        self.LacsLalurAposInovacoes = pd.concat([self.LacsLalurAposInovacoes, pd.DataFrame([{"Operation": "(-)Operações de Caráter Cultural e Artístico", "Value": self.operCultuArtistico}])], ignore_index=True )      

    
    def insencaoRedImposto(self):

        lalur = self.ec630Filtrado
        lalur = lalur[(
                    lalur['Código Lançamento'] == 17)&
                    (lalur['Data Inicial'].str.contains(self.data))]
                
        self.reducaoImposto = lalur['Vlr Lançamento'].sum()

        self.results = pd.concat([self.results, pd.DataFrame([{"Operation": "(-)Isenção e Redução do Imposto", "Value": self.reducaoImposto}])], ignore_index=True )      
        self.LacsLalurAposInovacoes = pd.concat([self.LacsLalurAposInovacoes, pd.DataFrame([{"Operation": "(-)Isenção e Redução do Imposto", "Value": self.reducaoImposto}])], ignore_index=True )      

    
    def impostoRetFonte(self):

        lalur = self.ec630Filtrado
        lalur = lalur[(
                    lalur['Código Lançamento'] == 20)&
                    (lalur['Data Inicial'].str.contains(self.data))]
                
        self.impostRetFonte = lalur['Vlr Lançamento'].sum()

        self.results = pd.concat([self.results, pd.DataFrame([{"Operation": "(-)Imposto de Renda Retido na Fonte", "Value": self.impostRetFonte}])], ignore_index=True )      
        self.LacsLalurAposInovacoes = pd.concat([self.LacsLalurAposInovacoes, pd.DataFrame([{"Operation": "(-)Imposto de Renda Retido na Fonte", "Value": self.impostRetFonte}])], ignore_index=True )      

    
    def impostoRetFonteOrgsAutarquias(self):

        lalur = self.ec630Filtrado
        lalur = lalur[(
            lalur['Código Lançamento'] == 21)&
            (lalur['Data Inicial'].str.contains(self.data))]
        
        self.impostRetFonteOrgAut = lalur['Vlr Lançamento'].sum()

        self.results = pd.concat([self.results, pd.DataFrame([{"Operation": "(-)Imposto de Renda Retido na Fonte por Órgãos, Autarquias e Fundações Federais (Lei nº 9.430/1996, art. 64)", "Value": self.impostRetFonteOrgAut}])],
                                  ignore_index=True )      
        self.LacsLalurAposInovacoes = pd.concat([self.LacsLalurAposInovacoes, pd.DataFrame([{"Operation": "(-)Imposto de Renda Retido na Fonte por Órgãos, Autarquias e Fundações Federais (Lei nº 9.430/1996, art. 64)", "Value": self.impostRetFonteOrgAut}])],
                                  ignore_index=True )      

    
    def impostoRetFonteDemaisEntidades(self):

        lalur = self.ec630Filtrado
        lalur = lalur[(
                    lalur['Código Lançamento'] == 22)&
                    (lalur['Data Inicial'].str.contains(self.data))]
                
        self.impostRetFonteDemEnti = lalur['Vlr Lançamento'].sum()

        self.results = pd.concat([self.results, pd.DataFrame([{"Operation": "(-)Imposto de Renda Retido na Fonte pelas Demais Entidades da Administração Pública Federal (Lei n° 10.833/2003, art. 34)",
                                                                "Value": self.impostRetFonteDemEnti}])], ignore_index=True )      
        self.LacsLalurAposInovacoes = pd.concat([self.LacsLalurAposInovacoes, pd.DataFrame([{"Operation": "(-)Imposto de Renda Retido na Fonte pelas Demais Entidades da Administração Pública Federal (Lei n° 10.833/2003, art. 34)",
                                                                "Value": self.impostRetFonteDemEnti}])], ignore_index=True )      
   
    
    def impostoRendaRV(self):

        lalur = self.ec630Filtrado
        lalur = lalur[(
            lalur['Código Lançamento'] == 23)&
            (lalur['Data Inicial'].str.contains(self.data))]
        
        self.impostRV = lalur['Vlr Lançamento'].sum()

        self.results = pd.concat([self.results, pd.DataFrame([{"Operation": "(-)Imposto Pago Incidente sobre Ganhos no Mercado de Renda Variável",
                                                                "Value": self.impostRV}])], ignore_index=True )      
        self.LacsLalurAposInovacoes = pd.concat([self.LacsLalurAposInovacoes, pd.DataFrame([{"Operation": "(-)Imposto Pago Incidente sobre Ganhos no Mercado de Renda Variável",
                                                                "Value": self.impostRV}])], ignore_index=True )      

    
    def impostoRendPagoEfe(self):

        lalur = self.ec630Filtrado
        lalur = lalur[(
                    lalur['Código Lançamento'] == 24)&
                    (lalur['Data Inicial'].str.contains(self.data))]
                
        self.impostRendaPago = lalur['Vlr Lançamento'].sum()

        self.results = pd.concat([self.results, pd.DataFrame([{"Operation": "(-)Imposto de Renda Mensal Efetivamente Pago por Estimativa",
                                                                "Value": self.impostRendaPago}])], ignore_index=True )      
        self.LacsLalurAposInovacoes = pd.concat([self.LacsLalurAposInovacoes, pd.DataFrame([{"Operation": "(-)Imposto de Renda Mensal Efetivamente Pago por Estimativa",
                                                                "Value": self.impostRendaPago}])], ignore_index=True )      

    
    def subTotal(self):

        self.subtotal = (self.totalDevido - self.PAT - 
                         self.operCultuArtistico - self.reducaoImposto - 
                         self.impostRetFonte - self.impostRetFonteOrgAut - 
                         self.impostRetFonteDemEnti - self.impostRV - 
                         self.impostRendaPago)

        self.results = pd.concat([self.results, pd.DataFrame([{"Operation": "Sub total IRPJ a Recolher",
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



        self.results['Value'] = self.results['Value'].apply(lambda x: "{:,.2f}".format(x)).str.replace('.','_').str.replace(',','.').str.replace('_',',')
        st.dataframe(self.results)
        return self.results
    

    def runPipeAposInovacoesLacsLalurCSLL(self):

        self.lucroAntesCSLL()
        self.adicoes()
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
        #self.LacsLalurAposInovacoes['Value'] = self.LacsLalurAposInovacoes['Value'].apply(lambda x: "{:,.2f}".format(x)).str.replace('.','_').str.replace(',','.').str.replace('_',',')

        return self.LacsLalurAposInovacoes  
      
    @functools.cache
    def runPipeFinalTabelLacsLalur(self):

        self.baseCSLL()
        self.LucroLiquidoAntesIRPJ()
        
        self.resultsTabelaFinal['Value'] = self.resultsTabelaFinal['Value'].apply(lambda x: f"{x:,.2f}")
        st.dataframe(self.resultsTabelaFinal)

# if __name__=='__main__':

#     data = st.text_input('Digite a data de referência', key='Lacs_Lalur')

#     lacs = LacsLalurCSLL(data)
#     lacs.runPipeLacsLalurCSLL()
    
#     lacs.runPipeLacsLalurIRPJ()








