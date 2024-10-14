import pandas as pd
import numpy as np
import streamlit as st

import sys
import os
import functools


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from db.controllerDB import dbController

class LacsLalurAposInovacoes(dbController):

    def __init__(self, banco):
        super().__init__(banco)


    def gerandoTabelas(self,cnpj,ano):

        tabelaLacsLalur = self.queryResultadoFinal(cnpj=cnpj,tabela='lacslalur',ano=ano)
        jcp = self.get_jcp_value(cnpj,'resultadosjcp',ano,"Valor do JSCP")
        tabelaFInal = pd.concat([tabelaLacsLalur,jcp]).reset_index(drop='index')
        lacs = self.get_all_data(tabela='m350')



        tabelaFInal2 = self.LacsLalurAposInovacoesCalculos(tabelaFInal)

        return tabelaFInal2
    
    def gerandoTabelasTrimestral(self, cnpj:str, ano:int) -> pd.DataFrame:
        tabelaLacsLalur = self.queryResultadoFinalTrimestral(cnpj=cnpj, tabela='lacslalurtrimestral', ano=ano)
        jcp = self.get_jcp_value_trimestral(cnpj, 'resultadosjcptrimestral', ano, "Valor do JSCP")
        tabelaFInal = pd.concat([tabelaLacsLalur, jcp]).reset_index(drop='index')
        tabelaFInal2 = self.LacsLalurAposInovacoesTrimestral(tabelaFInal)
        return (tabelaFInal2)

    def LacsLalurAposInovacoesCalculos(self,dataframe: pd.DataFrame)-> pd.DataFrame:
            lacsLalurAposInovacoesDF = pd.DataFrame(dataframe)
            ganbiarraParaPegarPrejuizoIRPJ = lacsLalurAposInovacoesDF.loc[12].to_frame().T

            lacsLalurAposInovacoesDF = lacsLalurAposInovacoesDF.reset_index(drop='index').iloc[[2,1,0,37,3,4,5,12,31,13,14,15,16,17,19,20,
                                                                                                21,22,23,24,25,26,27,28,29,30,31,32,
                                                                                                33,34,35,36],[3,2]].reset_index(drop='index')
            lacsLalurAposInovacoesDF.at[33,'Operation'] = ''
            # Calculo das exclusoes, (Adicionando valor de JCP)
            lacsLalurAposInovacoesDF.at[2,'Value'] = lacsLalurAposInovacoesDF.at[2,'Value'] + lacsLalurAposInovacoesDF.at[3,'Value']
            #Calculo da base CSLL
            lacsLalurAposInovacoesDF.at[4,'Value'] = (lacsLalurAposInovacoesDF.at[0,'Value'] + lacsLalurAposInovacoesDF.at[1,'Value']) - lacsLalurAposInovacoesDF.at[2,'Value']
            #Calclulo da Base de Calculo CSLL
            lacsLalurAposInovacoesDF.at[6,'Value'] = lacsLalurAposInovacoesDF.at[4,'Value'] - lacsLalurAposInovacoesDF.at[5,'Value']
            #Calclulo do valor  CSLL
            if lacsLalurAposInovacoesDF.at[6,'Value'] > 0 :
                lacsLalurAposInovacoesDF.at[7,'Value'] = lacsLalurAposInovacoesDF.at[6,'Value'] * 0.09
            else:
                0    
            #Calculando Subtotal CSLL Recolher
            lacsLalurAposInovacoesDF.at[12,'Value'] = lacsLalurAposInovacoesDF.at[7,'Value'] - lacsLalurAposInovacoesDF.at[9,'Value'] - lacsLalurAposInovacoesDF.at[10,'Value'] - lacsLalurAposInovacoesDF.at[11,'Value']                
            #Calculo Base IRPJ
            lacsLalurAposInovacoesDF.at[13,'Value'] = lacsLalurAposInovacoesDF.at[0,'Value'] - lacsLalurAposInovacoesDF.at[7,'Value']

            #Calculo Base de Calculo IRPJ
            lacsLalurAposInovacoesDF.at[27,'Value'] = lacsLalurAposInovacoesDF.at[13,'Value'] + lacsLalurAposInovacoesDF.at[14,'Value'] -lacsLalurAposInovacoesDF.at[2,'Value']
            #lacsLalurAposInovacoesDF.at[27,'Operation'] = 'Base de calculo IRPJ'
            #Calculo Lucro Real IRPJ
            #lacsLalurAposInovacoesDF = pd.concat([lacsLalurAposInovacoesDF ,ganbiarraParaPegarPrejuizoIRPJ],ignore_index=True).reset_index(drop='index')
            lacsLalurAposInovacoesDF.at[15,'Value'] = lacsLalurAposInovacoesDF.at[4,'Value'] #- lacsLalurAposInovacoesDF.at[28,'Value']
            #Calculo valor do IRPJ
            #lacsLalurAposInovacoesDF.at[16,'Value'] = lacsLalurAposInovacoesDF.at[15,'Value'] * 0.15
            lacsLalurAposInovacoesDF.at[21,'Value'] = np.where(lacsLalurAposInovacoesDF.at[20,'Value']>0,
                                                                lacsLalurAposInovacoesDF.at[20,'Value'] * 0.15,0)
            

            #Calculo valor do IRPJ Adicional
            lacsLalurAposInovacoesDF.at[22,'Value'] = np.where(lacsLalurAposInovacoesDF.at[20,'Value']< 240000,
                                                                (lacsLalurAposInovacoesDF.at[20,'Value'] - 240000)*0.1,0)

            #Calculo Total Devido IRPJ
            lacsLalurAposInovacoesDF.at[23,'Value'] = lacsLalurAposInovacoesDF.at[21,'Value'] + lacsLalurAposInovacoesDF.at[22,'Value']
            #Calculo PAT
            lacsLalurAposInovacoesDF.at[24,'Value'] = lacsLalurAposInovacoesDF.at[21,'Value'] * 0.04
            #Sub total IRPJ a recolher
            lacsLalurAposInovacoesDF.at[32,'Value'] = (lacsLalurAposInovacoesDF.at[23,'Value']-
                                                            lacsLalurAposInovacoesDF.at[24,'Value']-
                                                            lacsLalurAposInovacoesDF.at[25,'Value']-
                                                            lacsLalurAposInovacoesDF.at[26,'Value']-
                                                                lacsLalurAposInovacoesDF.at[27,'Value']-
                                                                lacsLalurAposInovacoesDF.at[28,'Value']-
                                                                lacsLalurAposInovacoesDF.at[29,'Value']-
                                                                    lacsLalurAposInovacoesDF.at[30,'Value']-
                                                                    lacsLalurAposInovacoesDF.at[31,'Value'])
            lacsLalurAposInovacoesDF = lacsLalurAposInovacoesDF.iloc[[0,1,2,3,4,5,6,7,8,9,10,11,
                                                                      12,33,13,14,15,16,17,18,19,
                                                                      20,21,22,23,24,25,26,27,28,29,
                                                                      30,31,32],:]                                              
            return lacsLalurAposInovacoesDF                      

    def LacsLalurAposInovacoesTrimestral(self,dataframe:pd.DataFrame) -> pd.DataFrame:
    
        df = dataframe
        df.at[35,'Operation 1º Trimestre'] = ''
        new_row = pd.DataFrame({'Operation 1º Trimestre': ['']}, index=[35])
        df = pd.concat([df, new_row])
        df = df.iloc[[0,1,2,33,3,4,5,6,26,7,8,9,10,35,11,14,12,13,17,18,19,20,21,22,23,24,25,27,28,29,30,31,32],2:]

        trimestres = ['1º Trimestre','2º Trimestre','3º Trimestre','4º Trimestre',]
        for i in trimestres:
            #Calculo exclusoes
            df.at[2,f'Value {i}'] = df.at[2,f'Value {i}'] + df.at[33,f'Value {i}'] 
            #Calculo Base 
            df.at[3,f'Value {i}'] = df.at[0,f'Value {i}'] + df.at[1,f'Value {i}'] - df.at[2,f'Value {i}'] 
            #Comp Preju Fiscal
            df.at[4,f'Value {i}'] =   np.where(df.at[4,f'Value {i}'] > df.at[3,f'Value {i}'] * 0.3,
                                               df.at[3,f'Value {i}'] * 0.3,
                                               df.at[4,f'Value {i}'])  
            #Calculo base CSLL
            df.at[5,f'Value {i}'] = df.at[3,f'Value {i}'] - df.at[4,f'Value {i}'] 
            #Valor CSLL
            df.at[6,f'Value {i}'] = np.where(df.at[5,f'Value {i}']>0,df.at[5,f'Value {i}']*0.09,0) 
            #Valor Sub total CSLL a Recolher
            df.at[10,f'Value {i}'] = df.at[6,f'Value {i}'] - df.at[7,f'Value {i}'] - df.at[8,f'Value {i}'] 
            #CSLL IRPJ
            df.at[12,f'Value {i}'] = df.at[6,f'Value {i}'] 
            #exclusoes
            df.at[17,f'Value {i}'] = df.at[2,f'Value {i}']
            #Valor Sub total Base IRPJ
            df.at[18,f'Value {i}'] = (df.at[11,f'Value {i}'] + df.at[14,f'Value {i}']) - df.at[2,f'Value {i}']
            #Calculando Lucro Real
            df.at[20,f'Value {i}'] = df.at[18,f'Value {i}'] - df.at[19,f'Value {i}']
            #Valor IRPJ
            df.at[21,f'Value {i}'] = np.where(df.at[20,f'Value {i}']>0,df.at[20,f'Value {i}']*0.15,0) 
            #Valor IRPJ Adicionais
            df.at[22,f'Value {i}'] = np.where(df.at[20,f'Value {i}']>60000,(df.at[20,f'Value {i}']-60000)*0.10,0) 
            #Total devido IRPJ antes retenções
            df.at[23,f'Value {i}'] = df.at[22,f'Value {i}'] + df.at[21,f'Value {i}'] 
            #Verificação pat
            df.at[24,f'Value {i}'] = np.where(df.at[21,f'Value {i}'] * 0.04 < df.at[24,f'Value {i}'], 
                                              df.at[21,f'Value {i}'] * 0.04,
                                              df.at[24,f'Value {i}']) 
            #Total devido IRPJ antes retenções
            df.at[32,f'Value {i}'] = (df.at[23,f'Value {i}'] - df.at[24,f'Value {i}'] - 
                                        df.at[25,f'Value {i}']- df.at[27,f'Value {i}'] - 
                                        df.at[28,f'Value {i}'] - df.at[29,f'Value {i}']-
                                        df.at[30,f'Value {i}'] - df.at[31,f'Value {i}'])


            return df

    def LacsLalurAposInovacoesTrimestralCallback(self,dataframe:pd.DataFrame) -> pd.DataFrame:

        df = dataframe
        trimestres = ['1º Trimestre','2º Trimestre','3º Trimestre','4º Trimestre',]
        for i in trimestres:
            #Calculo exclusoes
            df.at[2,f'Value {i}'] = df.at[2,f'Value {i}'] + df.at[33,f'Value {i}'] 
            #Calculo Base 
            df.at[3,f'Value {i}'] = df.at[0,f'Value {i}'] + df.at[1,f'Value {i}'] - df.at[2,f'Value {i}'] 
            #Calculo base CSLL
            df.at[5,f'Value {i}'] = df.at[3,f'Value {i}'] - df.at[4,f'Value {i}'] 
            #Valor CSLL
            df.at[6,f'Value {i}'] = np.where(df.at[5,f'Value {i}']>0,df.at[5,f'Value {i}']*0.09,0) 
            #Valor Sub total CSLL a Recolher
            df.at[10,f'Value {i}'] = df.at[6,f'Value {i}'] - df.at[7,f'Value {i}'] - df.at[8,f'Value {i}'] 
            #Valor Sub total Base IRPJ
            df.at[18,f'Value {i}'] = (df.at[11,f'Value {i}'] + df.at[14,f'Value {i}']) - df.at[2,f'Value {i}']
            #Calculando Lucro Real
            df.at[20,f'Value {i}'] = df.at[18,f'Value {i}'] - df.at[19,f'Value {i}']
            #Valor IRPJ
            df.at[21,f'Value {i}'] = np.where(df.at[20,f'Value {i}']>0,df.at[20,f'Value {i}']*0.15,0) 
            #Valor IRPJ Adicionais
            df.at[22,f'Value {i}'] = np.where(df.at[20,f'Value {i}']>60000,(df.at[20,f'Value {i}']-60000)*0.10,0) 
            #Total devido IRPJ antes retenções
            df.at[23,f'Value {i}'] = df.at[22,f'Value {i}'] + df.at[21,f'Value {i}'] 
            #Total devido IRPJ antes retenções
            df.at[32,f'Value {i}'] = (df.at[23,f'Value {i}'] - df.at[24,f'Value {i}'] - 
                                    df.at[25,f'Value {i}']- df.at[27,f'Value {i}'] - 
                                    df.at[28,f'Value {i}'] - df.at[29,f'Value {i}']-
                                        df.at[30,f'Value {i}'] - df.at[31,f'Value {i}'])


        return df

    def tabelaComparativaLacsLalur(self,cnpj,ano):
        tabelaLacsLalur = self.queryResultadoFinalTrimestral(cnpj=cnpj, tabela='lacslalurtrimestral', ano=ano)

        return tabelaLacsLalur
    
    def tabelaComparativaLacsLalurAno(self,cnpj,ano):
        tabelaLacsLalur = self.queryResultadoFinal(cnpj=cnpj, tabela='lacslalur', ano=ano)

        return tabelaLacsLalur

if __name__=='__main__':

    aposInovacoes = LacsLalurAposInovacoes('taxall')

    resultadoAnual =  aposInovacoes.gerandoTabelas('79283065000141',2019)
    st.dataframe(resultadoAnual,height=1000)
    #aposInovacoes.gerandoTabelasTrimestral()
