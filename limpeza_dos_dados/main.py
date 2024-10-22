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


def reCalculandoAno(economia2019: pd.DataFrame,retirarMulta: bool)-> pd.DataFrame:
    #'''Função de callback para recalcular os valores apresentados e gerados para análise trimestral do JCP'''


    
    economia2019_copy = economia2019.copy() 
    
    economia2019_copy.at[14, f'Value'] = np.sum([economia2019_copy.at[1, f'Value'],economia2019_copy.at[2, f'Value'],economia2019_copy.at[3, f'Value'],
                                                                economia2019_copy.at[4, f'Value'],economia2019_copy.at[5, f'Value'],
                                                                economia2019_copy.at[6, f'Value'],economia2019_copy.at[7, f'Value'],economia2019_copy.at[8, f'Value'],
                                                                economia2019_copy.at[9, f'Value'],economia2019_copy.at[11, f'Value'],
                                                                economia2019_copy.at[12, f'Value'],economia2019_copy.at[13, f'Value']]) - economia2019_copy.at[10, f'Value']

    #Calculando Total Para Fins de JSPC  -- 
    economia2019_copy.at[15, f'Value'] = sum([economia2019_copy.at[1, f'Value'], economia2019_copy.at[2, f'Value'], 
                                                        economia2019_copy.at[3, f'Value'], economia2019_copy.at[5, f'Value'],economia2019_copy.at[6, f'Value'],
                                                        economia2019_copy.at[12, f'Value'],economia2019_copy.at[13, f'Value']])-economia2019_copy.at[10, f'Value']
    
    #Veriricação se o valor de JSCP e negativo para ser a conta caso positivo
    if economia2019_copy.at[15, f'Value'] > 0:
        economia2019_copy.at[16, f'Value'] = economia2019_copy.at[15, f'Value'] - economia2019_copy.at[0,f'Value']
    else:
        economia2019_copy.at[16, f'Value'] = 0.0
    
    if economia2019_copy.at[15, f'Value'] > 0:

        #Calculando o Valor de JSCP(Valor da base multiplicado pela TJLP)
        economia2019_copy.at[18, f'Value'] = economia2019_copy.at[16, f'Value'] * (economia2019_copy.at[17, f'Value'] / 100)
        
        #Valor do IRRF (Multiplica o valor de JSCP por 15%)
        economia2019_copy.at[19, f'Value'] = economia2019_copy.at[18, f'Value'] * 0.15       
        
        # Valor de JSCP a apropriar pelo cliente( subtrair o valor de JSCP por pelo valor do IRRF )
        economia2019_copy.at[20, f'Value'] = abs(economia2019_copy.at[18, f'Value'] - economia2019_copy.at[19, f'Value'])
        
        # 50% do lucro acumulado, se faz pelas somas da reserva de lucros, reserva legal e lucros acumulados subtrai prejuizo acumulado e divide pela metade
        economia2019_copy.at[22, f'Value'] = ((economia2019_copy.at[5, f'Value'] + economia2019_copy.at[6, f'Value'] + economia2019_copy.at[12, f'Value']) - economia2019_copy.at[10, f'Value']) * 0.5
        if retirarMulta == True:
            #Calculo  do valor da DARF( Soma o valor de IRRF mas 20 % do mesmo, em cenarios em que nao se retira a multa)            
            economia2019_copy.at[23, f'Value'] = economia2019_copy.at[19, f'Value'] + (economia2019_copy.at[19, f'Value'] * 0.2 * 0)
        else:
            economia2019_copy.at[23, f'Value'] = economia2019_copy.at[19, f'Value'] + (economia2019_copy.at[19, f'Value'] * 0.2)    

        # Valor de economia gerada( Subtrir a redução no IRPJ pelo valor de DARF)
        economia2019_copy.at[25, f'Value'] = economia2019_copy.at[24, f'Value'] - economia2019_copy.at[23, f'Value']
        
        economia2019_copy[f'Value'] = round(economia2019_copy[f'Value'],2)
    else:
        economia2019_copy.at[18, f'Value'] = 0
        economia2019_copy.at[19, f'Value'] = 0     
        economia2019_copy.at[20, f'Value'] = 0
        economia2019_copy.at[22, f'Value'] = 0
                    
        economia2019_copy.at[23, f'Value'] = 0
        economia2019_copy.at[24, f'Value'] = 0

        economia2019_copy.at[25, f'Value'] = 0
        economia2019_copy.at[21, f'Value'] = 0

        economia2019_copy[f'Value'] = round(economia2019_copy[f'Value'],2)

        
    economia2019 = economia2019_copy

    return economia2019


def reCalculandoTrimestral(economia2019: pd.DataFrame,retirarMulta: bool)-> pd.DataFrame:
    #'''Função de callback para recalcular os valores apresentados e gerados para análise trimestral do JCP'''
    trimestres = [1,2,3,4]
    for i in trimestres:
        
        economia2019_copy = economia2019.copy() 
        
        economia2019_copy.at[14, f'Value {i}º Trimestre'] = np.sum([economia2019_copy.at[1, f'Value {i}º Trimestre'],economia2019_copy.at[2, f'Value {i}º Trimestre'],economia2019_copy.at[3, f'Value {i}º Trimestre'],
                                                                    economia2019_copy.at[4, f'Value {i}º Trimestre'],economia2019_copy.at[5, f'Value {i}º Trimestre'],
                                                                    economia2019_copy.at[6, f'Value {i}º Trimestre'],economia2019_copy.at[7, f'Value {i}º Trimestre'],economia2019_copy.at[8, f'Value {i}º Trimestre'],
                                                                    economia2019_copy.at[9, f'Value {i}º Trimestre'],economia2019_copy.at[11, f'Value {i}º Trimestre'],
                                                                    economia2019_copy.at[12, f'Value {i}º Trimestre'],economia2019_copy.at[13, f'Value {i}º Trimestre']]) - economia2019_copy.at[10, f'Value {i}º Trimestre']

        #Calculando Total Para Fins de JSPC  -- 
        economia2019_copy.at[15, f'Value {i}º Trimestre'] = sum([economia2019_copy.at[1, f'Value {i}º Trimestre'], economia2019_copy.at[2, f'Value {i}º Trimestre'], 
                                                            economia2019_copy.at[3, f'Value {i}º Trimestre'], economia2019_copy.at[5, f'Value {i}º Trimestre'],economia2019_copy.at[6, f'Value {i}º Trimestre'],
                                                            economia2019_copy.at[12, f'Value {i}º Trimestre'],economia2019_copy.at[13, f'Value {i}º Trimestre']])-economia2019_copy.at[10, f'Value {i}º Trimestre']
        
        #Veriricação se o valor de JSCP e negativo para ser a conta caso positivo
        if economia2019_copy.at[15, f'Value {i}º Trimestre'] > 0 and economia2019_copy.at[9, f'Operation {i}º Trimestre'] == 'Lucro do Período ' :
            economia2019_copy.at[16, f'Value {i}º Trimestre'] = economia2019_copy.at[15, f'Value {i}º Trimestre'] - economia2019_copy.at[0,f'Value {i}º Trimestre']
        else:
            economia2019_copy.at[16, f'Value {i}º Trimestre'] = 0.0
        
        if economia2019_copy.at[15, f'Value {i}º Trimestre'] or economia2019_copy.at[16, f'Value {i}º Trimestre'] > 0:

            #Calculando o Valor de JSCP(Valor da base multiplicado pela TJLP)
            economia2019_copy.at[18, f'Value {i}º Trimestre'] = economia2019_copy.at[16, f'Value {i}º Trimestre'] * (economia2019_copy.at[17, f'Value {i}º Trimestre'] / 100)
            
            #Valor do IRRF (Multiplica o valor de JSCP por 15%)
            economia2019_copy.at[19, f'Value {i}º Trimestre'] = economia2019_copy.at[18, f'Value {i}º Trimestre'] * 0.15       
            
            # Valor de JSCP a apropriar pelo cliente( subtrair o valor de JSCP por pelo valor do IRRF )
            economia2019_copy.at[20, f'Value {i}º Trimestre'] = abs(economia2019_copy.at[18, f'Value {i}º Trimestre'] - economia2019_copy.at[19, f'Value {i}º Trimestre'])
            
            # 50% do lucro acumulado, se faz pelas somas da reserva de lucros, reserva legal e lucros acumulados subtrai prejuizo acumulado e divide pela metade
            economia2019_copy.at[22, f'Value {i}º Trimestre'] = ((economia2019_copy.at[5, f'Value {i}º Trimestre'] + economia2019_copy.at[6, f'Value {i}º Trimestre'] + economia2019_copy.at[12, f'Value {i}º Trimestre']) - economia2019_copy.at[10, f'Value {i}º Trimestre']) * 0.5
            if retirarMulta == True:
                #Calculo  do valor da DARF( Soma o valor de IRRF mas 20 % do mesmo, em cenarios em que nao se retira a multa)            
                economia2019_copy.at[23, f'Value {i}º Trimestre'] = economia2019_copy.at[19, f'Value {i}º Trimestre'] + (economia2019_copy.at[19, f'Value {i}º Trimestre'] * 0.2 * 0)
            else:
                economia2019_copy.at[23, f'Value {i}º Trimestre'] = economia2019_copy.at[19, f'Value {i}º Trimestre'] + (economia2019_copy.at[19, f'Value {i}º Trimestre'] * 0.2)    
            #Valor do imposto 
            if economia2019_copy.at[24, f'Operation {i}º Trimestre'] == 'REDUÇÃO NO IRPJ/CSLL - 0.34%':
                economia2019_copy.at[24, f'Value {i}º Trimestre'] = economia2019_copy.at[18, f'Value {i}º Trimestre'] * 0.34
            else:
                economia2019_copy.at[24, f'Value {i}º Trimestre'] = economia2019_copy.at[18, f'Value {i}º Trimestre'] * 0.24   

            # Valor de economia gerada( Subtrir a redução no IRPJ pelo valor de DARF)
            economia2019_copy.at[25, f'Value {i}º Trimestre'] = economia2019_copy.at[24, f'Value {i}º Trimestre'] - economia2019_copy.at[23, f'Value {i}º Trimestre']
            
            economia2019_copy[f'Value {i}º Trimestre'] = round(economia2019_copy[f'Value {i}º Trimestre'],2)
        else:
            economia2019_copy.at[18, f'Value {i}º Trimestre'] = 0
            economia2019_copy.at[19, f'Value {i}º Trimestre'] = 0     
            economia2019_copy.at[20, f'Value {i}º Trimestre'] = 0
            economia2019_copy.at[22, f'Value {i}º Trimestre'] = 0
                        
            economia2019_copy.at[23, f'Value {i}º Trimestre'] = 0

            economia2019_copy.at[24, f'Value {i}º Trimestre'] = 0

            economia2019_copy.at[25, f'Value {i}º Trimestre'] = 0
            economia2019_copy.at[21, f'Value {i}º Trimestre'] = 0

            economia2019_copy[f'Value {i}º Trimestre'] = round(economia2019_copy[f'Value {i}º Trimestre'],2)

        
        economia2019 = economia2019_copy

    return economia2019


def criandoVisualizacao(trimestre: list, ano: int,
                         anoDeAnalise: bool, dataframesParaDownload: pd.DataFrame, cnpj_selecionado:str,tabelaParaRelatorio:str):

    #'''Cria visualizaçãos dos widgets e tabelas'''
    st.subheader(anoDeAnalise)

    periodoDeAnalise = st.toggle('', key=f"teste{anoDeAnalise}")

    session_cnpj_key = f'cnpj_selecionado_{anoDeAnalise}'

    if periodoDeAnalise:

        st.write(ano) 
        session_state_name = f"economia{anoDeAnalise}"
        #Funções de callbacks para análise trimestral, lógica e igual a do anual , porém com o trimestral, a função de callback faz um loop para iterar sobre cada trimestre
        if session_state_name not in st.session_state or st.session_state.get(session_cnpj_key, None) != cnpj_selecionado:
            economia2019 = controler.queryResultadoFinal(cnpj_selecionado, "resultadosjcp", anoDeAnalise).iloc[:, [3,2,4]].set_index('index').sort_values(by='index')
            st.session_state[session_state_name] = economia2019
        
        st.session_state[session_cnpj_key] = cnpj_selecionado
        
        with st.form(f"my_form{anoDeAnalise}{ano}"):

            multa = st.toggle('Retirar multa', key=f'{anoDeAnalise}')

            economia2019_data_editor = st.data_editor(st.session_state[session_state_name], key=f'{anoDeAnalise}deano', height=1000, use_container_width=True)
            submitted = st.form_submit_button(f"Atualizar {anoDeAnalise}")

        if submitted:
            if 'form_submit' not in st.session_state or not st.session_state.form_submit:
                st.session_state[session_state_name] = reCalculandoAno(economia2019_data_editor, multa)
                st.session_state.form_submit = True
            else:
                st.session_state.form_submit = False

        if st.button('Salvar alterações',key=f'{cnpj_selecionado,anoDeAnalise}'):
            with st.spinner('Salvando alterações...'):
                controler.update_table('resultadosjcp', economia2019_data_editor, cnpj_selecionado, anoDeAnalise)    
                st.success('Dados atualizados')
    


        #======== --- Tbaelas Lacs e Lalur Aós inovações

        with st.expander('Lacs Lalur'):
            session_state_lacs = f"economia_{anoDeAnalise}_lacslalurAnual"

            st.session_state[session_cnpj_key] = cnpj_selecionado

         
            if session_state_lacs not in st.session_state or st.session_state.get(session_state_lacs) is None or not st.session_state[session_state_lacs].equals(lacslalur.gerandoTabelas(cnpj_selecionado, anoDeAnalise)):
               
                lacslaurAno = lacslalur.gerandoTabelas(cnpj_selecionado, anoDeAnalise)
                st.session_state[session_state_lacs] = lacslaurAno

            with st.form(f"{anoDeAnalise}__===__{trimestre}"):

                lacslalur_data_editor = st.data_editor(st.session_state[session_state_lacs], key=f'data_{anoDeAnalise}', height=800, use_container_width=True)
    
                submittedbutton1 = st.form_submit_button(f"Recalcular Tabela {anoDeAnalise}")


            if submittedbutton1:

                updated_lacslalur = lacslalur.CallBack_LacsLalurAposInovacoesCalculos(lacslalur_data_editor)

                st.session_state[session_state_lacs] = updated_lacslalur
                
                lacslaurAno = updated_lacslalur

                st.write("Tabela recalculada com sucesso!")
                st.dataframe(lacslaurAno)



        ## ---- Tabelas comparativas Lacs e Lalur antes e após inovações do período anual
        

        lacslalurOrignal = lacslalur.tabelaComparativaLacsLalurAno(cnpj_selecionado,anoDeAnalise).iloc[[15,36],[3,2]].reset_index(drop='index')
        
        try:
            
            aposInovacoesLacslalur = lacslaurAno.iloc[[10,31],:]
        except:
            aposInovacoesLacslalur = lacslalur_data_editor.iloc[[10,31],:]

        tabelaComparativa = pd.concat([lacslalurOrignal,aposInovacoesLacslalur]).reset_index(drop='index')

        tabelaComparativa.at[2,f'Operation'] = 'Subtotal CSLL  Após Inovações'
        tabelaComparativa.at[3,f'Operation'] = 'Sub total IRPJ Após Inovações'
        tabelaComparativa.at[4,f'Operation'] = ''
        tabelaComparativa.at[5,f'Operation'] = 'Comparativo CSLL'
        tabelaComparativa.at[6,f'Operation'] = 'Comparativo IRPJ'
        tabelaComparativa.at[7,f'Operation'] = ''
        tabelaComparativa.at[8,f'Operation'] = ''       
        
        
        tabelaComparativa.at[5,'Value'] = tabelaComparativa.at[0,'Value'] - tabelaComparativa.at[2,'Value'] 
        tabelaComparativa.at[6,'Value'] = tabelaComparativa.at[1,'Value'] - tabelaComparativa.at[3,'Value'] 
        
        totalCSLL = round(np.sum([tabelaComparativa.at[5,f'Value'],
                            tabelaComparativa.at[5,f'Value'],
                            tabelaComparativa.at[5,f'Value'],
                            tabelaComparativa.at[5,f'Value']]),2)
        
        totalIRPJ = round(np.sum([tabelaComparativa.at[6,f'Value'],
                            tabelaComparativa.at[6,f'Value'],
                            tabelaComparativa.at[6,f'Value'],
                            tabelaComparativa.at[6,f'Value']]),2)
        
        with st.expander('Tabela Comparativa'):
            totalCSLL_formatted = "{:,.2f}".format(totalCSLL)
            totalIRPJ_formatted = "{:,.2f}".format(totalIRPJ)
            tabelaComparativa = tabelaComparativa.reindex([0,2,4,5,8,1,3,7,6])
            st.dataframe(tabelaComparativa,key=anoDeAnalise)
            st.metric(label=f'Total CSLL {anoDeAnalise}: ', value=totalCSLL_formatted)
            st.metric(label=f'Total IRPJ {anoDeAnalise}: ', value=totalIRPJ_formatted)

    
        
        #Tabelas para gerar o relatorio fiscal
        tabelaRelatorio = economia2019_data_editor.copy()
        tabelaRelatorio = tabelaRelatorio.iloc[24:,:].reset_index(drop='index')
        tabelaRelatorio = tabelaRelatorio.drop(columns='Operation')
        tabelaRelatorio.columns = [f"{col}_{anoDeAnalise}" for col in tabelaRelatorio.columns]

        #Tabela para exportação em excel

        resultadoAnual = economia2019_data_editor.copy()
        try:
            dfParaDownloadFinal = pd.concat([resultadoAnual,lacslaurAno,tabelaComparativa])
        except:
            dfParaDownloadFinal = pd.concat([resultadoAnual,lacslalur_data_editor,tabelaComparativa]) 
        dfParaDownloadFinal.columns = [f"{col}_{anoDeAnalise}" for col in dfParaDownloadFinal.columns]
        dfParaDownloadFinal = dfParaDownloadFinal.drop([4,5,6,7,15,20]).reset_index(drop='index')


    else:
        #Exibição e logica de callbacks tabela principal
        st.write(trimestre) 
        session_state_name = f"economia{anoDeAnalise}Trimestral"
        #Funções de callbacks para análise trimestral, lógica e igual a do anual , porém com o trimestral, a função de callback faz um loop para iterar sobre cada trimestre
        if session_state_name not in st.session_state or st.session_state.get(session_cnpj_key, None) != cnpj_selecionado:
            economia2019Trimestral = controler.queryResultadoFinalTrimestral(cnpj_selecionado, "resultadosjcptrimestral", anoDeAnalise).iloc[:, [2,3,4,5,6,7,8,9,10]].set_index('index').sort_values(by='index')
            st.session_state[session_state_name] = economia2019Trimestral
        st.session_state[session_cnpj_key] = cnpj_selecionado
        
        with st.form(f"{anoDeAnalise}{trimestre}"):

            multa = st.toggle('Retirar multa', key=f'{anoDeAnalise}')


            economia2019Trimestral_data_editor = st.data_editor(st.session_state[session_state_name], key=f'data_editor_{anoDeAnalise}', height=1000, use_container_width=True)
            submittedbutton1 = st.form_submit_button(f"Atualizar {anoDeAnalise}")

        if submittedbutton1:
            if 'form_submitted' not in st.session_state or not st.session_state.form_submitted:
                st.session_state[session_state_name] = reCalculandoTrimestral(economia2019Trimestral_data_editor, multa)
                st.session_state.form_submitted = True
            else:
                st.session_state.form_submitted = False
        
        
        if st.button('Salvar Alterações',key=f'{cnpj_selecionado,anoDeAnalise}'):
            with st.spinner('Salvando alterações...'):
                controler.update_table_trimestral('resultadosjcptrimestral', economia2019Trimestral_data_editor, cnpj_selecionado, anoDeAnalise)    
                st.success('Dados atualizados')

        #### ---- Lacs e Lalur após inovações editavel 
        with st.expander('Lacs Lalur'):
            session_state_lacs = f"economia_{anoDeAnalise}_lacslalur"

            st.session_state[session_cnpj_key] = cnpj_selecionado

         
            if session_state_lacs not in st.session_state or st.session_state.get(session_state_lacs) is None or not st.session_state[session_state_lacs].equals(lacslalur.gerandoTabelasTrimestral(cnpj_selecionado, anoDeAnalise)):
               
                lacslalurTrimestral = lacslalur.gerandoTabelasTrimestral(cnpj_selecionado, anoDeAnalise)
                st.session_state[session_state_lacs] = lacslalurTrimestral

            with st.form(f"{anoDeAnalise}__===__{trimestre}"):

                lacslalurTrimestral_data_editor = st.data_editor(st.session_state[session_state_lacs], key=f'data_{anoDeAnalise}', height=800, use_container_width=True)
    
                submittedbutton1 = st.form_submit_button(f"Recalcular Tabela {anoDeAnalise}")


            if submittedbutton1:

                updated_lacslalur = lacslalur.LacsLalurAposInovacoesTrimestralCallback(lacslalurTrimestral_data_editor)

                st.session_state[session_state_lacs] = updated_lacslalur
                
                lacslalurTrimestral = updated_lacslalur

                st.write("Tabela recalculada com sucesso!")
                st.dataframe(lacslalurTrimestral)

        ####---- Tabela Comparativa Lacs e Lalur antes e apos Inovações 
        lacslalurOrignal = lacslalur.tabelaComparativaLacsLalur(cnpj_selecionado,anoDeAnalise).iloc[[10,32],2:].reset_index(drop='index')

        try:
            aposInovacoesLacslalur = lacslalurTrimestral.iloc[[12,32],:]
        except:
            aposInovacoesLacslalur = lacslalur.gerandoTabelasTrimestral(cnpj_selecionado, anoDeAnalise).iloc[[12,32],:]
        
        tabelaComparativa = pd.concat([lacslalurOrignal,aposInovacoesLacslalur]).reset_index(drop='index')
        

        tabelaComparativa.at[2,f'Operation 1º Trimestre'] = 'Subtotal CSLL  Após Inovações'
        tabelaComparativa.at[3,f'Operation 1º Trimestre'] = 'Sub total IRPJ Após Inovações'
        tabelaComparativa.at[4,f'Operation 1º Trimestre'] = ''
        tabelaComparativa.at[5,f'Operation 1º Trimestre'] = 'Comparativo CSLL'
        tabelaComparativa.at[6,f'Operation 1º Trimestre'] = 'Comparativo IRPJ'
        tabelaComparativa.at[7,f'Operation 1º Trimestre'] = ''
        tabelaComparativa.at[8,f'Operation 1º Trimestre'] = ''
        tabelaComparativa.drop(columns=['Operation 2º Trimestre','Operation 3º Trimestre','Operation 4º Trimestre'],inplace=True)
            
        
        for i in [1,2,3,4]:
            tabelaComparativa.at[5,f'Value {i}º Trimestre'] = tabelaComparativa.at[0,f'Value {i}º Trimestre'] - tabelaComparativa.at[2,f'Value {i}º Trimestre'] 
            tabelaComparativa.at[6,f'Value {i}º Trimestre'] = tabelaComparativa.at[1,f'Value {i}º Trimestre'] - tabelaComparativa.at[3,f'Value {i}º Trimestre'] 
        
        totalCSLL = round(np.sum([tabelaComparativa.at[5,f'Value 1º Trimestre'],
                            tabelaComparativa.at[5,f'Value 2º Trimestre'],
                            tabelaComparativa.at[5,f'Value 3º Trimestre'],
                            tabelaComparativa.at[5,f'Value 4º Trimestre']]),2)
        totalIRPJ = round(np.sum([tabelaComparativa.at[6,f'Value 1º Trimestre'],
                            tabelaComparativa.at[6,f'Value 2º Trimestre'],
                            tabelaComparativa.at[6,f'Value 3º Trimestre'],
                            tabelaComparativa.at[6,f'Value 4º Trimestre']]),2)
        
        with st.expander('Tabela Comparativa'):
            totalCSLL_formatted = "{:,.2f}".format(totalCSLL)
            totalIRPJ_formatted = "{:,.2f}".format(totalIRPJ)
            tabelaComparativa = tabelaComparativa.reindex([0,2,4,5,8,1,3,7,6])
            st.dataframe(tabelaComparativa)
            st.metric(label=f'Total CSLL {anoDeAnalise}: ', value=totalCSLL_formatted)
            st.metric(label=f'Total IRPJ {anoDeAnalise}: ', value=totalIRPJ_formatted)


        tabelaRelatorioTri = economia2019Trimestral_data_editor.copy()
        tabelaRelatorioTri = tabelaRelatorioTri.iloc[24:,[0,1,3,5,7]].reset_index(drop='index')
        
        tabelaRelatorioTri[f'Value_{anoDeAnalise}'] = sum([tabelaRelatorioTri.at[1,'Value 1º Trimestre'],tabelaRelatorioTri.at[1,'Value 2º Trimestre'],
                                                        tabelaRelatorioTri.at[1,'Value 3º Trimestre'],tabelaRelatorioTri.at[1,'Value 4º Trimestre']])
        
        tabelaRelatorioTri.at[0,f'Value_{anoDeAnalise}'] = sum([tabelaRelatorioTri.at[0,'Value 1º Trimestre'],tabelaRelatorioTri.at[0,'Value 2º Trimestre'],
                                                        tabelaRelatorioTri.at[0,'Value 3º Trimestre'],tabelaRelatorioTri.at[0,'Value 4º Trimestre']])
        
        tabelaRelatorioTri = tabelaRelatorioTri.iloc[:,5].reset_index(drop='index')
        resultaTrimestral = economia2019Trimestral_data_editor
        try:
            dfParaDownloadFinaltrimestral = pd.concat([resultaTrimestral,lacslalurTrimestral,tabelaComparativa])
        except:
            dfParaDownloadFinaltrimestral = pd.concat([resultaTrimestral,lacslalur.gerandoTabelasTrimestral(cnpj_selecionado, anoDeAnalise),tabelaComparativa]) 

        
        dfParaDownloadFinaltrimestral.columns = [f"{col}_{anoDeAnalise}" for col in dfParaDownloadFinaltrimestral.columns]
        dfParaDownloadFinaltrimestral = dfParaDownloadFinaltrimestral.reset_index(drop='index')

    if periodoDeAnalise == True:
        dataframesParaDownload.append(dfParaDownloadFinal)
        tabelaParaRelatorio.append(tabelaRelatorio)
    else:
         dataframesParaDownload.append(dfParaDownloadFinaltrimestral)
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







