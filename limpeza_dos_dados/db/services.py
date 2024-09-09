import psycopg2
from psycopg2 import sql

class serviceTaxAllDB():

    def __init__(self):
        
        
        self.conn = psycopg2.connect(
            dbname="postgres",
            user="postgres",
            password="Taxall2024",
            host="localhost",
            port="5432"
        )

    def creating_DB(self,nomeDaDB):
        self.conn.autocommit = True 
        cur = self.conn.cursor()


        db_name = nomeDaDB


        try:
            cur.execute(sql.SQL("CREATE DATABASE {}").format(
                sql.Identifier(db_name)
            ))
            print(f"Banco de dados '{db_name}' criado com sucesso!")
        except psycopg2.errors.DuplicateDatabase:
            print(f"O banco de dados '{db_name}' já existe.")

    def creatingTables(self,db,formatoDaTabela):

        conn = psycopg2.connect(
            dbname=f"{db}",
            user="postgres",
            password="Taxall2024",
            host="localhost",
            port="5432"
        )


        cur = conn.cursor()
        cur.execute(formatoDaTabela)
        conn.commit()




if __name__=='__main__':

    service = serviceTaxAllDB()
    #service.creating_DB('Clientes')
    #service.creatingTables('ECF',create_table_query_teste)

    create_table_query_L100 = '''
    CREATE TABLE IF NOT EXISTS L100 (
        CNPJ NUMERIC NOT NULL,
        "Data Inicial" DATE NOT NULL,
        "Data Final" DATE NOT NULL,
        Ano INT,
        "Período Apuração" VARCHAR(50),
        "Período Apuração Trimestral" VARCHAR(50),
        "Conta Referencial" VARCHAR(50),
        "Conta Superior" VARCHAR(50),
        "Descrição Conta Referencial" VARCHAR(255),
        "Natureza Conta" VARCHAR(50),
        "Tipo Conta" VARCHAR(50),
        "Nível Conta" INT,
        "Vlr Saldo Final" NUMERIC,
        "D/C Saldo Final" VARCHAR(2)
    )
    '''

    create_table_query_L300 = '''
        CREATE TABLE IF NOT EXISTS L300 (
            CNPJ NUMERIC NOT NULL,
            "Data Inicial" DATE NOT NULL,
            "Data Final" DATE NOT NULL,
            Ano INT,
            "Período Apuração" VARCHAR(50),
            "Período Apuração Trimestral" VARCHAR(50),
            "Conta Referencial" VARCHAR(50),
            "Conta Superior" VARCHAR(50),
            "Descrição Conta Referencial" VARCHAR(255),
            "Natureza Conta" VARCHAR(50),
            "Tipo Conta" VARCHAR(50),
            "Nível Conta" INT,
            "Vlr Saldo Final" NUMERIC,
            "D/C Saldo Final" VARCHAR(2)
        )
        '''

    create_table_query_M300 = '''
        CREATE TABLE IF NOT EXISTS M300 (
            CNPJ NUMERIC NOT NULL,
            "Data Inicial" DATE NOT NULL,
            "Data Final" DATE NOT NULL,
            "Período Apuração" VARCHAR(50),
            "Período Apuração Trimestral" VARCHAR(50),
            "Conta Referencial" VARCHAR(50),
            "Código Lançamento e-Lalur" FLOAT,
            "Descrição Lançamento e-Lalur" VARCHAR(255),
            "Natureza Conta" VARCHAR(50),
            "Tipo Lançamento" VARCHAR(50),
            "Indicador Relação Parte A" VARCHAR(50),
            "Vlr Lançamento e-Lalur" NUMERIC,
            "Histórico e-Lalur" VARCHAR(50)
        )
        '''

    create_table_query_M350 = '''
        CREATE TABLE IF NOT EXISTS M350 (
            CNPJ NUMERIC NOT NULL,
            "Data Inicial" DATE NOT NULL,
            "Data Final" DATE NOT NULL,
            "Período Apuração" VARCHAR(50),
            "Período Apuração Trimestral" VARCHAR(50),
            "Código Lançamento e-Lacs" FLOAT,
            "Descrição Lançamento e-Lalur" VARCHAR(255),
            "Tipo Lançamento" VARCHAR(50),
            "Indicador Relação Parte A" VARCHAR(50),
            "Vlr Lançamento e-Lacs" NUMERIC,
            "Histórico e-Lacs" VARCHAR(50)
        )
        '''

    create_table_query_N630 = '''
        CREATE TABLE IF NOT EXISTS N630 (
            CNPJ NUMERIC NOT NULL,
            "Data Inicial" DATE NOT NULL,
            "Data Final" DATE NOT NULL,
            "Período Apuração" VARCHAR(50),
            "Período Apuração Trimestral" VARCHAR(50),
            "Código Lançamento" FLOAT,
            "Descrição Lançamento" VARCHAR(255),
            "Vlr Lançamento" NUMERIC
        )
        '''

    create_table_query_N670 = '''
        CREATE TABLE IF NOT EXISTS N670 (
            CNPJ NUMERIC NOT NULL,
            "Data Inicial" DATE NOT NULL,
            "Data Final" DATE NOT NULL,
            "Período Apuração" VARCHAR(50),
            "Período Apuração Trimestral" VARCHAR(50),
            "Código Lançamento" FLOAT,
            "Descrição Lançamento" VARCHAR(255),
            "Vlr Lançamento" NUMERIC
        )
        '''









