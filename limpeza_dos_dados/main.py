import streamlit as st
import numpy as np
import pandas as pd

import base64
import io
import textwrap
import re
import sys
import os
import time
import psutil


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from db.controllerDB import dbController
from regrasDeNegocio.aplicandoFormulaJPC import CalculosEProcessamentoDosDados
from relatorioPDF.relatorioAnual import RelatorioPDFJSCP
from arquivosSPED.pipeArquivosECF import SpedProcessor
from LacsLalur.AposInovacoesLacsLalur import LacsLalurAposInovacoes

controler = dbController('taxall')
#controler = dbController('taxall')


st.set_page_config(layout='wide')

controler = dbController('taxall')
lacslalur = LacsLalurAposInovacoes('taxall')


start_time = time.time()
tempoProcessamentoDasFuncoes = []
background_image ="Untitleddesign.jpg"
st.markdown(
     f"""
     <iframe src="data:image/jpg;base64,{base64.b64encode(open(background_image, 'rb').read()).decode(

    )}" style="width:3000px;height:9000px;position: absolute;top:-3vh;right:-350px;opacity: 0.5;background-size: cover;background-position: center;"></iframe>
     """,
     unsafe_allow_html=True )

def reCalculandoAno(economia2019: pd.DataFrame,retirarMulta: bool ,valorIRPJ:bool) -> pd.DataFrame:
    #'''Função de callback para recalcular os valores apresentados e gerados para análise anual do JCP'''
        economia2019.at[8, 'Value'] = economia2019.at[6, 'Value'] + economia2019.at[7, 'Value']
        economia2019.at[17, 'Value'] = sum([economia2019.at[0, 'Value'], economia2019.at[2, 'Value'], 
                                            economia2019.at[8, 'Value'], economia2019.at[13, 'Value'],
                                            economia2019.at[14, 'Value'], economia2019.at[12, 'Value'],
                                            economia2019.at[15, 'Value']])
        economia2019.at[22, 'Value'] = economia2019.at[17, 'Value']
        economia2019.at[24, 'Value'] = economia2019.at[22, 'Value'] * (economia2019.at[23, 'Value'] / 100)
        economia2019.at[25, 'Value'] = economia2019.at[24, 'Value'] * 0.15
        economia2019.at[26, 'Value'] = economia2019.at[24, 'Value'] - economia2019.at[25, 'Value']
        economia2019.at[27, 'Value'] = economia2019.at[20, 'Value'] * 0.5
        economia2019.at[28, 'Value'] = (economia2019.at[8, 'Value'] + economia2019.at[14, 'Value']) * 0.5
        if retirarMulta == True:
            economia2019.at[29, 'Value'] = economia2019.at[25, 'Value'] + (economia2019.at[25, 'Value'] * 0.2 * 0)
        else:
            economia2019.at[29, 'Value'] = economia2019.at[25, 'Value'] + (economia2019.at[25, 'Value'] * 0.2)
        if valorIRPJ == True:        
            economia2019.at[30, 'Value'] = economia2019.at[24, 'Value'] * 0.24
            economia2019.at[30,'Operation'] = 'REDUÇÃO NO IRPJ/CSLL - 0.24%'
        else:    
            economia2019.at[30, 'Value'] = economia2019.at[24, 'Value'] * 0.34
            economia2019.at[30,'Operation'] = 'REDUÇÃO NO IRPJ/CSLL - 0.34%'
        economia2019.at[31, 'Value'] = economia2019.at[30, 'Value'] - economia2019.at[29, 'Value']
        
        return economia2019

def reCalculandoTrimestral(economia2019: pd.DataFrame,retirarMulta: bool, valorIRPJ: bool)-> pd.DataFrame:
    #'''Função de callback para recalcular os valores apresentados e gerados para análise trimestral do JCP'''
    trimestres = [1,2,3,4]
    for i in trimestres:
        
        economia2019_copy = economia2019.copy()  
        economia2019_copy.at[13, f'Value {i}º Trimestre'] = sum([economia2019_copy.at[0, f'Value {i}º Trimestre'], economia2019_copy.at[1, f'Value {i}º Trimestre'], 
                                                            economia2019_copy.at[2, f'Value {i}º Trimestre'], economia2019_copy.at[4, f'Value {i}º Trimestre'],economia2019_copy.at[5, f'Value {i}º Trimestre'],
                                                            economia2019_copy.at[11, f'Value {i}º Trimestre'],economia2019_copy.at[12, f'Value {i}º Trimestre']])-economia2019_copy.at[9, f'Value {i}º Trimestre']
        if economia2019_copy.at[13, f'Value {i}º Trimestre'] > 0:
            economia2019_copy.at[14, f'Value {i}º Trimestre'] = economia2019_copy.at[13, f'Value {i}º Trimestre']
        else:
            economia2019_copy.at[14, f'Value {i}º Trimestre'] = 0.0
        
        if economia2019_copy.at[13, f'Value {i}º Trimestre'] > 0:
            economia2019_copy.at[16, f'Value {i}º Trimestre'] = economia2019_copy.at[14, f'Value {i}º Trimestre'] * (economia2019_copy.at[15, f'Value {i}º Trimestre'] / 100)
            economia2019_copy.at[17, f'Value {i}º Trimestre'] = economia2019_copy.at[16, f'Value {i}º Trimestre'] * 0.15       
            economia2019_copy.at[18, f'Value {i}º Trimestre'] = abs(economia2019_copy.at[16, f'Value {i}º Trimestre'] - economia2019_copy.at[17, f'Value {i}º Trimestre'])
            economia2019_copy.at[20, f'Value {i}º Trimestre'] = (economia2019_copy.at[5, f'Value {i}º Trimestre'] + economia2019_copy.at[11, f'Value {i}º Trimestre']) * 0.5
            if retirarMulta == True:            
                economia2019_copy.at[21, f'Value {i}º Trimestre'] = economia2019_copy.at[17, f'Value {i}º Trimestre'] + (economia2019_copy.at[17, f'Value {i}º Trimestre'] * 0.2 * 0)
            else:
                economia2019_copy.at[21, f'Value {i}º Trimestre'] = economia2019_copy.at[17, f'Value {i}º Trimestre'] + (economia2019_copy.at[17, f'Value {i}º Trimestre'] * 0.2)    
            
            if valorIRPJ == True:
                economia2019_copy.at[22, f'Value {i}º Trimestre'] = economia2019_copy.at[16, f'Value {i}º Trimestre'] * 0.24
                economia2019_copy.at[22, f'Operation {i}º Trimestre'] = 'REDUÇÃO NO IRPJ/CSLL - 0.24%'
            else:
                economia2019_copy.at[22, f'Value {i}º Trimestre'] = economia2019_copy.at[16, f'Value {i}º Trimestre'] * 0.34    
                economia2019_copy.at[22, f'Operation {i}º Trimestre'] = 'REDUÇÃO NO IRPJ/CSLL - 0.34%'

            economia2019_copy.at[23, f'Value {i}º Trimestre'] = economia2019_copy.at[22, f'Value {i}º Trimestre'] - economia2019_copy.at[21, f'Value {i}º Trimestre']
            
            economia2019_copy[f'Value {i}º Trimestre'] = round(economia2019_copy[f'Value {i}º Trimestre'],2)
        else:
            economia2019_copy.at[16, f'Value {i}º Trimestre'] = 0
            economia2019_copy.at[17, f'Value {i}º Trimestre'] = 0     
            economia2019_copy.at[18, f'Value {i}º Trimestre'] = 0
            economia2019_copy.at[20, f'Value {i}º Trimestre'] = 0
                        
            economia2019_copy.at[21, f'Value {i}º Trimestre'] = 0
            if valorIRPJ == True:
                economia2019_copy.at[22, f'Value {i}º Trimestre'] = 0
                economia2019_copy.at[22, f'Operation {i}º Trimestre'] = 'REDUÇÃO NO IRPJ/CSLL - 0.24%'
            else:
                economia2019_copy.at[22, f'Value {i}º Trimestre'] = 0  
                economia2019_copy.at[22, f'Operation {i}º Trimestre'] = 'REDUÇÃO NO IRPJ/CSLL - 0.34%'

            economia2019_copy.at[23, f'Value {i}º Trimestre'] = 0
            economia2019_copy.at[19, f'Value {i}º Trimestre'] = 0

            economia2019_copy[f'Value {i}º Trimestre'] = round(economia2019_copy[f'Value {i}º Trimestre'],2)

       # economia2019_copy[f'Value {i}º Trimestre'] = economia2019_copy[f'Value {i}º Trimestre'].apply(lambda x: '{:,.2f}'.format(x).replace('.', 'X').replace(',', '.').replace('X', ','))
        
        economia2019 = economia2019_copy

    return economia2019

def criandoVisualizacao(trimestre: list, ano: int, anoDeAnalise: bool, dataframesParaDownload: pd.DataFrame, cnpj_selecionado:str,tabelaParaRelatorio:str):

    #'''Cria visualizaçãos dos widgets e tabelas'''
    st.subheader(anoDeAnalise)

    periodoDeAnalise = st.toggle('', key=f"teste{anoDeAnalise}")

    session_cnpj_key = f'cnpj_selecionado_{anoDeAnalise}'

    if periodoDeAnalise:
        st.write(ano)
        session_state_name = f"economia{anoDeAnalise}"
        # Callbacks para atualizaçãos das alterações quando usurio fizer inputs manuais ou alterar aliquotas
        if session_state_name not in st.session_state or st.session_state.get(session_cnpj_key, None) != cnpj_selecionado:
            economia2019 = controler.queryResultadoFinal(cnpj_selecionado, "resultadosjcp", anoDeAnalise).iloc[:, [3,2,4]].set_index('index').sort_values(by='index')
            st.session_state[session_state_name] = economia2019
        st.session_state[session_cnpj_key] = cnpj_selecionado
        # A tabela foi armazenada dentro de um form para que nao tenha execução do codigo a cada iteração do usuario, 
        with st.form(f"my_form{anoDeAnalise}{ano}"):
            multa = st.toggle('Retirar multa', key=f'{anoDeAnalise}')
            valorIRPJ = st.toggle('Alterar valor IRPJ de 34% para 24%',key=f'{anoDeAnalise}widgetMulta')
            economia2019_data_editor = st.data_editor(st.session_state[session_state_name], key=f'{anoDeAnalise}deano', height=1175, use_container_width=True)
            submitted = st.form_submit_button(f"Atualizar {anoDeAnalise}")

        if submitted:
            st.session_state[session_state_name] = reCalculandoAno(economia2019_data_editor, multa,valorIRPJ)

        if st.button('Atualizar Banco de Dados',key=f'{cnpj_selecionado,anoDeAnalise}'):

            controler.update_table('resultadosjcp', economia2019_data_editor, cnpj_selecionado, anoDeAnalise)    
        
        with st.expander('Lacs Lalur'):
            lacslalur.gerandoTabelas(cnpj_selecionado,anoDeAnalise)
        
        #Tabelas para gerar o relatorio fiscal
        tabelaRelatorio = economia2019_data_editor.copy()
        tabelaRelatorio = tabelaRelatorio.iloc[30:,:].reset_index(drop='index')
        tabelaRelatorio = tabelaRelatorio.drop(columns='Operation')
        tabelaRelatorio.columns = [f"{col}_{anoDeAnalise}" for col in tabelaRelatorio.columns]

        #Tabela para exportação em excel
        resultadoAnual = economia2019_data_editor.copy()
        resultadoAnual.columns = [f"{col}_{anoDeAnalise}" for col in resultadoAnual.columns]
        resultadoAnual = resultadoAnual.drop([4,5,6,7,15,20]).reset_index(drop='index')

    else:
        st.write(trimestre) 
        session_state_name = f"economia{anoDeAnalise}Trimestral"
        #Funções de callbacks para análise trimestral, lógica e igual a do anual , porém com o trimestral, a função de callback faz um loop para iterar sobre cada trimestre
        if session_state_name not in st.session_state or st.session_state.get(session_cnpj_key, None) != cnpj_selecionado:
            economia2019Trimestral = controler.queryResultadoFinalTrimestral(cnpj_selecionado, "resultadosjcptrimestral", anoDeAnalise).iloc[:, [2,3,4,5,6,7,8,9,10]].set_index('index').sort_values(by='index')
            st.session_state[session_state_name] = economia2019Trimestral
        st.session_state[session_cnpj_key] = cnpj_selecionado
        
        with st.form(f"{anoDeAnalise}{trimestre}"):

            multa = st.toggle('Retirar multa', key=f'{anoDeAnalise}')
            valorIRPJ = st.toggle('Alterar valor IRPJ de 34% para 24%',key=f'{anoDeAnalise}widgetMulta')

            economia2019Trimestral_data_editor = st.data_editor(st.session_state[session_state_name], key=f'data_editor_{anoDeAnalise}', height=900, use_container_width=True)
            submittedbutton1 = st.form_submit_button(f"Atualizar {anoDeAnalise}")

        if submittedbutton1:
            if 'form_submitted' not in st.session_state or not st.session_state.form_submitted:
                st.session_state[session_state_name] = reCalculandoTrimestral(economia2019Trimestral_data_editor, multa,valorIRPJ)
                st.session_state.form_submitted = True
            else:
                st.session_state.form_submitted = False
        
        
        if st.button('Atualizar Banco de Dados',key=f'{cnpj_selecionado,anoDeAnalise}'):

            controler.update_table_trimestral('resultadosjcptrimestral', economia2019Trimestral_data_editor, cnpj_selecionado, anoDeAnalise)    
        
        with st.expander('Lacs Lalur'):
            lacslalur.gerandoTabelasTrimestral(cnpj_selecionado,anoDeAnalise)

        tabelaRelatorioTri = economia2019Trimestral_data_editor.copy()
        tabelaRelatorioTri = tabelaRelatorioTri.iloc[22:,[0,1,3,5,7]].reset_index(drop='index')
        
        tabelaRelatorioTri[f'Value_{anoDeAnalise}'] = sum([tabelaRelatorioTri.at[1,'Value 1º Trimestre'],tabelaRelatorioTri.at[1,'Value 2º Trimestre'],
                                                        tabelaRelatorioTri.at[1,'Value 3º Trimestre'],tabelaRelatorioTri.at[1,'Value 4º Trimestre']])
        
        tabelaRelatorioTri.at[0,f'Value_{anoDeAnalise}'] = sum([tabelaRelatorioTri.at[0,'Value 1º Trimestre'],tabelaRelatorioTri.at[0,'Value 2º Trimestre'],
                                                        tabelaRelatorioTri.at[0,'Value 3º Trimestre'],tabelaRelatorioTri.at[0,'Value 4º Trimestre']])
        
        tabelaRelatorioTri = tabelaRelatorioTri.iloc[:,5].reset_index(drop='index')

        resultaTrimestral = economia2019Trimestral_data_editor
        resultaTrimestral.columns = [f"{col}_{anoDeAnalise}" for col in resultaTrimestral.columns]
        
    if periodoDeAnalise == True:
        dataframesParaDownload.append(resultadoAnual)
        tabelaParaRelatorio.append(tabelaRelatorio)
    else:
         dataframesParaDownload.append(resultaTrimestral)
         tabelaParaRelatorio.append(tabelaRelatorioTri) 


if __name__=='__main__':

    
    seletorDePagina = st.sidebar.radio('Selecione',['Ver tabelas','Processar dados'])

    if seletorDePagina=='Ver tabelas':
        

        
        tabelaDeNomes = controler.get_all_data('cadastrodasempresas')
        listaDosNomesDasEmpresas = list(tabelaDeNomes['NomeDaEmpresa'])
        nome_para_cnpj = dict(zip(tabelaDeNomes['NomeDaEmpresa'], tabelaDeNomes['CNPJ']))

        dataframesParaDownload = []
        tabelaParaRelatorio = []
        nomeEmpresaSelecionada = st.sidebar.selectbox('Selecione a empresa',listaDosNomesDasEmpresas)
        cnpj_selecionado = nome_para_cnpj[nomeEmpresaSelecionada]
        
        if 'cnpj_selecionado' not in st.session_state:
            st.session_state.cnpj_selecionado = cnpj_selecionado
            
        st.header(f'{nomeEmpresaSelecionada}')
        st.subheader('')
        st.subheader('')

        tabelaPerioDeAnalise = controler.get_data_by_cnpj(cnpj_selecionado,'tipodaanalise')
        tabelaPerioDeAnalise = tabelaPerioDeAnalise.iloc[:,2:]
        tabelaPerioDeAnalise['PeriodoDeAnalise'] = tabelaPerioDeAnalise['PeriodoDeAnalise'].astype(str).str.replace(',','').str[:-2] 
    
        tabelaPerioDeAnalise = tabelaPerioDeAnalise.rename(columns={'PeriodoDeAnalise':'Periodo de Analise','TipoDaAnalise':'Tipo da Analise'})
        tabelaPerioDeAnalise = tabelaPerioDeAnalise.set_index('Periodo de Analise')
        st.dataframe(tabelaPerioDeAnalise)
        
        col1,col2,col3,col4,col5 = st.columns(5)
                    
        ano = 'Análise Anual'
        trimestre = 'Análise trimestral'

        with col1:
        
            criandoVisualizacao(trimestre,ano,2019,dataframesParaDownload,cnpj_selecionado,tabelaParaRelatorio)

        with col2:         

            criandoVisualizacao(trimestre,ano,2020,dataframesParaDownload,cnpj_selecionado,tabelaParaRelatorio)

        with col3:

            criandoVisualizacao(trimestre,ano,2021,dataframesParaDownload,cnpj_selecionado,tabelaParaRelatorio)

        with col4:

            criandoVisualizacao(trimestre,ano,2022,dataframesParaDownload,cnpj_selecionado,tabelaParaRelatorio)

        with col5:

            criandoVisualizacao(trimestre,ano,2023,dataframesParaDownload,cnpj_selecionado,tabelaParaRelatorio)



    
        arquivoParaDownload = pd.concat(dataframesParaDownload,axis=1)

        output8 = io.BytesIO()
        with pd.ExcelWriter(output8, engine='xlsxwriter') as writer:arquivoParaDownload.to_excel(writer,sheet_name=f'JSCP', index=False)
        output8.seek(0)
        st.write('')
        st.write('')
        st.write('')
        st.download_button(type='primary',label="Exportar tabela JSCP",data=output8,file_name=f"JSCP'.xlsx",key='download_button')
        st.write('')
        st.write('')
        st.write('')
        
        colunas = ['2019','2020','2021','2022','2023']
        
        try:
            dataframeParaRelatorio = pd.concat(tabelaParaRelatorio,axis=1,ignore_index=True).rename(columns={0:'',1:'2019',2:'2020',3:'2021',4:'2022',5:'2023'})
            for i in colunas:
                dataframeParaRelatorio[i] = dataframeParaRelatorio[i].apply(lambda x: f"{float(x):,.2f}" if pd.notnull(x) else x).str.replace('.', '_').str.replace(',', '.').str.replace('_', ',')

            dataframeParaRelatorio.at[0,''] = 'Redução no IRPJ/CSLL'
        except:
            dataframeParaRelatorio = pd.concat(tabelaParaRelatorio,axis=1,ignore_index=True)
            dataframeParaRelatorio[''] = ''
            dataframeParaRelatorio = dataframeParaRelatorio[['',0,1,2,3,4]].rename(columns={0:'2019',1:'2020',2:'2021',3:'2022',4:'2023'})
            dataframeParaRelatorio.at[0,''] =  'Redução no IRPJ/CSLL'
            dataframeParaRelatorio.at[1,''] = 'Economia'
            for i in colunas:
                dataframeParaRelatorio[i] = dataframeParaRelatorio[i].apply(lambda x: f"{float(x):,.2f}" if pd.notnull(x) else x).str.replace('.', '_').str.replace(',', '.').str.replace('_', ',')


           

        with col1: 
            st.write('')
            st.write('')
            st.write('')
            st.header('Gerar Relatório')
            aliquotaImposto = st.text_input('Digite o valor da alíquota de imposto, ex(24,34)')
            dataAssinatura = st.text_input('Escreva a data da assinatura do contrato, ex. 23 de agosto de 2024 ')
            observacoesDoAnlista = st.text_area('Digite aqui as observações :',height=500)
        
            pdf = RelatorioPDFJSCP()
            
            pdf.valorTotal(dataframeParaRelatorio)

            pdf_buffer = pdf.create_pdf(nomeEmpresaSelecionada, aliquotaImposto, observacoesDoAnlista, dataAssinatura)          

            st.download_button(label="Baixar relatório",data=pdf_buffer,file_name="relatório.pdf",mime="application/pdf")


    with st.spinner('Carregando dados'):
        if seletorDePagina =='Processar dados':
            #try:
            uploaded_files = st.sidebar.file_uploader("Escolha os arquivos SPED", type=['txt'], accept_multiple_files=True)

            if uploaded_files:
                                file_paths = []
                                for uploaded_file in uploaded_files:
                                    file_path = uploaded_file.name
                                    with open(file_path, 'wb') as f:
                                        f.write(uploaded_file.getbuffer())
                                    file_paths.append(file_path)
                                
                                periodoDeAnalise = []
                                sped_processor = SpedProcessor(file_paths)                            
                                for file in file_paths:
                                    periodoDeAnalise.append(sped_processor.pegandoPeriodoDeAnalise(file))

                                periodosETipoDeAnalise = pd.concat(periodoDeAnalise)
                                controler.inserirTabelas('tipodaanalise',periodosETipoDeAnalise)

            calculos = CalculosEProcessamentoDosDados()
                #try:
            calculos.filtrarCalcularECadastras(file_paths,file_path)
            #     except:
            #         pass
            # except Exception as e:
            #     st.write(e)




finish_time = time.time()
execution_time = finish_time - start_time

with st.sidebar.expander('Dados Processamento'):
    st.write(f"Tempo de execução: {execution_time} segundos")
    cpu_usage = psutil.cpu_percent(interval=1)
    memory_usagePercent = psutil.virtual_memory().percent
    memory_usage = psutil.virtual_memory().used
    st.write(f"Uso de CPU: {cpu_usage}%")
    st.write(f"Uso de Memória: {memory_usagePercent}%")
    st.write(f"Uso de Memória: {memory_usage}%")
    df_tempo_processamento = pd.DataFrame(tempoProcessamentoDasFuncoes)
    st.dataframe(df_tempo_processamento)







