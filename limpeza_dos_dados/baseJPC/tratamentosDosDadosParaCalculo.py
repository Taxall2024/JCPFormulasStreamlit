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
    def load_excel_file(file_path):
        return pd.read_excel(file_path) 
    
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
        self.l100 = FiltrandoDadosParaCalculo.load_excel_file(l100_file)
        self.l300 = FiltrandoDadosParaCalculo.load_excel_file(l300_file)


        self.resultsCalcJcp = pd.DataFrame(columns=["Operation", "Value"])
        self.resultsTabelaFinal = pd.DataFrame(columns=["Operation", "Value"]) 
        self.lucro_periodo_value = 0

        gc.collect()
        print("GARBAGE COLECTOR,GARBAGE COLECTOR,GARBAGE COLECTOR,GARBAGE COLECTOR,GARBAGE COLECTOR,GARBAGE COLECTOR,GARBAGE COLECTOR")
        print(gc.get_stats())
         

    
    def set_date(self, data):
        self.data = data         
 
 
    def capitalSocial(self):
        l100 = self.l100
        l100 = l100[(l100['Período Apuração']=='A00 – Receita Bruta/Balanço de Suspensão e Redução Anual')&(
            l100['Descrição Conta Referencial']=='Capital Subscrito de Domiciliados e Residentes no País')&
            (l100['Data Inicial'].str.contains(self.data))]
        self.capSocial = np.sum(l100['Vlr Saldo Final'].values)

        key = f'capitalSoc{self.data}'

        if key not in st.session_state:
            st.session_state[key] = float(self.capSocial)
        
        st.session_state[key] = st.session_state[key]

        self.capSocial = st.number_input('Ajuste Capital Social',key=key,value=st.session_state[key])

        self.resultsCalcJcp = pd.concat([self.resultsCalcJcp, pd.DataFrame([{"Operation": "Capital Social", "Value": self.capSocial}])], ignore_index=True)

 
    def capitalIntegralizador(self):
        l100 = self.l100
        l100 = l100[(l100['Conta Referencial']=='2.03.01.01.21')&(
            l100['Conta Referencial']=='2.03.01.02.10')&
            (l100['Data Inicial'].str.contains(self.data))]
        self.capitalIntegra = np.sum(l100['Vlr Saldo Final'].values)
        self.resultsCalcJcp = pd.concat([self.resultsCalcJcp, pd.DataFrame([{"Operation": "Capital Integralizador", "Value": self.capitalIntegra}])], ignore_index=True)
    
    
    def ReservasDeCapital(self):
        l100 = self.l100
        l100 = l100[(l100['Conta Referencial']=='2.03.02.01.99')&
        (l100['Período Apuração']=='A00 – Receita Bruta/Balanço de Suspensão e Redução Anual')&
            (l100['Data Inicial'].str.contains(self.data))]
        self.reservaCapital = np.sum(l100['Vlr Saldo Final'].values)
        key = f'ReservlCapital{self.data}'

        if key not in st.session_state:
            st.session_state[key] = self.reservaCapital
        
        st.session_state[key] = st.session_state[key]

        self.reservaCapital = st.number_input('Ajuste Reserva de Capital',key=key,value=st.session_state[key])
        self.resultsCalcJcp = pd.concat([self.resultsCalcJcp, pd.DataFrame([{"Operation": "Reservas de Capital", "Value": self.reservaCapital}])], ignore_index=True)


    def ajustesAvalPatrimonial(self):
        l100 = self.l100
        l100 = l100[(l100['Período Apuração']=='A00 – Receita Bruta/Balanço de Suspensão e Redução Anual')&
            (l100['Data Inicial'].str.contains(self.data))&(
            l100['Descrição Conta Referencial']=='Reavaliação de Ativos Próprios')]
        self.ajusteAvaPatrimonial = np.sum(l100['Vlr Saldo Final'].values)

        key = f'ajustAvaPatri{self.data}'

        if key not in st.session_state:
            st.session_state[key] = self.ajusteAvaPatrimonial
        st.session_state[key] = st.session_state[key]

        self.ajusteAvaPatrimonial = st.number_input('Ajuste Avaliação Patrimonial',key=key,value=st.session_state[key])
        self.resultsCalcJcp = pd.concat([self.resultsCalcJcp, pd.DataFrame([{"Operation": "Ajustes Avaliação Patrimonial", "Value": self.ajusteAvaPatrimonial}])], ignore_index=True)

             
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
        
        if (l100['D/C Saldo Final'] == 'C').any():
            self.lucroAcumulado = np.where(np.sum(l100['Vlr Saldo Final'].values)-lucroperio<0,0,np.sum(l100['Vlr Saldo Final'].values)-lucroperio)
        else:
            self.lucroAcumulado = np.sum(l100['Vlr Saldo Final'].values)
        
        self.lucroAcumulado = np.where(np.sum(l100['Vlr Saldo Final'].values)-lucroperio<0,0,np.sum(l100['Vlr Saldo Final'].values)-lucroperio)

        self.resultsCalcJcp = pd.concat([self.resultsCalcJcp, pd.DataFrame([{"Operation": "Lucros Acumulados", "Value": self.lucroAcumulado}])], ignore_index=True)
        self.resultsTabelaFinal = pd.concat([self.resultsTabelaFinal, pd.DataFrame([{"Operation": "Lucros Acumulados", "Value": self.lucroAcumulado}])], ignore_index=True)
      
    
    def ajustesExerAnteriores(self):
        l100 = self.l100
        l100 = l100[(l100['Conta Referencial']=='2.03.04.01.10')&
            (l100['Data Inicial'].str.contains(self.data))&(
            l100['Período Apuração']=='A00 – Receita Bruta/Balanço de Suspensão e Redução Anual')]
        self.ajustExercAnt = np.sum(l100['Vlr Saldo Final'].values)

        key = f'ajustExercAnte{self.data}'

        if key not in st.session_state:
            st.session_state[key] = self.ajustExercAnt
        st.session_state[key] = st.session_state[key]

        self.ajustExercAnt = st.number_input('Ajuste Exercícios Anteriores',key=key,value=st.session_state[key])
        self.resultsCalcJcp = pd.concat([self.resultsCalcJcp, pd.DataFrame([{"Operation": "Exercícios Anteriores", "Value": self.ajustExercAnt}])], ignore_index=True)

        
    def lucroPeriodo(self):
        l100 = self.l300
        l100 = l100[(l100['Descrição Conta Referencial']=='RESULTADO LÍQUIDO DO PERÍODO')&
            (l100['Data Inicial'].str.contains(self.data))&(
            l100['Período Apuração']=='A00 – Receita Bruta/Balanço de Suspensão e Redução Anual')]
        self.lucro_periodo_value = np.sum(l100['Vlr Saldo Final'].values)
        
        if (l100['D/C Saldo Final'] == 'C').any():
            lucroPrejuizo = 'Lucro do Período'
        else:
            lucroPrejuizo = 'Prejuízo do Período' 

        self.resultsCalcJcp = pd.concat([self.resultsCalcJcp, pd.DataFrame([{"Operation": f"{lucroPrejuizo}", "Value": self.lucro_periodo_value}])], ignore_index=True)
        self.resultsTabelaFinal = pd.concat([self.resultsTabelaFinal, pd.DataFrame([{"Operation": f"{lucroPrejuizo}", "Value": self.lucro_periodo_value}])], ignore_index=True)


    def TotalFinsCalcJSPC(self):

        self.totalJSPC =  sum((self.capSocial,self.reservaCapital,self.lucroAcumulado,self.reservLucro
                               ,self.prejuizoPeirod,self.ajustExercAnt,
                               self.resultExercicio,self.lucroPrejAcumu)) - self.prejuAcumulado
        
        self.resultsCalcJcp = pd.concat([self.resultsCalcJcp, pd.DataFrame([{"Operation": "Total Fins Calc JSPC", "Value": self.totalJSPC}])], ignore_index=True)
    

    def update_totalfinsparaJPC(self):
        self.totalJSPC = self.capSocial + self.reservaCapital + self.lucroAcumulado + self.reservLucro
        self.resultsCalcJcp = pd.concat([self.resultsCalcJcp, pd.DataFrame([{"Operation": "Total Fins Calc JSPC", "Value": self.totalJSPC}])], ignore_index=True)


    def update_reservas(self):
        self.reservLucro = self.reservLegal + self.outrasResLuc
        self.resultsTabelaFinal.loc[self.resultsTabelaFinal['Operation'] == 'Reservas de Lucros', 'Value'] = self.reservLucro

    
    def ReservaLegal(self):
        key = f'reservaLegal{self.data}'

        if key not in st.session_state:
            st.session_state[key] = 0.0

        st.session_state[key] = st.session_state[key]
        self.reservLegal = st.number_input('Digite o valor da Reserva Legal', key=key, value=st.session_state[key])
        self.resultsCalcJcp = pd.concat([self.resultsCalcJcp, pd.DataFrame([{"Operation": "Reserva legal", "Value": self.reservLegal}])], ignore_index=True)



    def OutrasReservasLucros(self):
        key = f'reservaOutras{self.data}'

        if key not in st.session_state:
            st.session_state[key] = 0.0
        
        st.session_state[key] = st.session_state[key]

        self.outrasResLuc = st.number_input('Digite o valor Outras reservas de lucros',key=key,value=st.session_state[key])

        self.resultsCalcJcp = pd.concat([self.resultsCalcJcp, pd.DataFrame([{"Operation": "Outras Reservas de Lucros", "Value": self.outrasResLuc}])], ignore_index=True)
    

    def ResultadoDoExercicio(self):
        key = f'ReusltadoDoExercico{self.data}'

        if key not in st.session_state:
            st.session_state[key] = 0.0
        
        st.session_state[key] = st.session_state[key]

        self.resultExercicio = st.number_input('Ajuste Resultado do Exercício',key=key,value=st.session_state[key])

        self.resultsCalcJcp = pd.concat([self.resultsCalcJcp, pd.DataFrame([{"Operation": "Resultado do Exercício", "Value": self.resultExercicio}])], ignore_index=True)

    def lucroPrejuAcumulado(self):
        key = f'LucroPrejuAc{self.data}'

        if key not in st.session_state:
            st.session_state[key] = 0.0
        
        st.session_state[key] = st.session_state[key]

        self.lucroPrejAcumu = st.number_input('Lucros/Prejuízos acumulados',key=key,value=st.session_state[key])

        self.resultsCalcJcp = pd.concat([self.resultsCalcJcp, pd.DataFrame([{"Operation": "Lucros/Prejuízos acumulados", "Value": self.lucroPrejAcumu}])], ignore_index=True)

    def ReservasLucros(self):
        self.reservLucro = self.reservLegal + self.outrasResLuc
        self.resultsCalcJcp = pd.concat([self.resultsCalcJcp, pd.DataFrame([{"Operation": "Reservas de Lucros", "Value": self.reservLucro}])], ignore_index=True)
    

    def acoesTesouraria(self):

        l100 = self.l100
        l100 = l100[(l100['Conta Referencial']=='2.03.04.01.12')&
            (l100['Data Inicial'].str.contains(self.data))&(
            l100['Período Apuração']=='A00 – Receita Bruta/Balanço de Suspensão e Redução Anual')]
        self.acosTesouraria = np.sum(l100['Vlr Saldo Final'].values)
        self.resultsCalcJcp = pd.concat([self.resultsCalcJcp, pd.DataFrame([{"Operation": "Ações em Tesouraria", "Value": self.acosTesouraria}])], ignore_index=True)

    def contPatrimonioNaoClass(self):

        l100 = self.l100
        l100 = l100[(l100['Conta Referencial']=='2.03.04.01.90')&
            (l100['Data Inicial'].str.contains(self.data))&(
            l100['Período Apuração']=='A00 – Receita Bruta/Balanço de Suspensão e Redução Anual')]
        self.contaPatriNClassifica = np.sum(l100['Vlr Saldo Final'].values)
        self.resultsCalcJcp = pd.concat([self.resultsCalcJcp, pd.DataFrame([{"Operation": "Contas do Patrimônio Líquido Não Classificadas ", "Value": self.contaPatriNClassifica}])], ignore_index=True)
    
    
    def PrejuizoPeriodo(self):

        key = f'PrejuAcumulado{self.data}'

        if key not in st.session_state:
            st.session_state[key] = 0.0
        
        st.session_state[key] = st.session_state[key]

        self.prejuizoPeirod = st.number_input('Digite o valor do Prejuízo do Período',key=key,value=st.session_state[key])

        self.resultsCalcJcp = pd.concat([self.resultsCalcJcp, pd.DataFrame([{"Operation": "Prejuízo do Período", "Value": self.prejuizoPeirod}])], ignore_index=True)
        
    
  
    def prejuizosAcumulados(self):

        lucroOuPrejuPeriodo = self.l300
        lucroOuPrejuPeriodo = lucroOuPrejuPeriodo[(lucroOuPrejuPeriodo['Descrição Conta Referencial']=='RESULTADO LÍQUIDO DO PERÍODO')&
            (lucroOuPrejuPeriodo['Data Inicial'].str.contains(self.data))&(
            lucroOuPrejuPeriodo['Período Apuração']=='A00 – Receita Bruta/Balanço de Suspensão e Redução Anual')]
        self.lucroOuPrejuPeriodo = np.sum(lucroOuPrejuPeriodo['Vlr Saldo Final'].values)
         

        l100 = self.l100
        l100 = l100[(l100['Conta Referencial']=='2.03.04.01.11')&
            (l100['Data Inicial'].str.contains(self.data))&(
            l100['Período Apuração']=='A00 – Receita Bruta/Balanço de Suspensão e Redução Anual')]
        self.contaPatriNClassifica = np.sum(l100['Vlr Saldo Final'].values)

        if (l100['D/C Saldo Final'] == 'C').any():
            self.prejuAcumulado = abs(self.contaPatriNClassifica)
        else:
            self.prejuAcumulado = abs(self.contaPatriNClassifica - self.lucroOuPrejuPeriodo)
        
        self.resultsCalcJcp = pd.concat([self.resultsCalcJcp, pd.DataFrame([{"Operation": "Prejuízos Acumulados", "Value": self.prejuAcumulado}])], ignore_index=True)
    
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
            

            self.resultsCalcJcp['Value'] = self.resultsCalcJcp['Value'].apply(lambda x: "{:,.2f}".format(x)).str.replace('.','_').str.replace(',','.').str.replace('_',',')
            st.dataframe(self.resultsCalcJcp)
            return self.resultsCalcJcp

    @functools.cache
    def runPipeFinalTable(self):

        self.lucrosAcumulados()
        self.lucroPeriodo()
        self.exclusoes()
        self.adicoes()
        self.lucroAntesCSLL()
        self.baseDeCalculo()
        self.compensacaoPrejuizo()   
        self.LucroLiquidoAntesIRPJ()
        self.baseCSLL()

        self.resultsTabelaFinal['Value'] = self.resultsTabelaFinal['Value'].apply(lambda x: "{:,.2f}".format(x)).str.replace('.','_').str.replace(',','.').str.replace('_',',')
        st.dataframe(self.resultsTabelaFinal)
        return self.resultsTabelaFinal

