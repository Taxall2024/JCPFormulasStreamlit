import pandas as pd
from sqlalchemy import create_engine, text
import streamlit as st



class dbController():

    def __init__(self,banco):
        
        self.engine = create_engine(f'postgresql+psycopg2://postgres:Taxall2024@localhost:5432/{banco}')
        self.conn = self.engine.connect()


    def inserirTabelas(self, tabela, df):

        verificacaoCNPJ = df.iloc[0]['CNPJ'] 
        query = text(f"SELECT * FROM {tabela} WHERE \"CNPJ\" = :CNPJ")
        result = self.conn.execute(query, {'CNPJ': verificacaoCNPJ})

        rows = result.fetchall()

        if rows:
            st.warning(f"CNPJ {verificacaoCNPJ} já existe na tabela {tabela}. Não inserindo dados.")
        else:
            df.to_sql(tabela, self.engine, if_exists='append', index=False)
            st.success(f"CNPJ {verificacaoCNPJ} inserido com sucesso na tabela {tabela}!")

    def get_data_by_cnpj(self, cnpj,tabela):
        query = f"SELECT * FROM {tabela} WHERE \"CNPJ\" = '{cnpj}'"
        df = pd.read_sql_query(query, self.engine)
        return df
    def get_all_data(self,tabela):
        query = f"SELECT * FROM {tabela}"
        df = pd.read_sql_query(query, self.engine)
        return df
    
    def queryResultadoFinal(self, cnpj,tabela,ano):
        query = f"SELECT * FROM {tabela} WHERE \"CNPJ\" = '{cnpj}' AND \"Ano\" = '{ano}'"
        df = pd.read_sql_query(query, self.engine)
        return df
    
    def inserirTabelasFinaisJCP(self, tabela, df):
        verificacaoAno = int(df.iloc[0]['Ano'])
        verificacaoCNPJ = df.iloc[0]['CNPJ']

        query = text(f"SELECT * FROM {tabela} WHERE \"Ano\" = :Ano AND \"CNPJ\" = :CNPJ")
        result = self.conn.execute(query, {'Ano': verificacaoAno, 'CNPJ': verificacaoCNPJ})

        rows = result.fetchall()

        if rows:
            st.warning(f"Ano {verificacaoAno} e CNPJ {verificacaoCNPJ} já existem na tabela {tabela}. Não inserindo dados.")
        else:
            df.to_sql(tabela, self.engine, if_exists='append', index=False)
            st.success(f"Ano {verificacaoAno} e CNPJ {verificacaoCNPJ} inserido com sucesso no banco ECF!")


if __name__ =="__main__":
    
    controler = dbController('ECF')


    l100Teste = controler.get_data_by_cnpj("14576552000157","m350")
    st.data_editor(l100Teste)


#     df = pd.DataFrame({
#     'CNPJ': [12345678000195, 98765432000167],
#     'Data Inicial': ['2023-01-01', '2023-01-01'],
#     'Data Final': ['2023-12-31', '2023-12-31'],
#     'Ano': [2023, 2023],
#     'Período Apuração': ['Anual', 'Anual'],
#     'Período Apuração Trimestral': ['Q1', 'Q2'],
#     'Conta Referencial': ['111', '222'],
#     'Conta Superior': ['110', '220'],
#     'Descrição Conta Referencial': ['Caixa', 'Banco'],
#     'Natureza Conta': ['Ativo', 'Ativo'],
#     'Tipo Conta': ['Sintética', 'Sintética'],
#     'Nível Conta': [1, 1],
#     'Vlr Saldo Final': [50000.00, 75000.00],
#     'D/C Saldo Final': ['D', 'C']
# })

#     controler.inserirTabelas('l100',df)


