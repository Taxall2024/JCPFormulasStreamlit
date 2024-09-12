import pandas as pd
import streamlit as st
import numpy as np
import openpyxl as op
import functools
import gc

from LacsLalur.lacsLalurAntesInoTributarias import LacsLalurCSLL




class FiltrandoDadosParaCalculo(LacsLalurCSLL):
    _widget_counter = 0


    @st.cache_data(ttl='1d',persist=False)
    @staticmethod
    def load_file(df):
            return df 
    
    #@st.cache_data(ttl='1d')
    def __init__(self, data, lacs_file, lalur_file, ecf670_file, ec630_file, l100_file, l300_file):
        self.data = None 
        super().__init__(data, lacs_file, lalur_file, ecf670_file, ec630_file)
        self.reservEstatuaria = 0.0
        self.resContingencia = 0.0
        self.reserExp = 0.0
        self.outrasResLuc = 0.0
        self.lucroAcumulado = 0.0
        self.reservLucro = 0.0


        #---ORBENK
        self.l100 = FiltrandoDadosParaCalculo.load_file(l100_file)
        self.l300 = FiltrandoDadosParaCalculo.load_file(l300_file)
        self.cnpj = self.l100.iloc[0]['CNPJ']


        self.resultsCalcJcp = pd.DataFrame(columns=["CNPJ","Operation", "Value","Ano"])
        self.resultsTabelaFinal = pd.DataFrame(columns=["CNPJ","Operation", "Value","Ano"]) 
        self.lucro_periodo_value = 0

        gc.collect()

    
    def set_date(self, data):
        self.data = data         
 
 
    def capitalSocial(self):
        l100 = self.l100
        l100 = l100[(l100['Período Apuração']=='A00 – Receita Bruta/Balanço de Suspensão e Redução Anual')&(
            l100['Descrição Conta Referencial']=='Capital Subscrito de Domiciliados e Residentes no País')&
            (l100['Data Inicial'].str.contains(self.data))]
        self.capSocial = float(np.sum(l100['Vlr Saldo Final'].values))

        self.resultsCalcJcp = pd.concat([self.resultsCalcJcp, pd.DataFrame([{"CNPJ":self.cnpj,"Operation": "Capital Social", "Value": self.capSocial,
                                                                             "Ano": self.data}])], ignore_index=True)

    def capitalIntegralizador(self):
        l100 = self.l100
        l100 = l100[(l100['Conta Referencial']=='2.03.01.01.21')&(
            l100['Conta Referencial']=='2.03.01.02.10')&
            (l100['Data Inicial'].str.contains(self.data))]
        self.capitalIntegra = float(np.sum(l100['Vlr Saldo Final'].values))
        self.resultsCalcJcp = pd.concat([self.resultsCalcJcp, pd.DataFrame([{"Ano":self.data,"CNPJ":self.cnpj,"Operation": "Capital Integralizador", "Value": self.capitalIntegra}])], ignore_index=True)
    
    
    def ReservasDeCapital(self):
        l100 = self.l100
        l100 = l100[(l100['Conta Referencial']=='2.03.02.01.99')&
        (l100['Período Apuração']=='A00 – Receita Bruta/Balanço de Suspensão e Redução Anual')&
            (l100['Data Inicial'].str.contains(self.data))]
        self.reservaCapital = float(np.sum(l100['Vlr Saldo Final'].values))

        self.resultsCalcJcp = pd.concat([self.resultsCalcJcp, pd.DataFrame([{"Ano":self.data,"CNPJ":self.cnpj,"Operation": "Reservas de Capital", "Value": self.reservaCapital}])], ignore_index=True)


    def ajustesAvalPatrimonial(self):
        l100 = self.l100
        l100 = l100[(l100['Período Apuração']=='A00 – Receita Bruta/Balanço de Suspensão e Redução Anual')&
            (l100['Data Inicial'].str.contains(self.data))&(
            l100['Descrição Conta Referencial']=='Reavaliação de Ativos Próprios')]
        self.ajusteAvaPatrimonial = float(np.sum(l100['Vlr Saldo Final'].values))

        self.resultsCalcJcp = pd.concat([self.resultsCalcJcp, pd.DataFrame([{"Ano":self.data,"CNPJ":self.cnpj,"Operation": "Ajustes Avaliação Patrimonial", "Value": self.ajusteAvaPatrimonial}])], ignore_index=True)

             
    def lucrosAcumulados(self):

        l100 = self.l100
        l300 = self.l300

        lucroperio = l300[(l300['Descrição Conta Referencial']=='RESULTADO LÍQUIDO DO PERÍODO')&
            (l300['Data Inicial'].str.contains(self.data))&(
            l300['Período Apuração']=='A00 – Receita Bruta/Balanço de Suspensão e Redução Anual')]
        lucroperio = lucroperio['Vlr Saldo Final'].sum()

        l100 = l100[(l100['Conta Referencial']=='2.03.04.01.01')&
            (l100['Data Inicial'].str.contains(self.data))&(
            l100['Período Apuração']=='A00 – Receita Bruta/Balanço de Suspensão e Redução Anual')]
        self.lucroAcumulado = np.where(
            float(np.sum(l100['Vlr Saldo Final'].values) - lucroperio) < 0,
            0,
            float(np.sum(l100['Vlr Saldo Final'].values) - lucroperio)
)
        self.resultsCalcJcp = pd.concat([self.resultsCalcJcp, pd.DataFrame([{"Ano":self.data,"CNPJ":self.cnpj,"Operation": "Lucros Acumulados", "Value": self.lucroAcumulado}])], ignore_index=True)
        self.resultsTabelaFinal = pd.concat([self.resultsTabelaFinal, pd.DataFrame([{"Ano":self.data,"CNPJ":self.cnpj,"Operation": "Lucros Acumulados", "Value": self.lucroAcumulado}])], ignore_index=True)
      
    
    def ajustesExerAnteriores(self):
        l100 = self.l100
        l100 = l100[(l100['Conta Referencial']=='2.03.04.01.10')&
            (l100['Data Inicial'].str.contains(self.data))&(
            l100['Período Apuração']=='A00 – Receita Bruta/Balanço de Suspensão e Redução Anual')]
        self.ajustExercAnt = float(np.sum(l100['Vlr Saldo Final'].values))

        self.resultsCalcJcp = pd.concat([self.resultsCalcJcp, pd.DataFrame([{"Ano":self.data,"CNPJ":self.cnpj,"Operation": "Exercícios Anteriores", "Value": self.ajustExercAnt}])], ignore_index=True)

        
    def lucroPeriodo(self):
        l100 = self.l300
        l100 = l100[(l100['Descrição Conta Referencial']=='RESULTADO LÍQUIDO DO PERÍODO')&
            (l100['Data Inicial'].str.contains(self.data))&(
            l100['Período Apuração']=='A00 – Receita Bruta/Balanço de Suspensão e Redução Anual')]
        self.lucro_periodo_value = float(np.sum(l100['Vlr Saldo Final'].values))
        self.resultsCalcJcp = pd.concat([self.resultsCalcJcp, pd.DataFrame([{"Ano":self.data,"CNPJ":self.cnpj,"Operation": "Lucro do Período", "Value": self.lucro_periodo_value}])], ignore_index=True)
        self.resultsTabelaFinal = pd.concat([self.resultsTabelaFinal, pd.DataFrame([{"Ano":self.data,"CNPJ":self.cnpj,"Operation": "Lucro do Período", "Value": self.lucro_periodo_value}])], ignore_index=True)


    def TotalFinsCalcJSPC(self):

        self.totalJSPC =  sum((self.capSocial,self.reservaCapital,self.lucroAcumulado,self.reservLucro,
                               self.contaPatriNClassifica,self.prejuizoPeirod,self.ajustExercAnt,
                               self.resultExercicio,self.lucroPrejAcumu))
        self.resultsCalcJcp = pd.concat([self.resultsCalcJcp, pd.DataFrame([{"Ano":self.data,"CNPJ":self.cnpj,"Operation": "Total Fins Calc JSPC", "Value": self.totalJSPC}])], ignore_index=True)
    

    def update_totalfinsparaJPC(self):
        self.totalJSPC = self.capSocial + self.reservaCapital + self.lucroAcumulado + self.reservLucro
        self.resultsCalcJcp = pd.concat([self.resultsCalcJcp, pd.DataFrame([{"Ano":self.data,"CNPJ":self.cnpj,"Operation": "Total Fins Calc JSPC", "Value": self.totalJSPC}])], ignore_index=True)


    def update_reservas(self):
        self.reservLucro = self.reservLegal + self.outrasResLuc
        self.resultsTabelaFinal.loc[self.resultsTabelaFinal['Operation'] == 'Reservas de Lucros', 'Value'] = self.reservLucro

    
    def ReservaLegal(self):

        self.reservLegal = 0.0
        self.resultsCalcJcp = pd.concat([self.resultsCalcJcp, pd.DataFrame([{"Ano":self.data,"CNPJ":self.cnpj,"Operation": "Reserva legal", "Value": self.reservLegal}])], ignore_index=True)



    def OutrasReservasLucros(self):

        self.outrasResLuc = 0.0

        self.resultsCalcJcp = pd.concat([self.resultsCalcJcp, pd.DataFrame([{"Ano":self.data,"CNPJ":self.cnpj,"Operation": "Outras Reservas de Lucros", "Value": self.outrasResLuc}])], ignore_index=True)
    

    def ResultadoDoExercicio(self):

        self.resultExercicio = 0.0

        self.resultsCalcJcp = pd.concat([self.resultsCalcJcp, pd.DataFrame([{"Ano":self.data,"CNPJ":self.cnpj,"Operation": "Resultado do Exercício", "Value": self.resultExercicio}])], ignore_index=True)

    def lucroPrejuAcumulado(self):

        self.lucroPrejAcumu = 0.0

        self.resultsCalcJcp = pd.concat([self.resultsCalcJcp, pd.DataFrame([{"Ano":self.data,"CNPJ":self.cnpj,"Operation": "Lucros/Prejuízos acumulados", "Value": self.lucroPrejAcumu}])], ignore_index=True)

    def ReservasLucros(self):
        self.reservLucro = self.reservLegal + self.outrasResLuc
        self.resultsCalcJcp = pd.concat([self.resultsCalcJcp, pd.DataFrame([{"Ano":self.data,"CNPJ":self.cnpj,"Operation": "Reservas de Lucros", "Value": self.reservLucro}])], ignore_index=True)
    

    def acoesTesouraria(self):

        l100 = self.l100
        l100 = l100[(l100['Conta Referencial']=='2.03.04.01.12')&
            (l100['Data Inicial'].str.contains(self.data))&(
            l100['Período Apuração']=='A00 – Receita Bruta/Balanço de Suspensão e Redução Anual')]
        self.acosTesouraria = float(np.sum(l100['Vlr Saldo Final'].values))
        self.resultsCalcJcp = pd.concat([self.resultsCalcJcp, pd.DataFrame([{"Ano":self.data,"CNPJ":self.cnpj,"Operation": "Ações em Tesouraria", "Value": self.acosTesouraria}])], ignore_index=True)

    def contPatrimonioNaoClass(self):

        l100 = self.l100
        l100 = l100[(l100['Conta Referencial']=='2.03.04.01.90')&
            (l100['Data Inicial'].str.contains(self.data))&(
            l100['Período Apuração']=='A00 – Receita Bruta/Balanço de Suspensão e Redução Anual')]
        self.contaPatriNClassifica = float(np.sum(l100['Vlr Saldo Final'].values))
        self.resultsCalcJcp = pd.concat([self.resultsCalcJcp, pd.DataFrame([{"Ano":self.data,"CNPJ":self.cnpj,"Operation": "Contas do Patrimônio Líquido Não Classificadas ", "Value": self.contaPatriNClassifica}])], ignore_index=True)
    
    
    def PrejuizoPeriodo(self):

        self.prejuizoPeirod = 0.0

        self.resultsCalcJcp = pd.concat([self.resultsCalcJcp, pd.DataFrame([{"Ano":self.data,"CNPJ":self.cnpj,"Operation": "Prejuízo do Período", "Value": self.prejuizoPeirod}])], ignore_index=True)
        
    
  
    def prejuizosAcumulados(self):

        l100 = self.l100
        l100 = l100[(l100['Conta Referencial']=='2.03.04.01.11')&
            (l100['Data Inicial'].str.contains(self.data))&(
            l100['Período Apuração']=='A00 – Receita Bruta/Balanço de Suspensão e Redução Anual')]
        self.contaPatriNClassifica = float(np.sum(l100['Vlr Saldo Final'].values)) * -1
        self.resultsCalcJcp = pd.concat([self.resultsCalcJcp, pd.DataFrame([{"Ano":self.data,"CNPJ":self.cnpj,"Operation": "Prejuízos Acumulados", "Value": self.contaPatriNClassifica}])], ignore_index=True)
    
    @functools.cache
    def runPipe(self):
           
            with st.expander('Inputs manuais : '):
                self.capitalSocial()
                self.capitalIntegralizador()
                self.ReservasDeCapital()
                self.ajustesAvalPatrimonial()
                self.lucroPrejuAcumulado()
                self.ResultadoDoExercicio()

                self.ReservaLegal()
                self.OutrasReservasLucros()
                self.ReservasLucros()

                self.acoesTesouraria()
                self.contPatrimonioNaoClass()
                self.PrejuizoPeriodo()
                self.prejuizosAcumulados()

                self.acoesTesouraria()
                self.lucrosAcumulados()
                self.ajustesExerAnteriores()
                self.lucroPeriodo()
                self.TotalFinsCalcJSPC()
            
            return self.resultsCalcJcp

    @functools.cache
    def runPipeFinalTable(self):

        self.exclusoes()
        self.adicoes()
        self.lucroAntesCSLL()
        self.baseDeCalculo()
        self.compensacaoPrejuizo()   
        self.LucroLiquidoAntesIRPJ()
        self.baseCSLL()

        return self.resultsTabelaFinal

# if __name__=='__main__':

#     jcp = FiltrandoDadosParaCalculo() 

#     jcp.runPipeFinalTable()
#     #jcp.runPipeFinalTabelLacsLalur()
#     st.subheader('Calculo JCP')
#     jcp.runPipe()
#     st.subheader('Lacs e Lalur ')
#     jcp.runPipeLacsLalurIRPJ()
#     jcp.runPipeLacsLalurCSLL()