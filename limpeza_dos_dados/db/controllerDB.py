import pandas as pd
from sqlalchemy import create_engine, text
import sqlalchemy as sa
import streamlit as st
from sqlalchemy.exc import DBAPIError
import time
import functools
from psycopg2 import pool
from sqlalchemy import create_engine



header = {
    "autorization":  st.secrets["general"]["auth_token"],
    "content-type":"application/json"
}

MAX_RETRIES = 5

RETRY_DELAY = 5

class dbController():
    
    def __init__(self,banco):
        
        # self.engine = create_engine(f'postgresql+psycopg2://{st.secrets["general"]["auth_token"]}/ECF', 
        #                connect_args={'options': '-c datestyle=iso,mdy'})
        
        username = st.secrets["apiAWS"]["username"]
        password = st.secrets["apiAWS"]["password"]
        host = st.secrets["apiAWS"]["host"]
        port = st.secrets["apiAWS"]["port"]
        try:
            self.engine = create_engine(f'postgresql+psycopg2://{username}:{password}@{host}:{port}/taxall',pool_size=10,max_overflow=10,)
            self.conn = self.engine.connect()
        finally:
            ''#self.engine.dispose()
            #self.conn.close()

    def inserirTabelas(self, tabela, df):


        verificacaoCNPJ = df.iloc[0]['CNPJ']
        query = text(f"SELECT * FROM {tabela} WHERE \"CNPJ\" = :CNPJ")
        
        self.retry_count = 0

        while self.retry_count < MAX_RETRIES:
            try:
                # Execute the query
                with self.engine.connect() as conn:
                    result = conn.execute(query, {'CNPJ': verificacaoCNPJ})

                # Fetch the results
                    rows = result.fetchall()

                if rows:
                    st.warning(f"CNPJ {verificacaoCNPJ} já existe na tabela {tabela}. Não inserindo dados.")
                else:
                    df.to_sql(tabela, self.engine, if_exists='append', index=False)
                    st.success(f"CNPJ {verificacaoCNPJ} inserido com sucesso na tabela {tabela}!")

                # Break out of the retry loop
                break

            except sa.exc.OperationalError as e:
        
                print(f"Operational error: {e}")
                self.retry_count += 1
       
                time.sleep(RETRY_DELAY)
           
                self.conn = self.engine.connect()

        if self.retry_count == MAX_RETRIES:

            raise Exception("Failed to execute query after {} retries".format(MAX_RETRIES))


    def get_data_by_cnpj(self, cnpj,tabela):
        query = f"SELECT * FROM {tabela} WHERE \"CNPJ\" = '{cnpj}'"
        with self.engine.connect():
            try:
                df = pd.read_sql_query(query, self.engine)
            finally:
               '' #self.engine.dispose()    

        
        return df

    @functools.cache
    def get_jcp_value(self, cnpj: str, tabela: str, ano: int, operation: str) -> pd.DataFrame:
        query = f"""
            SELECT "CNPJ", "Ano", "Value","Operation"
            FROM {tabela}
            WHERE "CNPJ" = '{cnpj}' AND "Ano" = '{ano}' AND "Operation" = '{operation}'
        """
        with self.engine.connect():
            try:
                df = pd.read_sql_query(query, self.engine)
            finally:
                self.engine.dispose()
     
        return df

    @functools.cache
    def get_jcp_value_trimestral(self, cnpj: str, tabela: str, ano: int, operation: str) -> pd.DataFrame:
        query = f"""
            SELECT "CNPJ", "Ano", "Value 1º Trimestre","Value 2º Trimestre","Value 3º Trimestre","Value 4º Trimestre",
            "Operation 1º Trimestre",
            "Operation 2º Trimestre",
            "Operation 3º Trimestre",
            "Operation 4º Trimestre"
            FROM {tabela}
            WHERE "CNPJ" = '{cnpj}' AND "Ano" = '{ano}' 
            AND "Operation 1º Trimestre" = '{operation}' 
            AND "Operation 2º Trimestre" = '{operation}' 
            AND "Operation 3º Trimestre" = '{operation}' 
            AND "Operation 4º Trimestre" = '{operation}'  """
        
        with self.engine.connect():
            try:
                df = pd.read_sql_query(query, self.engine)
            finally:
                self.engine.dispose()    

       
        return df
    
    def deletarDadosDaTabela(self,tabela):
        query = text("DELETE FROM {}".format(tabela))
        
        self.conn.execute(query)
        print(f'Os valores para tabela {tabela} foram DELETADOS!')
        self.conn.commit()
   
    def deletarDadosDaTabelaPorCnpj(self, cnpj, tabela):
        # Use parameterized query to avoid SQL injection and properly handle data types
        query = text(f"DELETE FROM {tabela} WHERE \"CNPJ\" = :cnpj")
        self.conn.execute(query, {"cnpj": cnpj})
        print(f'Os valores para tabela {tabela} e CNPJ {cnpj} foram DELETADOS!')
        self.conn.commit()


    def get_all_data(self,tabela):
        query = f"SELECT * FROM {tabela}"
        try:
            with self.engine.connect():
                df = pd.read_sql_query(query, self.engine)
        finally:
            ''#self.engine.dispose()
      
        return df

    @functools.cache
    def queryResultadoFinal(self, cnpj,tabela,ano):
        
        query = f""" 
        SELECT "CNPJ", "Ano", "Value","Operation","index"
        FROM {tabela}
        WHERE \"CNPJ\" = '{cnpj}' AND \"Ano\" = '{ano}'"""
        query2 = f""" 
        SELECT "CNPJ", "Ano", "Value","Operation"
        FROM {tabela}
        WHERE \"CNPJ\" = '{cnpj}' AND \"Ano\" = '{ano}'"""
        with self.engine.connect():
            try:
                try:
                    df = pd.read_sql_query(query, self.engine)
                except:
                    df = pd.read_sql_query(query2, self.engine)
            finally:
                self.engine.dispose()
        return df

    @functools.cache
    def queryResultadoFinalTrimestral(self, cnpj,tabela,ano):
        query = f"""
        SELECT "CNPJ", "Ano","Operation 1º Trimestre" ,"Value 1º Trimestre","Operation 2º Trimestre" ,"Value 2º Trimestre",
        "Operation 3º Trimestre" ,"Value 3º Trimestre","Operation 4º Trimestre" ,"Value 4º Trimestre","index"
            FROM {tabela}
            WHERE "CNPJ" = '{cnpj}' AND "Ano" = '{ano}' """
        
        query2 = f"""
        SELECT "CNPJ", "Ano","Operation 1º Trimestre" ,"Value 1º Trimestre","Operation 2º Trimestre" ,"Value 2º Trimestre",
        "Operation 3º Trimestre" ,"Value 3º Trimestre","Operation 4º Trimestre" ,"Value 4º Trimestre"
            FROM {tabela}
            WHERE "CNPJ" = '{cnpj}' AND "Ano" = '{ano}' """

        with self.engine.connect(): 
            try:   
                try:
                    df = pd.read_sql_query(query, self.engine)
                except:
                    df = pd.read_sql_query(query2, self.engine)
            finally:
                self.engine.dispose()
      
        return df
    
    def inserirTabelasFinaisJCP(self, tabela, df):
        verificacaoAno = int(df.iloc[0]['Ano'])
        verificacaoCNPJ = df.iloc[0]['CNPJ']

        query = text(f"SELECT * FROM {tabela} WHERE \"Ano\" = :Ano AND \"CNPJ\" = :CNPJ")
        
        result = self.conn.execute(query, {'Ano': verificacaoAno, 'CNPJ': float(verificacaoCNPJ)})

        rows = result.fetchall()

        if rows:
            st.warning(f"Ano {verificacaoAno} e CNPJ {verificacaoCNPJ} já existem na tabela {tabela}. Não inserindo dados.")
        else:
            with self.engine.connect():
                try:
                    df.to_sql(tabela, self.engine, if_exists='append', index=False)
                    st.success(f"Ano {verificacaoAno} e CNPJ {verificacaoCNPJ} inserido com sucesso no banco ECF!")
                finally:
                   '' #self.engine.dispose()

    def update_table(self, tabela, df, cnpj, ano):
        operations = df['Operation'].unique()
        
        # Gerenciador de contexto para a transação
        with self.conn.begin() as transaction:
            try:
                for operation in operations:
                    value = float(df.loc[df['Operation'] == operation, 'Value'].iloc[0])
                    query = text(f"UPDATE {tabela} SET \"Value\" = :Value WHERE \"CNPJ\" = :CNPJ AND \"Ano\" = :Ano AND \"Operation\" = :Operation")
                    params = {'Value': value, 'CNPJ': cnpj, 'Ano': ano, 'Operation': operation}
                    self.conn.execute(query, params)
                
                st.success('Os valores foram atualizados')
            
            except Exception as e:
                # Se ocorrer um erro, a transação será revertida automaticamente
                st.warning(f'Não foi possível atualizar os valores para {operation} por {e}')
            finally:
                ''#self.conn.close()

    def update_table_trimestral(self, tabela, df, cnpj, ano):
        operations = [op for trimestre in [1,2,3,4] for op in df[f'Operation {trimestre}º Trimestre'].unique()]
    # Gerenciador de contexto para a transação
        with self.conn.begin() as transaction:
            try:
                for trimestre in [1,2,3,4]:
                    for operation in operations:
                        filtered_df = df.loc[df[f'Operation {trimestre}º Trimestre'] == operation]
                        if not filtered_df.empty:
                            value = float(filtered_df[f'Value {trimestre}º Trimestre'].iloc[0])
                            query = text(f"UPDATE {tabela} SET \"Value {trimestre}º Trimestre\" = :Value WHERE \"CNPJ\" = :CNPJ AND \"Ano\" = :Ano AND \"Operation {trimestre}º Trimestre\" = :Operation")
                            params = {'Value': value, 'CNPJ': cnpj, 'Ano': ano, 'Operation': operation}
                            self.conn.execute(query, params)
                        else:
                            st.warning(f'Não há valores para {operation} no {trimestre}º trimestre')
                    st.success(f'Os valores para {trimestre}º trimestre foram atualizados')
            
            except Exception as e:
                # Se ocorrer um erro, a transação será revertida automaticamente
                st.warning(f'Não foi possível atualizar os valores para {operation} por {e}')

            finally:
                self.conn.close()


if __name__ =="__main__":
    
    controler = dbController('taxall')
    # controler.deletarDadosDaTabelaPorCnpj('07608821000154','l100')
    # controler.deletarDadosDaTabelaPorCnpj('07608821000154','l300')
    # controler.deletarDadosDaTabelaPorCnpj('07608821000154','m300')
    # controler.deletarDadosDaTabelaPorCnpj('07608821000154','m350')
    # controler.deletarDadosDaTabelaPorCnpj('07608821000154','n630')
    # controler.deletarDadosDaTabelaPorCnpj('07608821000154','n670')
    # controler.deletarDadosDaTabelaPorCnpj('07608821000154','resultadosjcp')
    # controler.deletarDadosDaTabelaPorCnpj('07608821000154','resultadosjcptrimestral')
    # controler.deletarDadosDaTabelaPorCnpj('07608821000154','tipodaanalise')
    # controler.deletarDadosDaTabelaPorCnpj('07608821000154','cadastrodasempresas')
    # controler.deletarDadosDaTabelaPorCnpj('07608821000154','lacslalur')
    # controler.deletarDadosDaTabelaPorCnpj('07608821000154','lacslalurtrimestral')

    controler.deletarDadosDaTabela('l100')
    controler.deletarDadosDaTabela('l300')
    controler.deletarDadosDaTabela('m300')
    controler.deletarDadosDaTabela('m350')
    controler.deletarDadosDaTabela('n630')
    controler.deletarDadosDaTabela('n670')
    controler.deletarDadosDaTabela('resultadosjcp')
    controler.deletarDadosDaTabela('resultadosjcptrimestral')
    controler.deletarDadosDaTabela('tipodaanalise')
    controler.deletarDadosDaTabela('cadastrodasempresas')
    controler.deletarDadosDaTabela('lacslalur')
    controler.deletarDadosDaTabela('lacslalurtrimestral')

    # l100Teste = controler.get_data_by_cnpj("14576552000157","m350")
    # st.data_editor(l100Teste)


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


