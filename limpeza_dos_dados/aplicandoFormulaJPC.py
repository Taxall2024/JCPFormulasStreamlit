import pandas as pd
import streamlit as st
import numpy as np


from baseJPC.tratamentosDosDadosParaCalculo import FiltrandoDadosParaCalculo
from baseJPC.trimestralTramentoECalculos import trimestralFiltrandoDadosParaCalculo
from arquivosSPED.pipeArquivosECF import SpedProcessor
from calculosAnual import Calculo
from db.controllerDB import dbController


import functools
import time
import base64
import psutil

controler = dbController('ECF')
st.set_page_config(layout="wide")
start_time = time.time()
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

def LacsLalurAposInovacoes(dataframe):
            lacsLalurAposInovacoesDF = pd.DataFrame(dataframe)
            ganbiarraParaPegarPrejuizoIRPJ = lacsLalurAposInovacoesDF.loc[12].to_frame().T
            lacsLalurAposInovacoesDF = lacsLalurAposInovacoesDF.drop([8,9,10,11,12,13,19,24]).reset_index(drop='index').iloc[[2,1,0,7,3,4,6,8,9,10,11,
                                                                                                    12,5,15,16,18,19,20,21,22,
                                                                                                    23,24,25,26,27,28,29],:].reset_index(drop='index')
            #Calculo das exclusoes, (Adicionando valor de JCP)
            lacsLalurAposInovacoesDF.at[2,'Value'] = lacsLalurAposInovacoesDF.at[2,'Value'] + lacsLalurAposInovacoesDF.at[3,'Value']
            #Calculo da base CSLL
            lacsLalurAposInovacoesDF.at[4,'Value'] = (lacsLalurAposInovacoesDF.at[0,'Value'] + lacsLalurAposInovacoesDF.at[1,'Value']) - lacsLalurAposInovacoesDF.at[2,'Value']
            #Calclulo da Base de Calculo CSLL
            lacsLalurAposInovacoesDF.at[6,'Value'] = lacsLalurAposInovacoesDF.at[4,'Value'] + lacsLalurAposInovacoesDF.at[5,'Value']
            #Calclulo do valor  CSLL
            if lacsLalurAposInovacoesDF.at[6,'Value'] > 0 :
                lacsLalurAposInovacoesDF.at[7,'Value'] = lacsLalurAposInovacoesDF.at[6,'Value'] * 0.09
            else:
                0    
            #Calculando Subtotal CSLL Recolher
            lacsLalurAposInovacoesDF.at[11,'Value'] = lacsLalurAposInovacoesDF.at[7,'Value'] - lacsLalurAposInovacoesDF.at[8,'Value'] - lacsLalurAposInovacoesDF.at[9,'Value'] - lacsLalurAposInovacoesDF.at[10,'Value']                
            #Calculo Base IRPJ
            lacsLalurAposInovacoesDF.at[12,'Value'] = lacsLalurAposInovacoesDF.at[0,'Value'] - lacsLalurAposInovacoesDF.at[7,'Value']

            #Calculo Base de Calculo IRPJ
            lacsLalurAposInovacoesDF.at[27,'Value'] = lacsLalurAposInovacoesDF.at[12,'Value'] + lacsLalurAposInovacoesDF.at[13,'Value'] -lacsLalurAposInovacoesDF.at[2,'Value']
            lacsLalurAposInovacoesDF.at[27,'Operation'] = 'Base de calculo IRPJ'
            #Calculo Lucro Real IRPJ
            #lacsLalurAposInovacoesDF = pd.concat([lacsLalurAposInovacoesDF ,ganbiarraParaPegarPrejuizoIRPJ],ignore_index=True).reset_index(drop='index')
            lacsLalurAposInovacoesDF.at[15,'Value'] = lacsLalurAposInovacoesDF.at[4,'Value'] #- lacsLalurAposInovacoesDF.at[28,'Value']
            #Calculo valor do IRPJ
            #lacsLalurAposInovacoesDF.at[16,'Value'] = lacsLalurAposInovacoesDF.at[15,'Value'] * 0.15
            lacsLalurAposInovacoesDF.at[16,'Value'] = np.where(lacsLalurAposInovacoesDF.at[15,'Value']>0,
                                                                lacsLalurAposInovacoesDF.at[15,'Value'] * 0.15,0)
            

            #Calculo valor do IRPJ Adicional
            lacsLalurAposInovacoesDF.at[17,'Value'] = np.where(lacsLalurAposInovacoes.at[15,'Value']< 240000,
                                                                (lacsLalurAposInovacoesDF.at[15,'Value'] - 240000)*0.1,0)

            #Calculo Total Devido IRPJ
            lacsLalurAposInovacoesDF.at[18,'Value'] = lacsLalurAposInovacoesDF.at[16,'Value'] + lacsLalurAposInovacoesDF.at[17,'Value']
            #Calculo PAT
            lacsLalurAposInovacoesDF.at[19,'Value'] = lacsLalurAposInovacoesDF.at[16,'Value'] * 0.04
            #Sub total IRPJ a recolher
            lacsLalurAposInovacoesDF.at[28,'Value'] = (lacsLalurAposInovacoesDF.at[18,'Value']-
                                                            lacsLalurAposInovacoesDF.at[19,'Value']-
                                                            lacsLalurAposInovacoesDF.at[20,'Value']-
                                                            lacsLalurAposInovacoesDF.at[21,'Value']-
                                                                lacsLalurAposInovacoesDF.at[22,'Value']-
                                                                lacsLalurAposInovacoesDF.at[23,'Value']-
                                                                lacsLalurAposInovacoesDF.at[24,'Value']-
                                                                    lacsLalurAposInovacoesDF.at[25,'Value']-
                                                                    lacsLalurAposInovacoesDF.at[26,'Value'])
            lacsLalurAposInovacoesDF.at[28,'Operation'] = 'Sub total IRPJ a Recolher'                                                  
            return lacsLalurAposInovacoesDF                      

def LacsLalurAposInovacoesTrimestral(dataframe,resultJSCP):
    df = pd.concat([dataframe,resultJSCP]).reset_index(drop='index')
    df = df.iloc[[1,2,3,34,4,5,6,7,9,10,11,12,15,13,14,18,19,20,
                    21,22,23,24,25,26,27,28,29,30,31,32,33,],:]
    #Calculo exclusoes
    df.at[3,'Value'] = df.at[3,'Value'] + df.at[34,'Value'] 
    #Calculo Base 
    df.at[4,'Value'] = df.at[2,'Value'] + df.at[1,'Value'] - df.at[3,'Value'] + df.at[1,'Value']
    #Calculo base CSLL
    df.at[6,'Value'] = df.at[4,'Value'] - df.at[5,'Value'] 
    #Valor CSLL
    df.at[7,'Value'] = np.where(df.at[6,'Value']>0,df.at[6,'Value']*0.09,0) 
    #Valor Sub total CSLL a Recolher
    df.at[11,'Value'] = df.at[7,'Value'] - df.at[9,'Value'] 
    #Valor Sub total Base IRPJ
    df.at[19,'Value'] = (df.at[13,'Value'] + df.at[14,'Value']+df.at[12,'Value']) - df.at[3,'Value']
    #Calculando Lucro Real
    df.at[21,'Value'] = df.at[19,'Value'] - df.at[20,'Value']
    #Valor IRPJ
    df.at[22,'Value'] = np.where(df.at[21,'Value']>0,df.at[21,'Value']*0.15,0) 
    #Valor IRPJ Adicionais
    df.at[23,'Value'] = np.where(df.at[21,'Value']>60000,(df.at[21,'Value']-60000)*0.10,0) 
    #Total devido IRPJ antes retenções
    df.at[24,'Value'] = df.at[22,'Value'] + df.at[23,'Value'] 
    #Total devido IRPJ antes retenções
    df.at[33,'Value'] = df.at[24,'Value'] - (df.at[25,'Value'] - df.at[26,'Value'] - df.at[27,'Value']
                                                -df.at[28,'Value'] - df.at[29,'Value']-df.at[30,'Value'] -
                                                    df.at[31,'Value']-df.at[32,'Value'])  
    df = df.reset_index(drop='index')
    df['Value'] =  df['Value'].apply(lambda x: "{:,.2f}".format(x).replace(',','_').replace('.',',').replace('_','.'))

    return df


class CalculosEProcessamentoDosDados():                    
    
    def filtrarCalcularECadastras(self,file_paths,file_path):        
        sped_processor = SpedProcessor(file_paths)
        nomeDaEmpresa = sped_processor.pegandoInfosDaEmpresa(file_path)  
        controler.inserirTabelas('cadastrodasempresas',nomeDaEmpresa)
        sped_processor.processar_arquivos()
        dfs_concatenados = sped_processor.concatenar_dfs()
        L100_final, L300_final, M300_final, M350_final, N630_final, N670_final = sped_processor.tratandoTiposDeDados(dfs_concatenados)


        cnpj = L100_final.loc[0,'CNPJ']

        controler.inserirTabelas('l100',L100_final)
        controler.inserirTabelas('l300',L300_final)
        controler.inserirTabelas('m300',M300_final)
        controler.inserirTabelas('m350',M350_final)
        controler.inserirTabelas('n630',N630_final)
        controler.inserirTabelas('n670',N670_final)

        uploaded_file_l100 = controler.get_data_by_cnpj(f"{cnpj}","l100")
        uploaded_file_l300 = controler.get_data_by_cnpj(f"{cnpj}","l300")
        uploaded_file_lacs = controler.get_data_by_cnpj(f"{cnpj}","m350")
        uploaded_file_lalur = controler.get_data_by_cnpj(f"{cnpj}","m300")
        uploaded_file_ecf670 = controler.get_data_by_cnpj(f"{cnpj}","n670")
        uploaded_file_ec630 = controler.get_data_by_cnpj(f"{cnpj}","n630")

       
        filtrando_dados = FiltrandoDadosParaCalculo(
                    data=None,
                    lacs_file=uploaded_file_lacs,
                    lalur_file=uploaded_file_lalur,
                    ecf670_file=uploaded_file_ecf670,
                    ec630_file=uploaded_file_ec630,
                    l100_file=uploaded_file_l100,
                    l300_file=uploaded_file_l300
                )
                
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
                    
   
        
        economiaPorAno = []
        dataFrameParaExportar1 = []
        dataFrameParaExportar2 = []
        dataFrameParaExportar3 = []

        df = pd.DataFrame(columns=['Operation','Value'])
                                


        calculosIniciais_2019 = calculos2019.runPipe()
        tabelaFinal_2019 = calculos2019.runPipeFinalTable()
        resultadoTotal_2019 = calculos2019.pipeCalculo('2019')
        economiaPorAno.append(resultadoTotal_2019)
        dataFrameParaExportar1.append(calculosIniciais_2019)
        dataFrameParaExportar2.append(tabelaFinal_2019)
        dataFrameParaExportar3.append(resultadoTotal_2019)
                                 

        calculosIniciais_2020 = calculos2020.runPipe()
        tabelaFinal_2020 = calculos2020.runPipeFinalTable()
        resultadoTotal_2020 = calculos2020.pipeCalculo('2020')
        economiaPorAno.append(resultadoTotal_2020)
        dataFrameParaExportar1.append(calculosIniciais_2020)
        dataFrameParaExportar2.append(tabelaFinal_2020)
        dataFrameParaExportar3.append(resultadoTotal_2020)


        calculosIniciais_2021 = calculos2021.runPipe()
        tabelaFinal_2021 = calculos2021.runPipeFinalTable()
        resultadoTotal_2021 = calculos2021.pipeCalculo('2021')
        economiaPorAno.append(resultadoTotal_2021)
        dataFrameParaExportar1.append(calculosIniciais_2021)
        dataFrameParaExportar2.append(tabelaFinal_2021)
        dataFrameParaExportar3.append(resultadoTotal_2021)
                                

        calculosIniciais_2022 = calculos2022.runPipe()
        tabelaFinal_2022 = calculos2022.runPipeFinalTable()
        resultadoTotal_2022 = calculos2022.pipeCalculo('2022')
        economiaPorAno.append(resultadoTotal_2022)
        dataFrameParaExportar1.append(calculosIniciais_2022)
        dataFrameParaExportar2.append(tabelaFinal_2022)
        dataFrameParaExportar3.append(resultadoTotal_2022)
        

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
                                
        jcp2019 = pd.concat([calculosIniciais_2019,tabelaFinal_2019,resultadoTotal_2019],axis=0).reset_index(drop='index')
        jcp2020 = pd.concat([calculosIniciais_2020,tabelaFinal_2020,resultadoTotal_2020],axis=0).reset_index(drop='index')
        jcp2021 = pd.concat([calculosIniciais_2021,tabelaFinal_2021,resultadoTotal_2021],axis=0).reset_index(drop='index')
        jcp2022 = pd.concat([calculosIniciais_2022,tabelaFinal_2022,resultadoTotal_2022],axis=0).reset_index(drop='index')
        jcp2023 = pd.concat([calculosIniciais_2023,tabelaFinal_2023,resultadoTotal_2023],axis=0).reset_index(drop='index')


        jcp2019['Value'] = jcp2019['Value'].astype(float)
        jcp2020['Value'] = jcp2020['Value'].astype(float)
        jcp2021['Value'] = jcp2021['Value'].astype(float)
        jcp2022['Value'] = jcp2022['Value'].astype(float)
        jcp2023['Value'] = jcp2023['Value'].astype(float)

        controler.inserirTabelasFinaisJCP('resultadosjcp',jcp2019)
        controler.inserirTabelasFinaisJCP('resultadosjcp',jcp2020)
        controler.inserirTabelasFinaisJCP('resultadosjcp',jcp2021)
        controler.inserirTabelasFinaisJCP('resultadosjcp',jcp2022)
        controler.inserirTabelasFinaisJCP('resultadosjcp',jcp2023)
                                



                            
        st.cache_data.clear()
        dataFrameParaExportarCSLL = []
        dataFrameParaExportarIRPJJ = []
        dfLacsLalur = pd.DataFrame(columns=['Operation','Value'])

        resultadoTotal_2019 = calculos2019.runPipeLacsLalurCSLL()
        resultadoTotal_2019IR = calculos2019.runPipeLacsLalurIRPJ()
        dataFrameParaExportarCSLL.append(resultadoTotal_2019)
        dataFrameParaExportarIRPJJ.append(resultadoTotal_2019IR)                         
                                
                            
        
        resultadoTotal_2020 = calculos2020.runPipeLacsLalurCSLL()
        resultadoTotal_2020IR = calculos2020.runPipeLacsLalurIRPJ()
        dataFrameParaExportarCSLL.append(resultadoTotal_2020)
        dataFrameParaExportarIRPJJ.append(resultadoTotal_2020IR)
                         
                            
        resultadoTotal_2021 = calculos2021.runPipeLacsLalurCSLL()
        resultadoTotal_2021IR = calculos2021.runPipeLacsLalurIRPJ()
        dataFrameParaExportarCSLL.append(resultadoTotal_2021)
        dataFrameParaExportarIRPJJ.append(resultadoTotal_2021IR)


        resultadoTotal_2022 = calculos2022.runPipeLacsLalurCSLL()
        resultadoTotal_2022IR = calculos2022.runPipeLacsLalurIRPJ()
        dataFrameParaExportarCSLL.append(resultadoTotal_2022)
        dataFrameParaExportarIRPJJ.append(resultadoTotal_2022IR)


        resultadoTotal_2023 = calculos2023.runPipeLacsLalurCSLL()
        resultadoTotal_2023IR = calculos2023.runPipeLacsLalurIRPJ()
        dataFrameParaExportarCSLL.append(resultadoTotal_2023)
        dataFrameParaExportarIRPJJ.append(resultadoTotal_2023IR)

        lacsLalur2019 = pd.concat([resultadoTotal_2019,resultadoTotal_2019IR]).reset_index(drop='index')
        lacsLalur2020 = pd.concat([resultadoTotal_2020,resultadoTotal_2020IR]).reset_index(drop='index')
        lacsLalur2021 = pd.concat([resultadoTotal_2021,resultadoTotal_2021IR]).reset_index(drop='index')
        lacsLalur2022 = pd.concat([resultadoTotal_2022,resultadoTotal_2022IR]).reset_index(drop='index')
        lacsLalur2023 = pd.concat([resultadoTotal_2023,resultadoTotal_2023IR]).reset_index(drop='index') 

        lacsLalur2019['Value'] = lacsLalur2019['Value'].astype(float)
        lacsLalur2020['Value'] = lacsLalur2020['Value'].astype(float)
        lacsLalur2021['Value'] = lacsLalur2021['Value'].astype(float)
        lacsLalur2022['Value'] = lacsLalur2022['Value'].astype(float)
        lacsLalur2023['Value'] = lacsLalur2023['Value'].astype(float) 

        controler.inserirTabelasFinaisJCP('lacslalur',lacsLalur2019)
        controler.inserirTabelasFinaisJCP('lacslalur',lacsLalur2020)
        controler.inserirTabelasFinaisJCP('lacslalur',lacsLalur2021)
        controler.inserirTabelasFinaisJCP('lacslalur',lacsLalur2022)
        controler.inserirTabelasFinaisJCP('lacslalur',lacsLalur2023)

        st.cache_data.clear()

                        

        colunas = st.columns(4)
        trimestres = ['1º Trimestre', '2º Trimestre', '3º Trimestre', '4º Trimestre']
        economia_gerada_por_trimestre = []
        arquivoFinalParaExportacaoTri = []
        tabelaUnicaLista = []
        for ano in range(2019, 2024):
                lacsLalurApos = []
                year_dfsLacs = []
                resultadoJCP = []
                resultadoDedu = []
                economiaGerada = []
                tabelaUnica = []
                tabelaUnicaLacsLalurAposInocacoes = []
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

                        resultJSCP = lacs.dfLacsLalurApos
                        lacs.LacsLalurTrimestral.trimestralLacsLalurAposInovacoesFn()
                        
                        df = lacs.LacsLalurTrimestral.triLacsLalurFinal
                        df = LacsLalurAposInovacoesTrimestral(df,resultJSCP)



                        df.columns = [f"{col} {trimestre}" for col in df.columns] 
                        lacsLalurApos.append(df)




                dfCalculos = pd.concat(year_dfsLacs, axis=1)
                tabelaJCP = pd.concat(resultadoJCP, axis=1)
                limiteDedutibili = pd.concat(resultadoDedu, axis=1)
                economiaGerada = pd.concat(economiaGerada, axis=1)

                LacasLalurAposTrimestres = pd.concat(lacsLalurApos,axis=1)
                tabelaUnica = pd.concat([dfCalculos,tabelaJCP,limiteDedutibili,economiaGerada],axis=0)
                tabelaUnica['Ano'] = int(ano)
                tabelaUnica['CNPJ'] = cnpj
                controler.inserirTabelasFinaisJCP('resultadosjcptrimestral',tabelaUnica)

                tabelaUnicaLista.append(tabelaUnica.add_suffix(ano))
     
    
        arquivoFinalParaExportacaoTri = pd.concat(tabelaUnicaLista,axis=1, ignore_index=True)
        


        st.cache_data.clear()
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
            tabelaFinalLacsLalur['Ano'] = int(ano)
            tabelaFinalLacsLalur['CNPJ'] = cnpj
            tabelaFinalLacsLalur['Value 1º Trimestre'] = round(tabelaFinalLacsLalur['Value 1º Trimestre'].astype(float),2)
            tabelaFinalLacsLalur['Value 2º Trimestre'] = round(tabelaFinalLacsLalur['Value 2º Trimestre'].astype(float),2)
            tabelaFinalLacsLalur['Value 3º Trimestre'] = round(tabelaFinalLacsLalur['Value 3º Trimestre'].astype(float),2)
            tabelaFinalLacsLalur['Value 4º Trimestre'] = round(tabelaFinalLacsLalur['Value 4º Trimestre'].astype(float),2)
            controler.inserirTabelasFinaisJCP('lacslalurtrimestral',tabelaFinalLacsLalur)

            tabelaFinalLacsLalurUnificad.append(tabelaFinalLacsLalur.add_suffix(ano))
    
                
        arquivoFinalParaExportacaoTriLacs = pd.concat(tabelaFinalLacsLalurUnificad,axis=1)    
          
                
end_time = time.time()
execution_time = end_time - start_time



      
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

