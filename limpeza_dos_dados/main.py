import streamlit as st

from db.controllerDB import dbController
from aplicandoFormulaJPC import CalculosEProcessamentoDosDados
from relatorioPDF.relatorioAnual import RelatorioPDFJSCP

import pandas as pd
import base64
import io
import textwrap
import re

#st.set_page_config(layout='wide')
background_image ="Untitleddesign.jpg"
st.markdown(
     f"""
     <iframe src="data:image/jpg;base64,{base64.b64encode(open(background_image, 'rb').read()).decode(

    )}" style="width:3000px;height:9000px;position: absolute;top:-3vh;right:-350px;opacity: 0.5;background-size: cover;background-position: center;"></iframe>
     """,
     unsafe_allow_html=True )

def reCalculandoAno(economia2019,retirarMulta):
  
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
        economia2019.at[30, 'Value'] = economia2019.at[24, 'Value'] * 0.34
        economia2019.at[31, 'Value'] = economia2019.at[30, 'Value'] - economia2019.at[29, 'Value']
        
        return economia2019
def reCalculandoTrimestral(economia2019,retirarMulta):

    trimestres = [1,2,3,4]
    for i in trimestres:
        economia2019_copy = economia2019.copy()  
        economia2019_copy.at[15, f'Value {i}º Trimestre'] = sum([economia2019_copy.at[0, f'Value {i}º Trimestre'], economia2019_copy.at[2, f'Value {i}º Trimestre'], 
                                                            economia2019_copy.at[6, f'Value {i}º Trimestre'], economia2019_copy.at[7, f'Value {i}º Trimestre'],
                                                            economia2019_copy.at[12, f'Value {i}º Trimestre'], economia2019_copy.at[13, f'Value {i}º Trimestre']])
        economia2019_copy.at[16, f'Value {i}º Trimestre'] = economia2019_copy.at[15, f'Value {i}º Trimestre']
        economia2019_copy.at[18, f'Value {i}º Trimestre'] = economia2019_copy.at[16, f'Value {i}º Trimestre'] * (economia2019_copy.at[17, f'Value {i}º Trimestre'] / 100000)
        economia2019_copy.at[19, f'Value {i}º Trimestre'] = economia2019_copy.at[20, f'Value {i}º Trimestre'] * 0.15       
        economia2019_copy.at[20, f'Value {i}º Trimestre'] = economia2019_copy.at[18, f'Value {i}º Trimestre'] - economia2019_copy.at[19, f'Value {i}º Trimestre']
        economia2019_copy.at[22, f'Value {i}º Trimestre'] = (economia2019_copy.at[6, f'Value {i}º Trimestre'] + economia2019_copy.at[12, f'Value {i}º Trimestre']) * 0.5
        if retirarMulta == True:            
            economia2019_copy.at[23, f'Value {i}º Trimestre'] = economia2019_copy.at[19, f'Value {i}º Trimestre'] + (economia2019_copy.at[19, f'Value {i}º Trimestre'] * 0.2 * 0)
        else:
            economia2019_copy.at[23, f'Value {i}º Trimestre'] = economia2019_copy.at[19, f'Value {i}º Trimestre'] + (economia2019_copy.at[19, f'Value {i}º Trimestre'] * 0.2)    
        economia2019_copy.at[24, f'Value {i}º Trimestre'] = economia2019_copy.at[20, f'Value {i}º Trimestre'] * 0.34
        economia2019_copy.at[25, f'Value {i}º Trimestre'] = economia2019_copy.at[24, f'Value {i}º Trimestre'] - economia2019_copy.at[23, f'Value {i}º Trimestre']

        
        economia2019 = economia2019_copy

        return economia2019

def criandoVisualizacao(trimestre, ano, anoDeAnalise, dataframesParaDownload, cnpj_selecionado):
    st.subheader(anoDeAnalise)
    multa = st.toggle('Retirar multa', key=f'{anoDeAnalise}')
    periodoDeAnalise = st.toggle('', key=f"teste{anoDeAnalise}")

    session_cnpj_key = f'cnpj_selecionado_{anoDeAnalise}'

    if periodoDeAnalise:
        st.write(ano)
        session_state_name = f"economia{anoDeAnalise}"

        if session_state_name not in st.session_state or st.session_state.get(session_cnpj_key, None) != cnpj_selecionado:
            economia2019 = controler.queryResultadoFinal(cnpj_selecionado, "resultadosjcp", anoDeAnalise).iloc[:, [1, 2]]
            st.session_state[session_state_name] = economia2019
        st.session_state[session_cnpj_key] = cnpj_selecionado

        with st.form(f"my_form{anoDeAnalise}{ano}"):
            economia2019_data_editor = st.data_editor(st.session_state[session_state_name], key=f'{anoDeAnalise}deano', height=1175, use_container_width=True)
            submitted = st.form_submit_button(f"Atualizar {anoDeAnalise}")

        if submitted:
            st.session_state[session_state_name] = reCalculandoAno(economia2019_data_editor, multa)
        resultadoAnual = economia2019_data_editor.copy()
        resultadoAnual.columns = [f"{col}_{anoDeAnalise}" for col in resultadoAnual.columns]
        resultadoAnual = resultadoAnual.drop([4,5,6,7,15,20]).reset_index(drop='index')

    else:
        st.write(trimestre) 
        session_state_name = f"economia{anoDeAnalise}Trimestral"

        if session_state_name not in st.session_state or st.session_state.get(session_cnpj_key, None) != cnpj_selecionado:
            economia2019Trimestral = controler.queryResultadoFinal(cnpj_selecionado, "resultadosjcptrimestral", anoDeAnalise).iloc[:, :8]
            st.session_state[session_state_name] = economia2019Trimestral
        st.session_state[session_cnpj_key] = cnpj_selecionado
        
        with st.form(f"{anoDeAnalise}{trimestre}"):

            economia2019Trimestral_data_editor = st.data_editor(st.session_state[session_state_name], key=f'data_editor_{anoDeAnalise}', height=950, use_container_width=True)
            submittedbutton1 = st.form_submit_button(f"Atualizar {anoDeAnalise}")

        if submittedbutton1:
            if 'form_submitted' not in st.session_state or not st.session_state.form_submitted:
                st.session_state[session_state_name] = reCalculandoTrimestral(economia2019Trimestral_data_editor, multa)
                st.session_state.form_submitted = True
            else:
                st.session_state.form_submitted = False

        resultaTrimestral = economia2019Trimestral_data_editor
        resultaTrimestral.columns = [f"{col}_{anoDeAnalise}" for col in resultaTrimestral.columns]

    if periodoDeAnalise == True:
        dataframesParaDownload.append(resultadoAnual)
    else:
         dataframesParaDownload.append(resultaTrimestral)
          


if __name__=='__main__':

    
    seletorDePagina = st.sidebar.radio('Selecione',['Ver tabelas','Processar dados'])

    if seletorDePagina=='Ver tabelas':
        

        controler = dbController('ECF')
        tabelaDeNomes = controler.get_all_data('cadastrodasempresas')
        listaDosNomesDasEmpresas = list(tabelaDeNomes['NomeDaEmpresa'])
        nome_para_cnpj = dict(zip(tabelaDeNomes['NomeDaEmpresa'], tabelaDeNomes['CNPJ']))

        dataframesParaDownload = []
        nomeEmpresaSelecionada = st.sidebar.selectbox('Selecione a empresa',listaDosNomesDasEmpresas)
        cnpj_selecionado = nome_para_cnpj[nomeEmpresaSelecionada]
        if 'cnpj_selecionado' not in st.session_state:
            st.session_state.cnpj_selecionado = cnpj_selecionado
            
        st.header(f'{nomeEmpresaSelecionada}')
        st.subheader('')
        st.subheader('')


        col1,col2,col3,col4,col5 = st.columns(5)
        
              

        ano = 'Análise Anual'
        trimestre = 'Análise trimestral'

        with col1:
        
            criandoVisualizacao(trimestre,ano,2019,dataframesParaDownload,cnpj_selecionado)

        with col2:         

            criandoVisualizacao(trimestre,ano,2020,dataframesParaDownload,cnpj_selecionado)

        with col3:

            criandoVisualizacao(trimestre,ano,2021,dataframesParaDownload,cnpj_selecionado)

        with col4:

            criandoVisualizacao(trimestre,ano,2022,dataframesParaDownload,cnpj_selecionado)

        with col5:

            criandoVisualizacao(trimestre,ano,2023,dataframesParaDownload,cnpj_selecionado)

        arquivoParaDownload = pd.concat(dataframesParaDownload,axis=1)

        output8 = io.BytesIO()
        with pd.ExcelWriter(output8, engine='xlsxwriter') as writer:arquivoParaDownload.to_excel(writer,sheet_name=f'JSCP_{re.sub(r'[^a-zA-Z0-9_]+', '', textwrap.shorten(nomeEmpresaSelecionada, width=25))}', index=False)
        output8.seek(0)
        st.write('')
        st.write('')
        st.write('')
        st.download_button(type='primary',label="Exportar tabela JSCP",data=output8,file_name=f"JSCP_{re.sub(r'[^a-zA-Z0-9_]+', '', textwrap.shorten(nomeEmpresaSelecionada, width=25))}'.xlsx",key='download_button')
        



    with st.spinner('Carregando dados'):
        if seletorDePagina =='Processar dados':
            
            uploaded_files = st.sidebar.file_uploader("Escolha os arquivos SPED", type=['txt'], accept_multiple_files=True)
          
            if uploaded_files:
                            file_paths = []
                            for uploaded_file in uploaded_files:
                                file_path = uploaded_file.name
                                with open(file_path, 'wb') as f:
                                    f.write(uploaded_file.getbuffer())
                                file_paths.append(file_path)
            calculos = CalculosEProcessamentoDosDados()
            calculos.filtrarCalcularECadastras(file_paths,file_path)





























# '''    anualOuTrimestral = st.sidebar.selectbox("Anual ou Trimestral", ["Ano", 'Trimestre'])  
#     barra = st.radio("Menu", ["Calculo JCP", "Lacs e Lalur",'Relátorio']) 
    
#     if barra == "Relátorio":
#         st.cache_data.clear()
#         col1,col2,col3,col4,col5,col6 = st.columns(6)
#         with col1:
#             uploaded_file_resultados = st.file_uploader("Coloque o arquivo de resultado", type="xlsx")
        
#         if uploaded_file_resultados is not None:

#             with col1:
#                 nomeDaEmepresa = st.text_input('Digite o nome da empresa')
#                 aliquotaImposto = st.text_input('Digite o valor da alíquota de imposto, ex(24,34)')
#                 dataAssinatura = st.text_input('Escreva a data da assinatura do contrato, ex. 23 de agosto de 2024 ')
#                 observacoesDoAnlista = st.text_area('Digite aqui as observações :',height=500)
            

#             pdf = RelatorioPDFJSCP()
#             try:
#                 pdf.valorTotal(uploaded_file_resultados)
#             except:
#                 pdf.valorTotalTrimestral(uploaded_file_resultados)

#             pdf_buffer = pdf.create_pdf(nomeDaEmepresa, aliquotaImposto, observacoesDoAnlista, dataAssinatura)          
#             st.download_button(label="Baixar relatório",data=pdf_buffer,file_name="relatório.pdf",mime="application/pdf")'''




# ''' try:
#         if anualOuTrimestral == 'Ano':
#             if barra == 'Calculo JCP':
#                 output8 = io.BytesIO()
#                 with pd.ExcelWriter(output8, engine='xlsxwriter') as writer:arquivoFInalParaExpostacao.to_excel(writer,sheet_name=f'JSCP',index=False)
#                 output8.seek(0)
#                 st.write('')
#                 st.write('')
#                 st.write('')
#                 st.download_button(type='primary',label="Exportar tabela JSCP",data=output8,file_name=f'JCP.xlsx',key='download_button')
                
#                 output14 = io.BytesIO()
#                 with pd.ExcelWriter(output14, engine='xlsxwriter') as writer:exportaLacsLalurAposInovacoes.to_excel(writer,sheet_name=f'LacsLalur',index=False)
#                 output14.seek(0)
#                 st.write('')
#                 st.write('')
#                 st.write('')
#                 st.download_button(type='secondary',label="Exportar Lacs e Lalur Apos Inovacoes",
#                                    data=output14,file_name=f'LacsLalur Após Inovacoes.xlsx',key='botaoLacsn')
            
#         elif barra == 'Lacs e Lalur':
#                 output7 = io.BytesIO()
#                 with pd.ExcelWriter(output7, engine='xlsxwriter') as writer:exportarLacsLalur.to_excel(writer,sheet_name=f'LacsLalur',index=False)
#                 output7.seek(0)
#                 st.write('')
#                 st.write('')
#                 st.write('')
#                 st.download_button(type='primary',label="Exportar tabela",data=output7,file_name=f'LacsLalur.xlsx',key='download_button')                    
#         elif anualOuTrimestral == 'Trimestre':
#             if barra == 'Calculo JCP':
#                 output9 = io.BytesIO()
#                 with pd.ExcelWriter(output9, engine='xlsxwriter') as writer:arquivoFinalParaExportacaoTri.to_excel(writer,sheet_name=f'JSCP',index=False)
#                 output9.seek(0)
#                 st.write('')
#                 st.write('')
#                 st.write('')
#                 st.download_button(type='primary',label="Exportar tabela",data=output9,file_name=f'JCP.xlsx',key='download_button')
#             elif barra == 'Lacs e Lalur':
#                 output10 = io.BytesIO()
#                 with pd.ExcelWriter(output10, engine='xlsxwriter') as writer:arquivoFinalParaExportacaoTriLacs.to_excel(writer,sheet_name=f'LacsLalur',index=False)
#                 output10.seek(0)
#                 st.write('')
#                 st.write('')
#                 st.write('')
#                 st.download_button(type='primary',label="Exportar tabela",data=output10,file_name=f'LacsLalur.xlsx',key='download_button')
    
#     except:
#         pass'''

#Atualização da tabela anual, teste

        # with col1:
        #     st.subheader('2019')
        #     ano = 'Análise Anual'

        #     if 'economia2019' not in st.session_state:
        #         economia2019 = controler.queryResultadoFinal(cnpj_selecionado, "resultadosjcp", 2019).iloc[:, [1, 2]]
        #         st.session_state.economia2019 = economia2019

        #     economia2019 = controler.queryResultadoFinal(cnpj_selecionado, "resultadosjcp", 2019).iloc[:, [1, 2]]
        #     economia2019recalculada = reCalculandoAno(economia2019)

        #     with st.form("my_form"):
        #         economia2019_data_editor = st.data_editor(economia2019recalculada, key='2019de', height=1250, use_container_width=True)
        #         submitted = st.form_submit_button("Submit")

        #     if submitted:
        #         st.session_state.economia2019 = economia2019_data_editor
        #         st.session_state.economia2019recalculada = reCalculandoAno(st.session_state.economia2019)

        #     st.data_editor(st.session_state.economia2019, key='2019de_final', height=1250, use_container_width=True)

            # else:
            #     st.write(trimestre)
            #     economia2019 = controler.queryResultadoFinal(cnpj_selecionado,"resultadosjcptrimestral",2019).iloc[:,:8]
            # st.data_editor(st.session_state.economia2019,key='2019de',height=1150,use_container_width=True)
           