from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np
import functools
import streamlit as st
@functools.cache
@st.cache_data()
class ScrappingTJPL():
    
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
