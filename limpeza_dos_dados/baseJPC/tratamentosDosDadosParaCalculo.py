import pandas as pd
import streamlit as st
import numpy as np
import openpyxl as op
import functools


from LacsLalur.lacsLalurAntesInoTributarias import LacsLalurCSLL




class FiltrandoDadosParaCalculo(LacsLalurCSLL):
    _widget_counter = 0

    @staticmethod
    @st.cache_data(ttl='1d', show_spinner=False)
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
    
    def nomeDasEmpresas(self):

        l100 = self.l100
        self.nomeEmpresa = ''        
        if l100['CNPJ'].iloc[0] == '82513490000194':
            self.nomeEmpresa = 'PROFISER SERVIÇOS PROFISSIONAIS LTDA'
        elif l100['CNPJ'].iloc[0] == '10332516000197':    
            self.nomeEmpresa = 'ORBENK TERCEIRIZAÇÃO E SERVIÇOS LTDA'
        elif l100['CNPJ'].iloc[0] == '04048628000118':
            self.nomeEmpresa = 'INVIOLAVEL SEGURANÇA ELETRONICA LTDA'
        else:
            self.nomeEmpresa = 'Empresa não encontrada'             



    
    def set_date(self, data):
        self.data = data         

    
 
    def capitalSocial(self):
        l100 = self.l100
        l100 = l100[(l100['Período Apuração']=='A00 – Receita Bruta/Balanço de Suspensão e Redução Anual')&(
            l100['Descrição Conta Referencial']=='Capital Subscrito de Domiciliados e Residentes no País')&
            (l100['Data Inicial'].str.contains(self.data))]
        self.capSocial = l100['Vlr Saldo Final'].sum()

        key = f'capitalSoc{self.data}'

        if key not in st.session_state:
            st.session_state[key] = self.capSocial
        
        st.session_state[key] = st.session_state[key]

        self.capSocial = st.number_input('Ajuste Capital Social',key=key,value=st.session_state[key])

        self.resultsCalcJcp = pd.concat([self.resultsCalcJcp, pd.DataFrame([{"Operation": "Capital Social", "Value": self.capSocial}])], ignore_index=True)


 
    def capitalIntegralizador(self):
        l100 = self.l100
        l100 = l100[(l100['Conta Referencial']=='2.03.01.01.21')&(
            l100['Conta Referencial']=='2.03.01.02.10')&
            (l100['Data Inicial'].str.contains(self.data))]
        self.capitalIntegra = l100['Vlr Saldo Final'].sum()
        self.resultsCalcJcp = pd.concat([self.resultsCalcJcp, pd.DataFrame([{"Operation": "Capital Integralizador", "Value": self.capitalIntegra}])], ignore_index=True)
    
    
    def ReservasDeCapital(self):
        l100 = self.l100
        l100 = l100[(l100['Conta Referencial']=='2.03.02.01.99')&
            (l100['Data Inicial'].str.contains(self.data))]
        self.reservaCapital = l100['Vlr Saldo Final'].sum()
        
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
        self.ajusteAvaPatrimonial = l100['Vlr Saldo Final'].sum()

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
        
        self.lucroAcumulado = np.where(l100['Vlr Saldo Final'].sum()-lucroperio<0,0,l100['Vlr Saldo Final'].sum()-lucroperio)

        self.resultsCalcJcp = pd.concat([self.resultsCalcJcp, pd.DataFrame([{"Operation": "Lucros Acumulados", "Value": self.lucroAcumulado}])], ignore_index=True)
        self.resultsTabelaFinal = pd.concat([self.resultsTabelaFinal, pd.DataFrame([{"Operation": "Lucros Acumulados", "Value": self.lucroAcumulado}])], ignore_index=True)
      
    
    def ajustesExerAnteriores(self):
        l100 = self.l100
        l100 = l100[(l100['Conta Referencial']=='2.03.04.01.10')&
            (l100['Data Inicial'].str.contains(self.data))&(
            l100['Período Apuração']=='A00 – Receita Bruta/Balanço de Suspensão e Redução Anual')]
        self.ajustExercAnt = l100['Vlr Saldo Final'].sum()

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
        self.lucro_periodo_value = l100['Vlr Saldo Final'].sum()
        self.resultsCalcJcp = pd.concat([self.resultsCalcJcp, pd.DataFrame([{"Operation": "Lucro do Período", "Value": self.lucro_periodo_value}])], ignore_index=True)
        self.resultsTabelaFinal = pd.concat([self.resultsTabelaFinal, pd.DataFrame([{"Operation": "Lucro do Período", "Value": self.lucro_periodo_value}])], ignore_index=True)


    def TotalFinsCalcJSPC(self):

        self.totalJSPC =  sum((self.capSocial,self.reservaCapital,self.lucroAcumulado,self.reservLucro,
                               self.contaPatriNClassifica,self.prejuizoPeirod,self.ajustExercAnt,
                               self.resultExercicio,self.lucroPrejAcumu))
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
        self.acosTesouraria = l100['Vlr Saldo Final'].sum()
        self.resultsCalcJcp = pd.concat([self.resultsCalcJcp, pd.DataFrame([{"Operation": "Ações em Tesouraria", "Value": self.acosTesouraria}])], ignore_index=True)

    def contPatrimonioNaoClass(self):

        l100 = self.l100
        l100 = l100[(l100['Conta Referencial']=='2.03.04.01.90')&
            (l100['Data Inicial'].str.contains(self.data))&(
            l100['Período Apuração']=='A00 – Receita Bruta/Balanço de Suspensão e Redução Anual')]
        self.contaPatriNClassifica = l100['Vlr Saldo Final'].sum()
        self.resultsCalcJcp = pd.concat([self.resultsCalcJcp, pd.DataFrame([{"Operation": "Contas do Patrimônio Líquido Não Classificadas ", "Value": self.contaPatriNClassifica}])], ignore_index=True)
    
    
    def PrejuizoPeriodo(self):

        key = f'PrejuAcumulado{self.data}'

        if key not in st.session_state:
            st.session_state[key] = 0.0
        
        st.session_state[key] = st.session_state[key]

        self.prejuizoPeirod = st.number_input('Digite o valor do Prejuízo do Período',key=key,value=st.session_state[key]) * -1

        self.resultsCalcJcp = pd.concat([self.resultsCalcJcp, pd.DataFrame([{"Operation": "Prejuízo do Período", "Value": self.prejuizoPeirod}])], ignore_index=True)
        
    
  
    def prejuizosAcumulados(self):

        l100 = self.l100
        l100 = l100[(l100['Conta Referencial']=='2.03.04.01.11')&
            (l100['Data Inicial'].str.contains(self.data))&(
            l100['Período Apuração']=='A00 – Receita Bruta/Balanço de Suspensão e Redução Anual')]
        self.contaPatriNClassifica = l100['Vlr Saldo Final'].sum() * -1
        self.resultsCalcJcp = pd.concat([self.resultsCalcJcp, pd.DataFrame([{"Operation": "Prejuízos Acumulados", "Value": self.contaPatriNClassifica}])], ignore_index=True)
    

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

# if __name__=='__main__':

#     jcp = FiltrandoDadosParaCalculo() 

#     jcp.runPipeFinalTable()
#     #jcp.runPipeFinalTabelLacsLalur()
#     st.subheader('Calculo JCP')
#     jcp.runPipe()
#     st.subheader('Lacs e Lalur ')
#     jcp.runPipeLacsLalurIRPJ()
#     jcp.runPipeLacsLalurCSLL()