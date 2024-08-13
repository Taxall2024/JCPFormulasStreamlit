import pandas as pd
import streamlit as st
import numpy as np
import openpyxl as op
import sys
import os
import base64
import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass

# Adicione o caminho do diretório onde o módulo 'LacsLalur' está localizado
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from LacsLalur.trimestralLacsLalur import LacsLalurCSLLTrimestral


st.set_page_config(layout="wide")
# background_image ="limpeza_dos_dados\\Untitleddesign.jpg"
# st.markdown(
#     f"""
#     <iframe src="data:image/jpg;base64,{base64.b64encode(open(background_image, 'rb').read()).decode(

#     )}" style="width:3000px;height:3500px;position: absolute;top:-3vh;right:-350px;opacity: 0.5;background-size: cover;background-position: center;"></iframe>
#     """,
#     unsafe_allow_html=True
# )

@st.cache_data(ttl='1d')
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



@dataclass
class trimestralFiltrandoDadosParaCalculo():
    _widget_counter = 0


    @st.cache_data(ttl='1d', show_spinner=False)
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

        self.resultadoJPC = pd.DataFrame(columns=["Operation", "Value"])
        self.resultadoLimiteDedu = pd.DataFrame(columns=["Operation", "Value"])
        self.resultadoEconomiaGerada = pd.DataFrame(columns=["Operation", "Value"])

        self.dataframe = fetch_tjlp_data()
  
        self.ano = ano
        self.mes_inicio = mes_inicio
        self.mes_fim = mes_fim
        self.trimestre = trimestre
        self.LacsLalurTrimestral = LacsLalurCSLLTrimestral(self.trimestre, self.ano, 1, 12,lacs_file, lalur_file, ecf670_file, ec630_file)

        # self.l100 = trimestralFiltrandoDadosParaCalculo.load_excel_file(r'C:\Users\lauro.loyola\Desktop\JCPCalculos\limpeza_dos_dados\DightBrasil\ECF - L030, L100 - Balanço Patrimonial - Lucro Real.xlsx')
        # self.l300 = trimestralFiltrandoDadosParaCalculo.load_excel_file(r'C:\Users\lauro.loyola\Desktop\JCPCalculos\limpeza_dos_dados\DightBrasil\ECF - L030, L300 - Demonstração do Resultado do Exercício - Lucro Real.xlsx')

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
            df.loc[(df['Data Final'].dt.month >= 1) & (df['Data Final'].dt.month <= 4), 'Trimestre'] = '1º Trimestre'
            df.loc[(df['Data Final'].dt.month > 4) & (df['Data Final'].dt.month < 7), 'Trimestre'] = '2º Trimestre'
            df.loc[(df['Data Final'].dt.month > 7) & (df['Data Final'].dt.month < 10), 'Trimestre'] = '3º Trimestre'
            df.loc[(df['Data Final'].dt.month >= 10) & (df['Data Final'].dt.month <= 12), 'Trimestre'] = '4º Trimestre'            


        self.resultsCalcJcp = pd.DataFrame(columns=["Operation", "Value"])
        self.resultsTabelaFinal = pd.DataFrame(columns=["Operation", "Value"])
         
        self.lucro_periodo_value = 0

    #-- Função que retorna o nome da empresa, deve ser substituida por uma função que busca o nome da empresa no banco de dados
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


    def get_input_value(self, label, key, default_value=0.0):
        if key not in st.session_state:
            st.session_state[key] = default_value
        return st.number_input(label, key=key, value=st.session_state[key])

    
    def set_date(self, data):
        self.data = data         

    
    
    def capitalSocial(self):
        l100 = self.l100
        l100 = l100[(l100['Descrição Conta Referencial']=='CAPITAL REALIZADO - DE RESIDENTE NO PAÍS')&
            (l100['Data Inicial'].dt.year == self.ano) &
            (l100['Data Inicial'].dt.month >= self.mes_inicio) &
            (l100['Data Inicial'].dt.month <= self.mes_fim)&
            (l100['Trimestre'] == self.trimestre)]
        self.capSocial = l100['Vlr Saldo Final'].sum()
        self.resultsCalcJcp = pd.concat([self.resultsCalcJcp, pd.DataFrame([{"Operation": "Capital Social", "Value": self.capSocial}])], ignore_index=True)



    
    def capitalIntegralizador(self):
    
        key = f'capitalIntregalizador{self.ano,self.mes_inicio,self.trimestre}'
        if key not in st.session_state:
            st.session_state[key] = 0.0
        st.session_state[key] = st.session_state[key]    
        
        self.capitalIntegra = st.number_input('Digite o valor do Capital Integralizador', key=key, value=st.session_state[key])
         
        self.resultsCalcJcp = pd.concat([self.resultsCalcJcp, pd.DataFrame([{"Operation": "Capital Integralizador", "Value": self.capitalIntegra}])], ignore_index=True)
    

    def ReservasDeCapital(self):

        key = f'reservasDeCapital{self.ano,self.mes_inicio,self.trimestre}'
        if key not in st.session_state:
            st.session_state[key] = 0.0
        st.session_state[key] = st.session_state[key]    
        
        self.reservaCapital = st.number_input('Digite o valor das Reservas de Capital', key=key, value=st.session_state[key])
         
        self.resultsCalcJcp = pd.concat([self.resultsCalcJcp, pd.DataFrame([{"Operation": "Reservas de Capital", "Value": self.reservaCapital}])], ignore_index=True)

            
    def ajustesAvalPatrimonial(self):
        key = f'ajustesPatrimonial{self.ano,self.mes_inicio,self.trimestre}'
        if key not in st.session_state:
            st.session_state[key] = 0.0
        st.session_state[key] = st.session_state[key]    
        
        self.ajusteAvaPatrimonial = st.number_input('Digite o valor dos Ajustes de Avaliação Patrimonial', key=key, value=st.session_state[key])
         
        self.resultsCalcJcp = pd.concat([self.resultsCalcJcp, pd.DataFrame([{"Operation": "Ajustes Avaliação Patrimonial", "Value": self.ajusteAvaPatrimonial}])], ignore_index=True)

                    
    def lucrosAcumulados(self):

        key = f'lucrosAcumulados{self.ano,self.mes_inicio,self.trimestre}'
        if key not in st.session_state:
            st.session_state[key] = 0.0
        st.session_state[key] = st.session_state[key]    
        
        self.lucroAcumulado = st.number_input('Digite o valor dos Lucros Acumulados', key=key, value=st.session_state[key])
         
        self.resultsCalcJcp = pd.concat([self.resultsCalcJcp, pd.DataFrame([{"Operation": "Lucros Acumulados", "Value": self.lucroAcumulado}])], ignore_index=True)
        self.resultsTabelaFinal = pd.concat([self.resultsTabelaFinal, pd.DataFrame([{"Operation": "Lucros Acumulados", "Value": self.lucroAcumulado}])], ignore_index=True)
      
    
    def ajustesExerAnteriores(self):

        key = f'ajustesExerAnteirores{self.ano,self.mes_inicio,self.trimestre}'
        if key not in st.session_state:
            st.session_state[key] = 0.0
        st.session_state[key] = st.session_state[key]    
        
        self.ajustExercAnt = st.number_input('Ajustes de Exercícios Anteriores', key=key, value=st.session_state[key])
         
        self.resultsCalcJcp = pd.concat([self.resultsCalcJcp, pd.DataFrame([{"Operation": "Ajustes Exercícios Anteriores", "Value": self.ajustExercAnt}])], ignore_index=True)

    
    def lucroPeriodo(self):

        key = f'lucroPeriodo{self.ano,self.mes_inicio,self.trimestre}'
        if key not in st.session_state:
            st.session_state[key] = 0.0
        st.session_state[key] = st.session_state[key]    
        
        self.lucro_periodo_value = st.number_input('Digite o valor dos Lucros do Período', key=key, value=st.session_state[key])  

        self.resultsCalcJcp = pd.concat([self.resultsCalcJcp, pd.DataFrame([{"Operation": "Lucro do Período", "Value": self.lucro_periodo_value}])], ignore_index=True)
        self.resultsTabelaFinal = pd.concat([self.resultsTabelaFinal, pd.DataFrame([{"Operation": "Lucro do Período", "Value": self.lucro_periodo_value}])], ignore_index=True)
    
    def TotalFinsCalcJSPC(self):

        self.totalJSPC =  sum((self.capSocial,self.reservaCapital,self.lucroAcumulado,self.reservLucro,self.contaPatriNClassifica,self.prejuizoPeirod))
        self.resultsCalcJcp = pd.concat([self.resultsCalcJcp, pd.DataFrame([{"Operation": "Total Fins Calc JSPC", "Value": self.totalJSPC}])], ignore_index=True)
    


    def update_totalfinsparaJPC(self):
        self.totalJSPC = self.capSocial + self.reservaCapital + self.lucroAcumulado + self.reservLucro
        self.resultsCalcJcp = pd.concat([self.resultsCalcJcp, pd.DataFrame([{"Operation": "Total Fins Calc JSPC", "Value": self.totalJSPC}])], ignore_index=True)
    
    def update_reservas(self):
        self.reservLucro = self.reservLegal + self.reservEstatuaria + self.resContingencia + self.reserExp + self.outrasResLuc
        self.resultsTabelaFinal.loc[self.resultsTabelaFinal['Operation'] == 'Reservas de Lucros', 'Value'] = self.reservLucro

    def ReservaLegal(self):
        key = f'reservaLegal{self.ano,self.mes_inicio,self.trimestre}'

        if key not in st.session_state:
            st.session_state[key] = 0.0

        st.session_state[key] = st.session_state[key]
        self.reservLegal = st.number_input('Digite o valor da Reserva Legal', key=key, value=st.session_state[key])
         
        self.resultsCalcJcp = pd.concat([self.resultsCalcJcp, pd.DataFrame([{"Operation": "Reserva legal", "Value": self.reservLegal}])], ignore_index=True)



    def ReservaEstatutária(self):
        key = f'reservaEsta{self.ano,self.mes_inicio,self.trimestre}'

        if key not in st.session_state:
            st.session_state[key] = 0.0

        st.session_state[key] = st.session_state[key]

        self.reservEstatuaria =  st.number_input('Digite o valor da Reserva Estatuaria',key=key,value=st.session_state[key])
         
        self.resultsCalcJcp = pd.concat([self.resultsCalcJcp, pd.DataFrame([{"Operation": "Reserva Estatutária", "Value": self.reservEstatuaria}])], ignore_index=True)
    

    def ReservaContingencias(self):
        key = f'reservaCont{self.ano,self.mes_inicio,self.trimestre}'  

        if key not in st.session_state:
            st.session_state[key] = 0.0

        st.session_state[key] = st.session_state[key]

        self.resContingencia =  st.number_input('Digite o valor da Reserva Reserva de contingências',key=key,value=st.session_state[key])
                 
        self.resultsCalcJcp = pd.concat([self.resultsCalcJcp, pd.DataFrame([{"Operation": "Reserva para Contingências", "Value": self.resContingencia}])], ignore_index=True)
    

    def ReservaExpansao(self):
        key = f'reservaExpans{self.ano,self.mes_inicio,self.trimestre}'

        if key not in st.session_state:
            st.session_state[key] = 0.0

        st.session_state[key] = st.session_state[key]
        self.reserExp =  st.number_input('Digite o valor da Reserva de Expansão',key=key,value=st.session_state[key])
         
        self.resultsCalcJcp = pd.concat([self.resultsCalcJcp, pd.DataFrame([{"Operation":"Reserva de Lucros para Expansão", "Value": self.reserExp}])], ignore_index=True)
    

    def OutrasReservasLucros(self):
        key = f'reservaOutras{self.ano,self.mes_inicio,self.trimestre}'

        if key not in st.session_state:
            st.session_state[key] = 0.0
        
        st.session_state[key] = st.session_state[key]

        self.outrasResLuc = st.number_input('Digite o valor Outras reservas de lucros',key=key,value=st.session_state[key])
         

        self.resultsCalcJcp = pd.concat([self.resultsCalcJcp, pd.DataFrame([{"Operation": "Outras Reservas de Lucros", "Value": self.outrasResLuc}])], ignore_index=True)

    
    def ReservasLucros(self):
        self.reservLucro = self.reservLegal + self.reservEstatuaria + self.resContingencia + self.reserExp + self.outrasResLuc
        self.resultsCalcJcp = pd.concat([self.resultsCalcJcp, pd.DataFrame([{"Operation": "Reservas de Lucros", "Value": self.reservLucro}])], ignore_index=True)
    
    
    def acoesTesouraria(self):

        l100 = self.l100
        l100 = l100[(l100['Conta Referencial']=='2.03.04.01.12')&
            (l100['Data Inicial'].dt.year == self.ano) &
            (l100['Data Inicial'].dt.month >= self.mes_inicio) &
            (l100['Data Inicial'].dt.month <= self.mes_fim)&(
            l100['Período Apuração']=='A00 – Receita Bruta/Balanço de Suspensão e Redução Anual')]
        self.acosTesouraria = l100['Vlr Saldo Final'].sum()
        self.resultsCalcJcp = pd.concat([self.resultsCalcJcp, pd.DataFrame([{"Operation": "Ações em Tesouraria", "Value": self.acosTesouraria}])], ignore_index=True)
    
    
    def contPatrimonioNaoClass(self):

        l100 = self.l100
        l100 = l100[(l100['Conta Referencial']=='2.03.04.01.90')&
            (l100['Data Inicial'].dt.year == self.ano) &
            (l100['Data Inicial'].dt.month >= self.mes_inicio) &
            (l100['Data Inicial'].dt.month <= self.mes_fim)&(
            l100['Período Apuração']=='A00 – Receita Bruta/Balanço de Suspensão e Redução Anual')]
        self.contaPatriNClassifica = l100['Vlr Saldo Final'].sum()
        self.resultsCalcJcp = pd.concat([self.resultsCalcJcp, pd.DataFrame([{"Operation": "Contas do Patrimônio Líquido Não Classificadas ", "Value": self.contaPatriNClassifica}])], ignore_index=True)
    
    #@staticmethod
    def PrejuizoPeriodo(self):

        key = f'PrejuAcumulado{self.ano,self.mes_inicio,self.trimestre}'   

        if key not in st.session_state:
            st.session_state[key] = 0.0
        
        st.session_state[key] = st.session_state[key]

        self.prejuizoPeirod = st.number_input('Digite o valor do Prejuízo do Período',key=key,value=st.session_state[key]) * -1
         
        self.resultsCalcJcp = pd.concat([self.resultsCalcJcp, pd.DataFrame([{"Operation": "Prejuízo do Período", "Value": self.prejuizoPeirod}])], ignore_index=True)
        
    
        
    def prejuizosAcumulados(self):

        l100 = self.l100
        l100 = l100[(l100['Conta Referencial']=='2.03.04.01.11')&
            (l100['Data Inicial'].dt.year == self.ano) &
            (l100['Data Inicial'].dt.month >= self.mes_inicio) &
            (l100['Data Inicial'].dt.month <= self.mes_fim)&(
            l100['Período Apuração']=='A00 – Receita Bruta/Balanço de Suspensão e Redução Anual')]
        self.contaPatriNClassifica = l100['Vlr Saldo Final'].sum() * -1
        self.resultsCalcJcp = pd.concat([self.resultsCalcJcp, pd.DataFrame([{"Operation": "Prejuízos Acumulados", "Value": self.contaPatriNClassifica}])], ignore_index=True)
    
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

        self.valorJPC = round(self.totalJSPC * (1.60 / 100), 2)
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
        self.reducaoIRPJCSLL = self.valorJPC * 0.34
        self.economia = self.reducaoIRPJCSLL - self.darf

        results = [
                {"Operation": "REDUÇÃO NO IRPJ/CSLL - 34%", "Value": self.reducaoIRPJCSLL},
                {"Operation": "Economia", "Value": self.economia},
            ]
        
        self.resultadoEconomiaGerada = pd.concat([self.resultadoEconomiaGerada, pd.DataFrame(results)], ignore_index=True)

   
    
    def runPipe(self):
        with st.expander("Adicionar valores :"):
            self.nomeDasEmpresas()
            self.capitalSocial()
            self.capitalIntegralizador()
            self.ReservasDeCapital()
            self.ajustesAvalPatrimonial()

            self.ReservaLegal()
            self.ReservaEstatutária()
            self.ReservaContingencias()
            self.ReservaExpansao()
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

            #-- Metódos que fazer calculos dos valores finais do JCP

            self.calculandoJPC(str(self.ano), self.trimestre)
            self.limiteDedutibilidade()
            self.tabelaEconomia()
        
        
        self.resultsCalcJcp['Value'] = self.resultsCalcJcp['Value'].apply(lambda x: "{:,.2f}".format(float(x)) if isinstance(x, (int, float)) or x.replace(',', '').replace('.', '').isdigit() else x)

        self.dataframeFinal = pd.DataFrame(self.resultsCalcJcp)
        self.dataframJCP = pd.DataFrame(self.resultadoJPC)

    
    def runPipeFinalTable(self):

        self.lucrosAcumulados()
        self.lucroPeriodo()
        self.LacsLalurTrimestral.exclusoes()
        self.LacsLalurTrimestral.calcAdicoes()
        self.LacsLalurTrimestral.lucroAntesCSLL()
        self.LacsLalurTrimestral.baseDeCalculo()
        self.LacsLalurTrimestral.compensacaoPrejuizo()   
        self.LacsLalurTrimestral.LucroLiquidoAntesIRPJ()
        self.LacsLalurTrimestral.baseCSLL()

        self.resultsTabelaFinal['Value'] = self.resultsTabelaFinal['Value'].apply(lambda x: "{:,.2f}".format(x))
        st.dataframe(self.resultsTabelaFinal)
    




# if __name__=='__main__':

    # uploaded_file_l100 = st.sidebar.file_uploader("Upload L100 Excel File", type="xlsx")
    # uploaded_file_l300 = st.sidebar.file_uploader("Upload L300 Excel File", type="xlsx")
    # uploaded_file_lacs = st.sidebar.file_uploader("Upload Lacs Excel File", type="xlsx")
    # uploaded_file_lalur = st.sidebar.file_uploader("Upload Lalur Excel File", type="xlsx")
    # uploaded_file_ecf670 = st.sidebar.file_uploader("Upload ECF 670 Excel File", type="xlsx")
    # uploaded_file_ec630 = st.sidebar.file_uploader("Upload ECF 630 Excel File", type="xlsx")


    # if uploaded_file_l100 and uploaded_file_l300 and uploaded_file_lacs and uploaded_file_lalur and uploaded_file_ecf670 and uploaded_file_ec630:
    #     with st.form(key='form1'):
    #         submitButton = st.form_submit_button('Processar')
            
    #         if submitButton:

    #             colunas = st.columns(4)
    #             trimestres = ['1º Trimestre', '2º Trimestre', '3º Trimestre', '4º Trimestre']
    #             economia_gerada_por_trimestre = []
    #             for ano in range(2019, 2024):
    #                 year_dfsLacs = []
    #                 resultadoJCP = []
    #                 resultadoDedu = []
    #                 economiaGerada = []
    #                 for col, trimestre in zip(colunas, trimestres):
    #                     with col:

    #                         lacs = trimestralFiltrandoDadosParaCalculo(
    #                                             trimestre=trimestre,
    #                                             ano=ano,
    #                                             mes_inicio=1,
    #                                             mes_fim=12,
    #                                             l100_file=uploaded_file_l100,
    #                                             l300_file=uploaded_file_l300,
    #                                             lacs_file=uploaded_file_lacs,
    #                                             lalur_file=uploaded_file_lalur,
    #                                             ecf670_file=uploaded_file_ecf670,
    #                                             ec630_file=uploaded_file_ec630)

    #                         st.subheader(f'{ano}    {trimestre}')
    #                         lacs.runPipe()
                            
    #                         df = lacs.dataframeFinal
    #                         df.columns = [f"{col} {trimestre}" for col in df.columns] 
    #                         year_dfsLacs.append(df)

    #                         df = lacs.resultadoJPC
    #                         df.columns = [f"{col} {trimestre}" for col in df.columns] 
    #                         resultadoJCP.append(df)

    #                         df = lacs.resultadoLimiteDedu
    #                         df.columns = [f"{col} {trimestre}" for col in df.columns] 
    #                         resultadoDedu.append(df)
                            
    #                         df = lacs.resultadoEconomiaGerada
    #                         df.columns = [f"{col} {trimestre}" for col in df.columns] 
    #                         economiaGerada.append(df) 

    #                         economia_gerada_por_trimestre.append(lacs.economia)

                            



    #                 dfCalculos = pd.concat(year_dfsLacs, axis=1)
    #                 tabelaJCP = pd.concat(resultadoJCP, axis=1)
    #                 limiteDedutibili = pd.concat(resultadoDedu, axis=1)
    #                 economiaGerada = pd.concat(economiaGerada, axis=1)
                    

    #                 st.subheader(f"Resultados Anuais - {ano}")
    #                 st.dataframe(dfCalculos)
    #                 st.dataframe(tabelaJCP)
    #                 st.dataframe(limiteDedutibili)
    #                 st.dataframe(economiaGerada)


