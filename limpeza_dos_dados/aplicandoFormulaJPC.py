import pandas as pd
import streamlit as st
import numpy as np
from bs4 import BeautifulSoup
import xlsxwriter
from xlsxwriter import Workbook

from baseJPC.tratamentosDosDadosParaCalculo import FiltrandoDadosParaCalculo
from baseJPC.trimestralTramentoECalculos import trimestralFiltrandoDadosParaCalculo
from LacsLalur.trimestralLacsLalur import LacsLalurCSLLTrimestral

import requests
import functools
import time
import base64
import io
import psutil
import pstats




start_time = time.time()
st.set_page_config(layout="wide")
background_image ="Untitleddesign.jpg"
st.markdown(
     f"""
     <iframe src="data:image/jpg;base64,{base64.b64encode(open(background_image, 'rb').read()).decode(

    )}" style="width:3000px;height:6000px;position: absolute;top:-3vh;right:-350px;opacity: 0.5;background-size: cover;background-position: center;"></iframe>
     """,
     unsafe_allow_html=True )

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

        self.dataframe = fetch_tjlp_data()
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
            st.dataframe(self.resultadoJPC, use_container_width=True)
        else:
            st.error("Data not found in the DataFrame")

    # @timing
    # def nomeDasEmpresas(self, l100_file):
    #     l100 = pd.read_excel(l100_file)
    #     nomeEmpresa = ''        
    #     if l100['CNPJ'].iloc[0] == 79283065000141:
    #         nomeEmpresa = 'ORBENK ADMNISTRAÇÃO E SERVIÇOS LTDA'
    #     elif l100['CNPJ'].iloc[0] == 14576552000157:    
    #         nomeEmpresa = 'ORBENK SERVIÇOS DE SEGURANÇA LTDA'
    #     elif l100['CNPJ'].iloc[0] == 10332516000197:
    #         nomeEmpresa = 'ORBENK TERCEIRIZAÇÃO E SERVIÇOS LTDA'
    #     elif l100['CNPJ'].iloc[0] == 82513490000194:
    #         nomeEmpresa = 'PROFISER SERVIÇOS PROFISSIONAIS LTDA'
    #     elif l100['CNPJ'].iloc[0] == 3750757000190:
    #         nomeEmpresa = 'SEPAT MULTI SERVICE LTDA'                          
    #     else:
    #         nomeEmpresa = 'Empresa não encontrada'
    #     return nomeEmpresa
                    
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
    
        
        
if __name__ == "__main__":
    anualOuTrimestral = st.sidebar.selectbox("Anual ou Trimestral", ["Ano", 'Trimestre'])
    barra = st.radio("Menu", ["Calculo JCP", "Lacs e Lalur"]) 
    with st.form('form1',border=False):
        if st.form_submit_button('Gerar Dados'):           
  
            try:
                
                ''
                #empresa_nome_placeholder = st.header("Empresa não selecionada")
            except:
                st.write('Clique em "Gerar Dados')    


        col1, col2, col3, col4, col5 = st.columns(5)

        uploaded_file_l100 = st.sidebar.file_uploader("Upload L100 Excel File", type="xlsx")
        uploaded_file_l300 = st.sidebar.file_uploader("Upload L300 Excel File", type="xlsx")
        uploaded_file_lacs = st.sidebar.file_uploader("Upload Lacs Excel File", type="xlsx")
        uploaded_file_lalur = st.sidebar.file_uploader("Upload Lalur Excel File", type="xlsx")
        uploaded_file_ecf670 = st.sidebar.file_uploader("Upload ECF 670 Excel File", type="xlsx")
        uploaded_file_ec630 = st.sidebar.file_uploader("Upload ECF 630 Excel File", type="xlsx")
        
        if uploaded_file_l100 and uploaded_file_l300 and uploaded_file_lacs and uploaded_file_lalur and uploaded_file_ecf670 and uploaded_file_ec630:
            if anualOuTrimestral == 'Ano':          
                filtrando_dados = FiltrandoDadosParaCalculo(
                    data=None,
                    lacs_file=uploaded_file_lacs,
                    lalur_file=uploaded_file_lalur,
                    ecf670_file=uploaded_file_ecf670,
                    ec630_file=uploaded_file_ec630,
                    l100_file=uploaded_file_l100,
                    l300_file=uploaded_file_l300
                )
                try:
                    calculos2019 = Calculo(data=str('2019'),
                                            lacs_file=uploaded_file_lacs,
                                            lalur_file=uploaded_file_lalur,
                                            ecf670_file=uploaded_file_ecf670,
                                            ec630_file=uploaded_file_ec630,
                                            l100_file=uploaded_file_l100,
                                            l300_file=uploaded_file_l300) 
                    calculos2020 = Calculo(data=str('2020'),
                                            lacs_file=uploaded_file_lacs,
                                            lalur_file=uploaded_file_lalur,
                                            ecf670_file=uploaded_file_ecf670,
                                            ec630_file=uploaded_file_ec630,
                                            l100_file=uploaded_file_l100,
                                            l300_file=uploaded_file_l300) 
                    calculos2021 = Calculo(data=str('2021'),
                                            lacs_file=uploaded_file_lacs,
                                            lalur_file=uploaded_file_lalur,
                                            ecf670_file=uploaded_file_ecf670,
                                            ec630_file=uploaded_file_ec630,
                                            l100_file=uploaded_file_l100,
                                            l300_file=uploaded_file_l300)
                    calculos2022 =  Calculo(data=str('2022'),
                                            lacs_file=uploaded_file_lacs,
                                            lalur_file=uploaded_file_lalur,
                                            ecf670_file=uploaded_file_ecf670,
                                            ec630_file=uploaded_file_ec630,
                                            l100_file=uploaded_file_l100,
                                            l300_file=uploaded_file_l300)                                             
                    calculos2023 =  Calculo(data=str('2023'),
                                        lacs_file=uploaded_file_lacs,
                                        lalur_file=uploaded_file_lalur,
                                        ecf670_file=uploaded_file_ecf670,
                                        ec630_file=uploaded_file_ec630,
                                        l100_file=uploaded_file_l100,
                                        l300_file=uploaded_file_l300) 
                
                except:
                    pass 
                #'''Execução do metódo que atribui os nomes da empresa no topo da tela, porem estava cobrando muita memoria e demorando muito para executar,
                # ate que alteções sejam concluidas e melhoras no tempo de execução'''     
                                 
                # empresa_nome = calculos2019.nomeDasEmpresas(uploaded_file_l100)
                # try:
                #     empresa_nome_placeholder.header(empresa_nome)    
                # except:
                #     pas
                                                    
                try:
                    if barra == "Calculo JCP":

                            
                            economiaPorAno = []
                            dataFrameParaExportar1 = []
                            dataFrameParaExportar2 = []
                            dataFrameParaExportar3 = []

                            df = pd.DataFrame(columns=['Operation','Value'])
                            

                            with col1:
                                st.write('')
                                st.write('')
                                st.write('')
                                st.write('')
                                st.subheader('2019')
                                calculosIniciais_2019 = calculos2019.runPipe()
                                tabelaFinal_2019 = calculos2019.runPipeFinalTable()
                                resultadoTotal_2019 = calculos2019.pipeCalculo('2019')
                                economiaPorAno.append(resultadoTotal_2019)
                                dataFrameParaExportar1.append(calculosIniciais_2019)
                                dataFrameParaExportar2.append(tabelaFinal_2019)
                                dataFrameParaExportar3.append(resultadoTotal_2019)

                            with col2:
                                st.write('')
                                st.write('')
                                st.write('')
                                st.write('')
                                st.subheader('2020')
                                calculosIniciais_2020 = calculos2020.runPipe()
                                tabelaFinal_2020 = calculos2020.runPipeFinalTable()
                                resultadoTotal_2020 = calculos2020.pipeCalculo('2020')
                                economiaPorAno.append(resultadoTotal_2020)
                                dataFrameParaExportar1.append(calculosIniciais_2020)
                                dataFrameParaExportar2.append(tabelaFinal_2020)
                                dataFrameParaExportar3.append(resultadoTotal_2020)

                            with col3:
                                st.write('')
                                st.write('')
                                st.write('')
                                st.write('')
                                st.subheader('2021')
                                calculosIniciais_2021 = calculos2021.runPipe()
                                tabelaFinal_2021 = calculos2021.runPipeFinalTable()
                                resultadoTotal_2021 = calculos2021.pipeCalculo('2021')
                                economiaPorAno.append(resultadoTotal_2021)
                                dataFrameParaExportar1.append(calculosIniciais_2021)
                                dataFrameParaExportar2.append(tabelaFinal_2021)
                                dataFrameParaExportar3.append(resultadoTotal_2021)

                            with col4:
                                st.write('')
                                st.write('')
                                st.write('')
                                st.write('')
                                st.subheader('2022')
                                calculosIniciais_2022 = calculos2022.runPipe()
                                tabelaFinal_2022 = calculos2022.runPipeFinalTable()
                                resultadoTotal_2022 = calculos2022.pipeCalculo('2022')
                                economiaPorAno.append(resultadoTotal_2022)
                                dataFrameParaExportar1.append(calculosIniciais_2022)
                                dataFrameParaExportar2.append(tabelaFinal_2022)
                                dataFrameParaExportar3.append(resultadoTotal_2022)

                            with col5:
                                st.write('')
                                st.write('')
                                st.write('')
                                st.write('')
                                st.subheader('2023')
                                calculosIniciais_2023 = calculos2023.runPipe()
                                tabelaFinal_2023 = calculos2023.runPipeFinalTable()
                                resultadoTotal_2023 = calculos2023.pipeCalculo('2023')
                                economiaPorAno.append(resultadoTotal_2023)
                                dataFrameParaExportar1.append(calculosIniciais_2023)
                                dataFrameParaExportar2.append(tabelaFinal_2023)
                                dataFrameParaExportar3.append(resultadoTotal_2023)

                            dfmetricaGeral = pd.concat(economiaPorAno).reset_index(drop='index')
                            dfmetricaGeral = dfmetricaGeral.transpose().iloc[:,[1,3,5,7,9]]
                            dfmetricaGeral['Agregado do período'] = dfmetricaGeral.apply(lambda row: row.sum(), axis=1)

                            arquivoParaExportar = pd.concat([calculosIniciais_2019.add_suffix('_2019'), calculosIniciais_2020.add_suffix('_2020'), 
                                                            calculosIniciais_2021.add_suffix('_2021'), calculosIniciais_2022.add_suffix('_2022'), 
                                                            calculosIniciais_2023.add_suffix('_2023')], axis=1)

                            arquivoParaExportar2 = pd.concat([tabelaFinal_2019.add_suffix('_2019'), tabelaFinal_2020.add_suffix('_2020'), 
                                                            tabelaFinal_2021.add_suffix('_2021'), tabelaFinal_2022.add_suffix('_2022'), 
                                                            tabelaFinal_2023.add_suffix('_2023')], axis=1)

                            arquivoParaExportar3 = pd.concat([resultadoTotal_2019.add_suffix('_2019'), resultadoTotal_2020.add_suffix('_2020'), 
                                                            resultadoTotal_2021.add_suffix('_2021'), resultadoTotal_2021.add_suffix('_2022'),
                                                            resultadoTotal_2021.add_suffix('_2023')])
                            
                            arquivoFInalParaExpostacao = pd.concat([arquivoParaExportar,arquivoParaExportar2,arquivoParaExportar3],axis=0)

                            st.write('')
                            st.write('')
                            st.write('')
                            st.metric("Total da Economia Gerada", f"R$ {dfmetricaGeral.iloc[1,-1]:,.2f}".replace(',','_').replace('.',',').replace('_','.'))

                    if barra == "Lacs e Lalur":

                        dataFrameParaExportarCSLL = []
                        dataFrameParaExportarIRPJJ = []
                        dfLacsLalur = pd.DataFrame(columns=['Operation','Value'])

                        with col1:

                            st.write('')
                            st.write('')
                            st.subheader('2019')
                            resultadoTotal_2019 = calculos2019.runPipeLacsLalurCSLL()
                            resultadoTotal_2019IR = calculos2019.runPipeLacsLalurIRPJ()
                            dataFrameParaExportarCSLL.append(resultadoTotal_2019)
                            dataFrameParaExportarIRPJJ.append(resultadoTotal_2019IR)

                        with col2:
                            st.write('')
                            st.write('')
                            st.subheader('2020')
                            resultadoTotal_2020 = calculos2020.runPipeLacsLalurCSLL()
                            resultadoTotal_2020IR = calculos2020.runPipeLacsLalurIRPJ()
                            dataFrameParaExportarCSLL.append(resultadoTotal_2020)
                            dataFrameParaExportarIRPJJ.append(resultadoTotal_2020IR)


                        with col3:
                            st.write('')
                            st.write('')
                            st.subheader('2021')
                            resultadoTotal_2021 = calculos2021.runPipeLacsLalurCSLL()
                            resultadoTotal_2021IR = calculos2021.runPipeLacsLalurIRPJ()
                            dataFrameParaExportarCSLL.append(resultadoTotal_2021)
                            dataFrameParaExportarIRPJJ.append(resultadoTotal_2021IR)

                        with col4:
                            st.write('')
                            st.write('')
                            st.subheader('2022')
                            resultadoTotal_2022 = calculos2022.runPipeLacsLalurCSLL()
                            resultadoTotal_2022IR = calculos2022.runPipeLacsLalurIRPJ()
                            dataFrameParaExportarCSLL.append(resultadoTotal_2022)
                            dataFrameParaExportarIRPJJ.append(resultadoTotal_2022IR)

                        with col5:
                            st.write('')
                            st.write('')
                            st.subheader('2023')
                            resultadoTotal_2023 = calculos2023.runPipeLacsLalurCSLL()
                            resultadoTotal_2023IR = calculos2023.runPipeLacsLalurIRPJ()
                            dataFrameParaExportarCSLL.append(resultadoTotal_2023)
                            dataFrameParaExportarIRPJJ.append(resultadoTotal_2023IR)
                    try:

                        arquivoParaExportarCSLL = pd.concat([resultadoTotal_2019.add_suffix('_2019'), resultadoTotal_2020.add_suffix('_2020'), 
                                                        resultadoTotal_2021.add_suffix('_2021'), resultadoTotal_2022.add_suffix('_2022'), 
                                                        resultadoTotal_2023.add_suffix('_2023')], axis=1)
                        
                        arquivoParaExportarIRPJ = pd.concat([resultadoTotal_2019IR.add_suffix('_2019'), resultadoTotal_2020IR.add_suffix('_2020'), 
                                                        resultadoTotal_2021IR.add_suffix('_2021'), resultadoTotal_2022IR.add_suffix('_2022'), 
                                                        resultadoTotal_2023IR.add_suffix('_2023')], axis=1)
                        
                        exportarLacsLalur = pd.concat([arquivoParaExportarCSLL,arquivoParaExportarIRPJ])

                    except:
                        pass

                except Exception as e:
                    #st.warning(f'Error :{str(e)}')
                    st.warning('Clique em "Gerar Dados"')
                    #pass
            if anualOuTrimestral == 'Trimestre':

                try:           
                    if barra == "Calculo JCP":
                        colunas = st.columns(4)
                        trimestres = ['1º Trimestre', '2º Trimestre', '3º Trimestre', '4º Trimestre']
                        economia_gerada_por_trimestre = []
                        arquivoFinalParaExportacaoTri = []
                        tabelaUnicaLista = []
                        for ano in range(2019, 2024):
                                year_dfsLacs = []
                                resultadoJCP = []
                                resultadoDedu = []
                                economiaGerada = []
                                tabelaUnica = []
                                for col, trimestre in zip(colunas, trimestres):
                                    with col:
                                        lacs = trimestralFiltrandoDadosParaCalculo(
                                            trimestre=trimestre,
                                            ano=ano,
                                            mes_inicio=1,
                                            mes_fim=12,
                                            l100_file=uploaded_file_l100,
                                            l300_file=uploaded_file_l300,
                                            lacs_file=uploaded_file_lacs,
                                            lalur_file=uploaded_file_lalur,
                                            ecf670_file=uploaded_file_ecf670,
                                            ec630_file=uploaded_file_ec630
                                        )

                                        st.subheader(f'{ano}    {trimestre}')
                                        lacs.runPipe()

                                        df = lacs.dataframeFinal
                                        df.columns = [f"{col} {trimestre}" for col in df.columns]
                                        year_dfsLacs.append(df)

                                        df = lacs.resultadoJPC
                                        df.columns = [f"{col} {trimestre}" for col in df.columns]
                                        resultadoJCP.append(df)

                                        df = lacs.resultadoLimiteDedu
                                        df.columns = [f"{col} {trimestre}" for col in df.columns]
                                        resultadoDedu.append(df)

                                        df = lacs.resultadoEconomiaGerada
                                        df.columns = [f"{col} {trimestre}" for col in df.columns]
                                        economiaGerada.append(df)

                                        economia_gerada_por_trimestre.append(lacs.economia)

                                dfCalculos = pd.concat(year_dfsLacs, axis=1)
                                tabelaJCP = pd.concat(resultadoJCP, axis=1)
                                limiteDedutibili = pd.concat(resultadoDedu, axis=1)
                                economiaGerada = pd.concat(economiaGerada, axis=1)

                                tabelaUnica = pd.concat([dfCalculos,tabelaJCP,limiteDedutibili,economiaGerada],axis=0)
                                tabelaUnicaLista.append(tabelaUnica.add_suffix(ano))
                    

                                st.subheader(f"Resultados Anuais - {ano}")
                                st.dataframe(dfCalculos)
                                st.dataframe(tabelaJCP)
                                st.dataframe(limiteDedutibili)
                                st.dataframe(economiaGerada)

                        arquivoFinalParaExportacaoTri = pd.concat(tabelaUnicaLista,axis=1)
      
                    if barra == "Lacs e Lalur":
                        col1, col2, col3, col4 = st.columns(4)
                        trimestres = ['1º Trimestre', '2º Trimestre', '3º Trimestre', '4º Trimestre']
                        tabelaFinalLacsLalurUnificad = []
                        for ano in range(2019, 2024):
                            year_dfsLacs = []
                            year_dfsLalurIRPJ = []
                            tabelaFinalLacsLalur = []

                            for col, trimestre in zip([col1, col2, col3, col4], trimestres):
                                with col:

                                    lacs = trimestralFiltrandoDadosParaCalculo(
                                            trimestre=trimestre,
                                            ano=ano,
                                            mes_inicio=1,
                                            mes_fim=12,
                                            l100_file=uploaded_file_l100,
                                            l300_file=uploaded_file_l300,
                                            lacs_file=uploaded_file_lacs,
                                            lalur_file=uploaded_file_lalur,
                                            ecf670_file=uploaded_file_ecf670,
                                            ec630_file=uploaded_file_ec630
                                        )

                                    lacs.LacsLalurTrimestral.runPipeLacsLalurCSLL()
                                    df = lacs.LacsLalurTrimestral.dataframeFinal
                                    df.columns = [f"{col} {trimestre}" for col in df.columns] 
                                    year_dfsLacs.append(df)


                                    lacs.LacsLalurTrimestral.runPipeLacsLalurIRPJ() 
                                    df2 = lacs.LacsLalurTrimestral.dataframeFinalIRPJ
                                    df2.columns = [f"{col} {trimestre}" for col in df2.columns] 
                                    year_dfsLalurIRPJ.append(df2)


                            dfFinalLacs = pd.concat(year_dfsLacs, axis=1)
                            dfFinalLacsIRPJ = pd.concat(year_dfsLalurIRPJ, axis=1)

                            tabelaFinalLacsLalur = pd.concat([dfFinalLacs,dfFinalLacsIRPJ],axis=0)
                            tabelaFinalLacsLalurUnificad.append(tabelaFinalLacsLalur.add_suffix(ano))
                    
                                
                            st.subheader(f"Resultados Anuais - {ano}")
                            st.dataframe(dfFinalLacs)
                            st.dataframe(dfFinalLacsIRPJ)
                        arquivoFinalParaExportacaoTriLacs = pd.concat(tabelaFinalLacsLalurUnificad,axis=1)    
                        st.dataframe(arquivoFinalParaExportacaoTriLacs)



                except Exception as e:
                    st.warning(f'Error :{str(e)}')
                    
                    pass
                        
                     

    try:
        if anualOuTrimestral == 'Ano':
            if barra == 'Calculo JCP':
                output8 = io.BytesIO()
                with pd.ExcelWriter(output8, engine='xlsxwriter') as writer:arquivoFInalParaExpostacao.to_excel(writer,sheet_name=f'JCP',index=False)
                output8.seek(0)
                st.write('')
                st.write('')
                st.write('')
                st.download_button(type='primary',label="Exportar tabela",data=output8,file_name=f'JCP.xlsx',key='download_button')
            elif barra == 'Lacs e Lalur':
                output7 = io.BytesIO()
                with pd.ExcelWriter(output7, engine='xlsxwriter') as writer:exportarLacsLalur.to_excel(writer,sheet_name=f'Lacs Lalur',index=False)
                output7.seek(0)
                st.write('')
                st.write('')
                st.write('')
                st.download_button(type='primary',label="Exportar tabela",data=output7,file_name=f'Lacs Lalur.xlsx',key='download_button')                    
        elif anualOuTrimestral == 'Trimestre':
            if barra == 'Calculo JCP':
                output9 = io.BytesIO()
                with pd.ExcelWriter(output9, engine='xlsxwriter') as writer:arquivoFinalParaExportacaoTri.to_excel(writer,sheet_name=f'JCP',index=False)
                output9.seek(0)
                st.write('')
                st.write('')
                st.write('')
                st.download_button(type='primary',label="Exportar tabela",data=output9,file_name=f'JCP Trimestral.xlsx',key='download_button')
            elif barra == 'Lacs e Lalur':
                output10 = io.BytesIO()
                with pd.ExcelWriter(output10, engine='xlsxwriter') as writer:arquivoFinalParaExportacaoTriLacs.to_excel(writer,sheet_name=f'Lacs Lalur',index=False)
                output10.seek(0)
                st.write('')
                st.write('')
                st.write('')
                st.download_button(type='primary',label="Exportar tabela",data=output10,file_name=f'LacsLalus Trimestral.xlsx',key='download_button')
    
    except:
        pass

end_time = time.time()

execution_time = end_time - start_time



      
with st.sidebar.expander('Dados Processamento'):
    st.write(f"Tempo de execução: {execution_time} segundos")
    cpu_usage = psutil.cpu_percent(interval=1)
    memory_usage = psutil.virtual_memory().percent
    st.write(f"Uso de CPU: {cpu_usage}%")
    st.write(f"Uso de Memória: {memory_usage}%")

    df_tempo_processamento = pd.DataFrame(tempoProcessamentoDasFuncoes)
    st.dataframe(df_tempo_processamento)


