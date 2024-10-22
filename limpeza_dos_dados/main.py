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
import functools
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from db.controllerDB import dbController
from regrasDeNegocio.aplicandoFormulaJPC import CalculosEProcessamentoDosDados
from relatorioPDF.relatorioAnual import RelatorioPDFJSCP
from arquivosSPED.pipeArquivosECF import SpedProcessor
from LacsLalur.AposInovacoesLacsLalur import LacsLalurAposInovacoes




st.set_page_config(layout='wide')

controler = dbController('taxall')
lacslalur = LacsLalurAposInovacoes('taxall')


start_time = time.time()
tempoProcessamentoDasFuncoes = []
background_image ="Untitleddesign.jpg"
st.markdown(
     f"""
     <iframe src="data:image/jpg;base64,{base64.b64encode(open(background_image, 'rb').read()).decode(

    )}" style="width:4000px;height:3000px;position: absolute;top:-3vh;right:-1250px;opacity: 0.5;background-size: cover;background-position: center;"></iframe>
     """,
     unsafe_allow_html=True )

if __name__=='__main__':


    with st.spinner('Carregando dados'):

            try:
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
                
                calculos.filtrarCalcularECadastras(file_paths,file_path)
                st.success('Dados processados e salvos!')
                for file in file_paths:
                    os.remove(file)
            except Exception as e:
                #st.warning(e)
                pass
    controler.engine.dispose()


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







