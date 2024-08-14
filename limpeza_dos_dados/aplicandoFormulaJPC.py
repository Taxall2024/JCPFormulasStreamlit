import pandas as pd
import streamlit as st
import numpy as np
from baseJPC.tratamentosDosDadosParaCalculo import FiltrandoDadosParaCalculo
from LacsLalur.lacsLalurAntesInoTributarias import LacsLalurCSLL
from bs4 import BeautifulSoup
import requests
from functools import lru_cache
import time
import base64
import io
import xlsxwriter
from xlsxwriter import Workbook



start_time = time.time()
st.set_page_config(layout="wide")
background_image ="Untitleddesign.jpg"
st.markdown(
    f"""
    <iframe src="data:image/jpg;base64,{base64.b64encode(open(background_image, 'rb').read()).decode(

    )}" style="width:3000px;height:3500px;position: absolute;top:-3vh;right:-350px;opacity: 0.5;background-size: cover;background-position: center;"></iframe>
    """,
    unsafe_allow_html=True
)

#@st.cache_data(ttl='1d')
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

    def __init__(self, data, lacs_file, lalur_file, ecf670_file, ec630_file, l100_file, l300_file):
        super().__init__(data, lacs_file, lalur_file, ecf670_file, ec630_file, l100_file, l300_file)
        self.data = data
        self.resultadoJPC = pd.DataFrame(columns=["Operation", "Value"])
        self.resultadoLimiteDedu = pd.DataFrame(columns=["Operation", "Value"])
        self.resultadoEconomiaGerada = pd.DataFrame(columns=["Operation", "Value"])

        self.dataframe = fetch_tjlp_data()


    def valorJPCRetroativo(self):
        key = f'retroativoJCP{self.data}'

        if key not in st.session_state:
            st.session_state[key] = 0.0

        st.session_state[key] = st.session_state[key]
        self.jcpRetroativo = st.number_input('Digite o valor de JCP ja utilizado pelo cliente', key=key, value=st.session_state[key])
        #self.resultsCalcJcp = pd.concat([self.resultsCalcJcp, pd.DataFrame([{"Operation": "Debito JCP(Cliente ja utilizou)", "Value": self.jcpRetroativo}])], ignore_index=True)



    def calculandoJPC(self, data):

        if data in self.dataframe.index:
            self.taxaJuros = self.dataframe.loc[data, 'Ano']
            self.valorJPC = round(self.totalJSPC * (self.dataframe.loc[data, 'Ano'] / 100), 2)-self.jcpRetroativo
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

    def nomeDasEmpresas(self, l100_file):
        l100 = pd.read_excel(l100_file)
        nomeEmpresa = ''        
        if l100['CNPJ'].iloc[0] == 79283065000141:
            nomeEmpresa = 'ORBENK ADMNISTRAÇÃO E SERVIÇOS LTDA'
        elif l100['CNPJ'].iloc[0] == 14576552000157:    
            nomeEmpresa = 'ORBENK SERVIÇOS DE SEGURANÇA LTDA'
        elif l100['CNPJ'].iloc[0] == 10332516000197:
            nomeEmpresa = 'ORBENK TERCEIRIZAÇÃO E SERVIÇOS LTDA'
        elif l100['CNPJ'].iloc[0] == 82513490000194:
            nomeEmpresa = 'PROFISER SERVIÇOS PROFISSIONAIS LTDA'
        elif l100['CNPJ'].iloc[0] == 3750757000190:
            nomeEmpresa = 'SEPAT MULTI SERVICE LTDA'                          
        else:
            nomeEmpresa = 'Empresa não encontrada'
        return nomeEmpresa
                    


    def limiteDedutibilidade(self):

        key = f'retirar_multa_{year}'
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

    def tabelaEconomia(self):

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

        delta_color = "normal" if self.economia > 0 else "inverse"
        st.metric("Economia Gerada", f"R$ {self.economia:,.2f}", delta_color=delta_color)

    def pipeCalculo(self, data):
        self.set_date(data)
        self.lucrosAcumulados()
        self.valorJPCRetroativo()
        self.TotalFinsCalcJSPC()
        self.calculandoJPC(self.data)
        self.limiteDedutibilidade()
        self.tabelaEconomia()
        return self.resultadoEconomiaGerada
        
        
if __name__ == "__main__":
         
  
    barra = st.radio("Menu", ["Calculo JCP", "Lacs e Lalur"])
    empresa_nome_placeholder = st.header("Empresa não selecionada")
     



    col1, col2, col3, col4, col5 = st.columns(5)

    uploaded_file_l100 = st.sidebar.file_uploader("Upload L100 Excel File", type="xlsx")
    uploaded_file_l300 = st.sidebar.file_uploader("Upload L300 Excel File", type="xlsx")
    uploaded_file_lacs = st.sidebar.file_uploader("Upload Lacs Excel File", type="xlsx")
    uploaded_file_lalur = st.sidebar.file_uploader("Upload Lalur Excel File", type="xlsx")
    uploaded_file_ecf670 = st.sidebar.file_uploader("Upload ECF 670 Excel File", type="xlsx")
    uploaded_file_ec630 = st.sidebar.file_uploader("Upload ECF 630 Excel File", type="xlsx")

    if uploaded_file_l100 and uploaded_file_l300 and uploaded_file_lacs and uploaded_file_lalur and uploaded_file_ecf670 and uploaded_file_ec630:
        filtrando_dados = FiltrandoDadosParaCalculo(
            data=None,
            lacs_file=uploaded_file_lacs,
            lalur_file=uploaded_file_lalur,
            ecf670_file=uploaded_file_ecf670,
            ec630_file=uploaded_file_ec630,
            l100_file=uploaded_file_l100,
            l300_file=uploaded_file_l300
        )


        calculos = {year: Calculo(data=str(year),
                                   lacs_file=uploaded_file_lacs,
                                   lalur_file=uploaded_file_lalur,
                                   ecf670_file=uploaded_file_ecf670,
                                   ec630_file=uploaded_file_ec630,
                                   l100_file=uploaded_file_l100,
                                   l300_file=uploaded_file_l300) for year in range(2019, 2024)} 

        empresa_nome = calculos[2019].nomeDasEmpresas(uploaded_file_l100)

        empresa_nome_placeholder.header(empresa_nome)    
         
                                            

        if barra == "Calculo JCP":

                
                economiaPorAno = []
                dataFrameParaExportar1 = []
                dataFrameParaExportar2 = []
                dataFrameParaExportar3 = []

                df = pd.DataFrame(columns=['Operation','Value'])
                

                for col, year in zip([col1, col2, col3, col4, col5], range(2019, 2024)):
                    
                    with col:
     
                        st.write('')
                        st.write('')
                        st.write('')
                        st.write('')
                        st.subheader(str(year))
                        
                        calculosIniciais = calculos[year].runPipe()
                        tabelaFinal = calculos[year].runPipeFinalTable()
                        resultadoTotal = calculos[year].pipeCalculo(str(year))

                        economiaPorAno.append(resultadoTotal)
                        dataFrameParaExportar1.append(calculosIniciais)
                        dataFrameParaExportar2.append(tabelaFinal)
                        dataFrameParaExportar3.append(resultadoTotal)
                
                dfmetricaGeral = pd.concat(economiaPorAno).reset_index(drop='index')
                dfmetricaGeral = dfmetricaGeral.transpose().iloc[:,[1,3,5,7,9]]
                dfmetricaGeral['Agregado do período'] = dfmetricaGeral.apply(lambda row: row.sum(), axis=1)

                arquivoParaExportar = pd.concat([df.add_suffix(f'_{year}') for df, year in zip(dataFrameParaExportar1, range(2019, 2024))], axis=1)
                arquivoParaExportar2 = pd.concat([df.add_suffix(f'_{year}') for df, year in zip(dataFrameParaExportar2, range(2019, 2024))], axis=1)
                arquivoParaExportar3 = pd.concat([df.add_suffix(f'_{year}') for df, year in zip(dataFrameParaExportar3, range(2019, 2024))], axis=1)
                
                arquivoFInalParaExpostacao = pd.concat([arquivoParaExportar,arquivoParaExportar2,arquivoParaExportar3],axis=0)

                st.write('')
                st.write('')
                st.write('')
                st.metric("Agregado da Economia Gerada", f"R$ {dfmetricaGeral.iloc[1,-1]:,.2f}")

                output8 = io.BytesIO()
                with pd.ExcelWriter(output8, engine='xlsxwriter') as writer:arquivoFInalParaExpostacao.to_excel(writer,sheet_name=f'JSCP',index=False)
                output8.seek(0)
                st.write('')
                st.write('')
                st.write('')
                st.download_button(type='primary',label="Exportar tabela",data=output8,file_name=f'JSCP.xlsx',key='download_button')


        if barra == "Lacs e Lalur":

            for col, year in zip([col1, col2, col3, col4, col5], range(2019, 2024)):
                with col:

                    st.write('')
                    st.write('')
                    st.write('')
                    st.write('')
                    st.subheader(str(year))
                    calculos[year].runPipeLacsLalurIRPJ()
                    calculos[year].runPipeLacsLalurCSLL()

end_time = time.time()

execution_time = end_time - start_time

print('#############################################')
print('TEMPO DE EXECUÇÃO DO PROGRAMA')
print(f"Tempo de execução: {execution_time} segundos")


