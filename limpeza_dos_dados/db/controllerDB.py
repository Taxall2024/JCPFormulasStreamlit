import pandas as pd
from sqlalchemy import create_engine, text




class dbController():

    def __init__(self,banco):
        
        self.engine = create_engine(f'postgresql+psycopg2://postgres:Taxall2024@localhost:5432/{banco}')
        self.conn = self.engine.connect()
        #self.cur = self.conn.execute()

    def inserirTabelas(self, tabela, df):
            
            verificacaoCNPJ = df.iloc[0]['CNPJ']  
            query = text(f"SELECT * FROM {tabela} WHERE CNPJ = :CNPJ")
            result = self.conn.execute(query, {'CNPJ': verificacaoCNPJ})

            # Fetch the result to check if any rows were found
            rows = result.fetchall()

            if rows:
                print(f"CNPJ {verificacaoCNPJ} já existe na tabela {tabela}. Não inserindo dados.")
            else:
                df.to_sql(tabela, self.engine, if_exists='append', index=False)
                self.conn.execute("COMMIT")
                print("DataFrame inserido com sucesso no banco ECF!")

    def get_data_by_cnpj(self, cnpj,tabela):
        query = f"SELECT * FROM {tabela} WHERE CNPJ = '{cnpj}'"
        df = pd.read_sql_query(query, self.engine)
        return df

# if __name__ =="__main__":
#     controler = dbController('ECF')



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


