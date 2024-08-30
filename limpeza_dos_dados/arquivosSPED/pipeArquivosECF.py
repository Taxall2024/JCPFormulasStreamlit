import pandas as pd
import streamlit as st


#st.set_page_config(layout='wide')

# class PipeTratamentoDadosSPED()
#     def __init__(self):
        
# sped1 = r'C:\Users\lauro.loyola\Desktop\JCPCalculos\limpeza_dos_dados\arquivosSPED\SPEDECF-79283065000141-20190101-20191231-20231208111202.txt'
# sped2 = r'C:\Users\lauro.loyola\Desktop\JCPCalculos\limpeza_dos_dados\arquivosSPED\SPEDECF-79283065000141-20200101-20201231-20231208111910.txt'
# sped3 = r'C:\Users\lauro.loyola\Desktop\JCPCalculos\limpeza_dos_dados\arquivosSPED\SPEDECF-79283065000141-20210101-20211231-20231016174350.txt'
# sped4 = r'C:\Users\lauro.loyola\Desktop\JCPCalculos\limpeza_dos_dados\arquivosSPED\SPEDECF-79283065000141-20220101-20221231-20231114173914.txt'
# sped5 = r'C:\Users\lauro.loyola\Desktop\JCPCalculos\limpeza_dos_dados\arquivosSPED\SPEDECF-79283065000141-20230101-20231231-20240417183332.txt'

# listaDeArquivos= [sped1,sped2,sped3,sped4,sped5]

# listaL100 = []
# listaL300 = []
# listaM300 = []
# listaM350 = []
# listaN630 = []
# listaN670 = []

# def lendoELimpandoDadosSped(filePath):
# # Inicializa uma lista para armazenar todas as linhas formatadas
#     data = []

#     # Abre o arquivo e lê linha por linha
#     with open(filePath, 'r', encoding='latin-1') as file:
#         for linha in file:
#             # Remove espaços em branco ao redor da linha
#             linha = linha.strip()
            
#             # Verifica se a linha começa com um padrão de 4 dígitos seguido por '|'
#             if linha.startswith('|'):
#                 # Separa os valores utilizando '|' como delimitador
#                 valores = linha.split('|')[1:]  # Ignora o primeiro elemento vazio antes do primeiro '|'
#                 data.append(valores)

#     df = pd.DataFrame(data).iloc[:,:13]
#     df['Data Inicial'] = df.iloc[0,9]
#     df['Data Final'] = df.iloc[0,10]
#     df['Ano'] = df['Data Inicial'].astype(str).str[-4:]
#     df['CNPJ'] = df.iloc[0,3]
#     df['Período Apuração'] = None
#     df['Data Inicial'] = pd.to_datetime(df['Data Inicial'], format='%d%m%Y').dt.strftime('%d/%m/%Y')
#     df['Data Final'] = pd.to_datetime(df['Data Final'], format='%d%m%Y').dt.strftime('%d/%m/%Y')
    
#     return df
# peridoApuracao = [
#     'A01 – Balanço de Suspensão e Redução até Janeiro',
#     'A02 – Balanço de Suspensão e Redução até Fevereiro',
#     'A03 – Balanço de Suspensão e Redução até Março',
#     'A04 – Balanço de Suspensão e Redução até Abril',
#     'A05 – Balanço de Suspensão e Redução até Maio',
#     'A06 – Balanço de Suspensão e Redução até Junho',
#     'A07 – Balanço de Suspensão e Redução até Julho',
#     'A08 – Balanço de Suspensão e Redução até Agosto',
#     'A09 – Balanço de Suspensão e Redução até Setembro',
#     'A10 – Balanço de Suspensão e Redução até Outubro',
#     'A11 – Balanço de Suspensão e Redução até Novembro',
#     'A12 – Balanço de Suspensão e Redução até Dezembro',
#     'A00 – Receita Bruta/Balanço de Suspensão e Redução Anual']


# arquivoTeste = lendoELimpandoDadosSped(sped1)
# #arquivoTeste.to_excel('L100EncontrarPadraoDeA00.xlsx')
# def classificaPeriodoDeApuracao(arquivo, referencia):
#     bloco_iniciado = False
#     data_index = 0
#     for i in range(len(arquivo)):
#         if arquivo.loc[i, 2] == referencia:
#             if bloco_iniciado:
#                 data_index += 1
#             else:
#                 # Inicia o bloco na primeira ocorrência
#                 bloco_iniciado = True
            
#             # Atualizar a coluna 'Data Final' para o bloco atual
#             if data_index < len(peridoApuracao):
#                 arquivo.loc[i:, 'Período Apuração'] = peridoApuracao[data_index]
#     return arquivo

# def gerandoArquivosECF(caminho):
#     dfSped1 = lendoELimpandoDadosSped(caminho)

#     dfSped1L100 =  dfSped1[(dfSped1[0]=='L100')|(dfSped1[0]=='N030')].reset_index(drop='index')
#     dfSped1L100 = classificaPeriodoDeApuracao(dfSped1L100,'ATIVO')

#     dfSped1L300 =  dfSped1[dfSped1[0]=='L300'].reset_index(drop='index')
#     dfSped1L300 = classificaPeriodoDeApuracao(dfSped1L300,'RESULTADO LÍQUIDO DO PERÍODO')

#     dfSped1M300 =  dfSped1[dfSped1[0]=='M300'].reset_index(drop='index')
#     dfSped1M300 = classificaPeriodoDeApuracao(dfSped1M300,'ATIVIDADE GERAL')

#     dfSped1M350 =  dfSped1[dfSped1[0]=='M350'].reset_index(drop='index')
#     dfSped1M350 = classificaPeriodoDeApuracao(dfSped1M350,'ATIVIDADE GERAL')

#     dfSped1N630 =  dfSped1[dfSped1[0]=='N630'].reset_index(drop='index')
#     dfSped1N630['Período Apuração'] = 'A00 – Receita Bruta/Balanço de Suspensão e Redução Anual'

#     dfSped1N670 =  dfSped1[dfSped1[0]=='N670'].reset_index(drop='index')
#     dfSped1N670['Período Apuração'] = 'A00 – Receita Bruta/Balanço de Suspensão e Redução Anual'

#     return dfSped1L100, dfSped1L300, dfSped1M300, dfSped1M350, dfSped1N630, dfSped1N670

# for i in listaDeArquivos:
#     dfSped1L100, dfSped1L300, dfSped1M300, dfSped1M350, dfSped1N630, dfSped1N670 = gerandoArquivosECF(i)
#     listaL100.append(dfSped1L100)
#     listaL300.append(dfSped1L300)
#     listaM300.append(dfSped1M300)
#     listaM350.append(dfSped1M350)
#     listaN630.append(dfSped1N630)
#     listaN670.append(dfSped1N670)

# L100Final = pd.concat(listaL100).reset_index(drop='index').rename(columns={1:'Conta Referencial',
#                                                                            2:'Descrição Conta Referencial',
#                                                                            3:"Tipo Conta",
#                                                                            4:'Nível Conta',
#                                                                            5:'Natureza Conta',
#                                                                            6:'Conta Superior',
#                                                                            8:'D/C Saldo Final',
#                                                                            11:'Vlr Saldo Final',}).drop(columns=[7,9,10,0])
# L100Final = L100Final[['CNPJ','Data Inicial','Data Final','Ano','Período Apuração',
#                        'Conta Referencial','Conta Superior','Descrição Conta Referencial',
#                        'Natureza Conta','Tipo Conta','Nível Conta','Vlr Saldo Final','D/C Saldo Final']]

# L300Final = pd.concat(listaL300).reset_index(drop='index').rename(columns={1:"Conta Referencial",
#                                                                            2:'Descrição Conta Referencial',
#                                                                            3:'Tipo Conta',
#                                                                            4:"Nível Conta",
#                                                                            5:'Natureza Conta',
#                                                                            6:'Conta Superior',
#                                                                            7:'Vlr Saldo Final',
#                                                                            8:'D/C Saldo Final'})
# L300Final= L300Final[['CNPJ','Data Inicial','Data Final','Ano','Período Apuração',
#                        'Conta Referencial','Conta Superior','Descrição Conta Referencial',
#                        'Natureza Conta','Tipo Conta','Nível Conta','Vlr Saldo Final','D/C Saldo Final']]

# M300Final = pd.concat(listaM300).reset_index(drop='index').rename(columns={1:'Código Lançamento e-Lalur',
#                                                                            2:'Descrição Lançamento e-Lalur',
#                                                                            3:'Tipo Lançamento',
#                                                                            4:'Indicador Relação Parte A',
#                                                                            5:'Vlr Lançamento e-Lalur',
#                                                                            6:'Histórico e-Lalur'})
# M300Final = M300Final[['CNPJ','Data Inicial','Data Final','Ano','Período Apuração',
#                        'Código Lançamento e-Lalur','Descrição Lançamento e-Lalur','Tipo Lançamento',
#                        'Indicador Relação Parte A','Vlr Lançamento e-Lalur']]

# M350Final = pd.concat(listaM350).reset_index(drop='index').rename(columns={1:'Código Lançamento e-Lacs',
#                                                                            2:'Descrição Lançamento e-Lacs',
#                                                                            4:'Indicador Relação Parte A',
#                                                                            5:'Vlr Lançamento e-Lacs',
#                                                                            6:'Histórico e-Lacs'})
# M350Final = M350Final[['CNPJ','Data Inicial','Data Final','Ano','Período Apuração',
#                        'Código Lançamento e-Lacs','Descrição Lançamento e-Lacs',
#                        'Indicador Relação Parte A','Vlr Lançamento e-Lacs','Histórico e-Lacs']]

# N630Final = pd.concat(listaN630).reset_index(drop='index').rename(columns={1:'Código Lançamento',
#                                                                            2:"Descrição Lançamento",
#                                                                            3:'Vlr Lançamento'})
# N630Final = N630Final[['CNPJ','Data Inicial','Data Final','Ano','Período Apuração',
#                        'Código Lançamento','Descrição Lançamento','Vlr Lançamento']]

# N670Final = pd.concat(listaN670).reset_index(drop='index').rename(columns={1:'Código Lançamento',
#                                                                            2:'Descrição Lançamento',
#                                                                            3:"Vlr Lançamento"})
# N670Final = N670Final[['CNPJ','Data Inicial','Data Final','Ano','Período Apuração',
#                        'Código Lançamento','Descrição Lançamento','Vlr Lançamento']]

# st.dataframe(L100Final)
# st.dataframe(L300Final)
# st.dataframe(M300Final)
# st.dataframe(M350Final)
# st.dataframe(N630Final)
# st.dataframe(N670Final)


class SpedProcessor:
    def __init__(self, file_paths):
        self.file_paths = file_paths
        self.listaL100 = []
        self.listaL300 = []
        self.listaM300 = []
        self.listaM350 = []
        self.listaN630 = []
        self.listaN670 = []

    def lendoELimpandoDadosSped(self, file_path):
        data = []
        with open(file_path, 'r', encoding='latin-1') as file:
            for linha in file:
                linha = linha.strip()
                if linha.startswith('|'):
                    valores = linha.split('|')[1:]
                    data.append(valores)

        df = pd.DataFrame(data).iloc[:, :13]
        df['Data Inicial'] = df.iloc[0, 9]
        df['Data Final'] = df.iloc[0, 10]
        df['Ano'] = df['Data Inicial'].astype(str).str[-4:]
        df['CNPJ'] = df.iloc[0, 3]
        df['Período Apuração'] = None
        df['Data Inicial'] = pd.to_datetime(df['Data Inicial'], format='%d%m%Y').dt.strftime('%d/%m/%Y')
        df['Data Final'] = pd.to_datetime(df['Data Final'], format='%d%m%Y').dt.strftime('%d/%m/%Y')
        
        return df

    def classificaPeriodoDeApuracao(self, arquivo, referencia):
        bloco_iniciado = False
        data_index = 0
        perido_apuracao = [
            'A01 – Balanço de Suspensão e Redução até Janeiro',
            'A02 – Balanço de Suspensão e Redução até Fevereiro',
            'A03 – Balanço de Suspensão e Redução até Março',
            'A04 – Balanço de Suspensão e Redução até Abril',
            'A05 – Balanço de Suspensão e Redução até Maio',
            'A06 – Balanço de Suspensão e Redução até Junho',
            'A07 – Balanço de Suspensão e Redução até Julho',
            'A08 – Balanço de Suspensão e Redução até Agosto',
            'A09 – Balanço de Suspensão e Redução até Setembro',
            'A10 – Balanço de Suspensão e Redução até Outubro',
            'A11 – Balanço de Suspensão e Redução até Novembro',
            'A12 – Balanço de Suspensão e Redução até Dezembro',
            'A00 – Receita Bruta/Balanço de Suspensão e Redução Anual'
        ]
        for i in range(len(arquivo)):
            if arquivo.loc[i, 2] == referencia:
                if bloco_iniciado:
                    data_index += 1
                else:
                    bloco_iniciado = True

                if data_index < len(perido_apuracao):
                    arquivo.loc[i:, 'Período Apuração'] = perido_apuracao[data_index]
        return arquivo

    def gerandoArquivosECF(self, caminho):
        df_sped = self.lendoELimpandoDadosSped(caminho)

        df_sped_l100 = df_sped[(df_sped[0] == 'L100') | (df_sped[0] == 'N030')].reset_index(drop=True)
        df_sped_l100 = self.classificaPeriodoDeApuracao(df_sped_l100, 'ATIVO')

        df_sped_l300 = df_sped[df_sped[0] == 'L300'].reset_index(drop=True)
        df_sped_l300 = self.classificaPeriodoDeApuracao(df_sped_l300, 'RESULTADO LÍQUIDO DO PERÍODO')

        df_sped_m300 = df_sped[df_sped[0] == 'M300'].reset_index(drop=True)
        df_sped_m300 = self.classificaPeriodoDeApuracao(df_sped_m300, 'ATIVIDADE GERAL')

        df_sped_m350 = df_sped[df_sped[0] == 'M350'].reset_index(drop=True)
        df_sped_m350 = self.classificaPeriodoDeApuracao(df_sped_m350, 'ATIVIDADE GERAL')

        df_sped_n630 = df_sped[df_sped[0] == 'N630'].reset_index(drop=True)
        df_sped_n630['Período Apuração'] = 'A00 – Receita Bruta/Balanço de Suspensão e Redução Anual'

        df_sped_n670 = df_sped[df_sped[0] == 'N670'].reset_index(drop=True)
        df_sped_n670['Período Apuração'] = 'A00 – Receita Bruta/Balanço de Suspensão e Redução Anual'

        return df_sped_l100, df_sped_l300, df_sped_m300, df_sped_m350, df_sped_n630, df_sped_n670

    def processar_arquivos(self):
        for file_path in self.file_paths:
            df_sped_l100, df_sped_l300, df_sped_m300, df_sped_m350, df_sped_n630, df_sped_n670 = self.gerandoArquivosECF(file_path)
            self.listaL100.append(df_sped_l100)
            self.listaL300.append(df_sped_l300)
            self.listaM300.append(df_sped_m300)
            self.listaM350.append(df_sped_m350)
            self.listaN630.append(df_sped_n630)
            self.listaN670.append(df_sped_n670)

    def concatenar_dfs(self):
        L100_final = pd.concat(self.listaL100).reset_index(drop=True).rename(columns={
            1: 'Conta Referencial', 2: 'Descrição Conta Referencial', 3: "Tipo Conta", 4: 'Nível Conta',
            5: 'Natureza Conta', 6: 'Conta Superior', 8: 'D/C Saldo Final', 11: 'Vlr Saldo Final'}).drop(columns=[7, 9, 10, 0])
        L100_final = L100_final[['CNPJ', 'Data Inicial', 'Data Final', 'Ano', 'Período Apuração',
                                 'Conta Referencial', 'Conta Superior', 'Descrição Conta Referencial',
                                 'Natureza Conta', 'Tipo Conta', 'Nível Conta', 'Vlr Saldo Final', 'D/C Saldo Final']]

        L300_final = pd.concat(self.listaL300).reset_index(drop=True).rename(columns={
            1: "Conta Referencial", 2: 'Descrição Conta Referencial', 3: 'Tipo Conta', 4: "Nível Conta",
            5: 'Natureza Conta', 6: 'Conta Superior', 7: 'Vlr Saldo Final', 8: 'D/C Saldo Final'})
        L300_final = L300_final[['CNPJ', 'Data Inicial', 'Data Final', 'Ano', 'Período Apuração',
                                 'Conta Referencial', 'Conta Superior', 'Descrição Conta Referencial',
                                 'Natureza Conta', 'Tipo Conta', 'Nível Conta', 'Vlr Saldo Final', 'D/C Saldo Final']]

        M300_final = pd.concat(self.listaM300).reset_index(drop=True).rename(columns={
            1: 'Código Lançamento e-Lalur', 2: 'Descrição Lançamento e-Lalur', 3: 'Tipo Lançamento',
            4: 'Indicador Relação Parte A', 5: 'Vlr Lançamento e-Lalur', 6: 'Histórico e-Lalur'})
        M300_final = M300_final[['CNPJ', 'Data Inicial', 'Data Final', 'Ano', 'Período Apuração',
                                 'Código Lançamento e-Lalur', 'Descrição Lançamento e-Lalur', 'Tipo Lançamento',
                                 'Indicador Relação Parte A', 'Vlr Lançamento e-Lalur']]

        M350_final = pd.concat(self.listaM350).reset_index(drop=True).rename(columns={
            1: 'Código Lançamento e-Lacs', 2: 'Descrição Lançamento e-Lacs', 4: 'Indicador Relação Parte A',
            5: 'Vlr Lançamento e-Lacs', 6: 'Histórico e-Lacs'})
        M350_final = M350_final[['CNPJ', 'Data Inicial', 'Data Final', 'Ano', 'Período Apuração',
                                 'Código Lançamento e-Lacs', 'Descrição Lançamento e-Lacs',
                                 'Indicador Relação Parte A', 'Vlr Lançamento e-Lacs', 'Histórico e-Lacs']]

        N630_final = pd.concat(self.listaN630).reset_index(drop=True).rename(columns={
            1: 'Código Lançamento', 2: "Descrição Lançamento", 3: 'Vlr Lançamento'})
        N630_final = N630_final[['CNPJ', 'Data Inicial', 'Data Final', 'Ano', 'Período Apuração',
                                 'Código Lançamento', 'Descrição Lançamento', 'Vlr Lançamento']]

        N670_final = pd.concat(self.listaN670).reset_index(drop=True).rename(columns={
            1: 'Código Lançamento', 2: 'Descrição Lançamento', 3: "Vlr Lançamento"})
        N670_final = N670_final[['CNPJ', 'Data Inicial', 'Data Final', 'Ano', 'Período Apuração',
                                 'Código Lançamento', 'Descrição Lançamento', 'Vlr Lançamento']]

        return {
            "L100": L100_final,
            "L300": L300_final,
            "M300": M300_final,
            "M350": M350_final,
            "N630": N630_final,
            "N670": N670_final
        }

# Exemplo de uso da classe
if __name__=='__main__':

    st.title('Processamento de Arquivos SPED')

    uploaded_files = st.file_uploader("Escolha os arquivos SPED", type=['txt'], accept_multiple_files=True)

    if uploaded_files:
        file_paths = []
        for uploaded_file in uploaded_files:
            file_path = uploaded_file.name
            with open(file_path, 'wb') as f:
                f.write(uploaded_file.getbuffer())
            file_paths.append(file_path)

        sped_processor = SpedProcessor(file_paths)
        sped_processor.processar_arquivos()
        dfs_concatenados = sped_processor.concatenar_dfs()

        # Acesso aos DataFrames processados
        L100_final = dfs_concatenados["L100"]
        L300_final = dfs_concatenados["L300"]
        M300_final = dfs_concatenados["M300"]
        M350_final = dfs_concatenados["M350"]
        N630_final = dfs_concatenados["N630"]
        N670_final = dfs_concatenados["N670"]

        st.dataframe(L100_final)
        st.dataframe(L300_final)
        st.dataframe(M300_final)
        st.dataframe(M350_final)
        st.dataframe(N630_final)
        st.dataframe(N670_final)
        # Adicione exibição dos outros DataFrames se necessário








    # '''
    # file_paths = [r'C:\Users\lauro.loyola\Desktop\JCPCalculos\limpeza_dos_dados\arquivosSPED\SPEDECF-79283065000141-20190101-20191231-20231208111202.txt',
    #             r'C:\Users\lauro.loyola\Desktop\JCPCalculos\limpeza_dos_dados\arquivosSPED\SPEDECF-79283065000141-20200101-20201231-20231208111910.txt',
    #             r'C:\Users\lauro.loyola\Desktop\JCPCalculos\limpeza_dos_dados\arquivosSPED\SPEDECF-79283065000141-20210101-20211231-20231016174350.txt',
    #             r'C:\Users\lauro.loyola\Desktop\JCPCalculos\limpeza_dos_dados\arquivosSPED\SPEDECF-79283065000141-20220101-20221231-20231114173914.txt',
    #             r'C:\Users\lauro.loyola\Desktop\JCPCalculos\limpeza_dos_dados\arquivosSPED\SPEDECF-79283065000141-20230101-20231231-20240417183332.txt'
    #             ]
    # sped_processor = SpedProcessor(file_paths)
    # sped_processor.processar_arquivos()
    # dfs_concatenados = sped_processor.concatenar_dfs()

    # # Acesso aos DataFrames processados
    # L100_final = dfs_concatenados["L100"]
    # L300_final = dfs_concatenados["L300"]
    # M300_final = dfs_concatenados["M300"]
    # M350_final = dfs_concatenados["M350"]
    # N630_final = dfs_concatenados["N630"]
    # N670_final = dfs_concatenados["N670"]

    # st.dataframe(L100_final)
    # st.dataframe(L300_final)
    # '''


'''        file_paths = [st.sidebar.file_uploader("Upload L100 Excel File", type="txt"),
                      st.sidebar.file_uploader("Upload L300 Excel File", type="txt"),
                      st.sidebar.file_uploader("Upload Lacs Excel File", type="txt"),
                      st.sidebar.file_uploader("Upload Lalur Excel File", type="txt"),
                      st.sidebar.file_uploader("Upload ECF 670 Excel File", type="txt")
                    ]
        temp_dir = tempfile.TemporaryDirectory()
        
        file_paths_temp = []
        for file in file_paths:
            temp_file_path = os.path.join(temp_dir.name, file.name)
            with open(temp_file_path, 'wb') as f:
                f.write(file.getvalue())
            file_paths_temp.append(temp_file_path)

        sped_processor = SpedProcessor(file_paths_temp)
        sped_processor.processar_arquivos()
        dfs_concatenados = sped_processor.concatenar_dfs()

        # Acesso aos DataFrames processados
        L100_final = dfs_concatenados["L100"]
        L300_final = dfs_concatenados["L300"]
        M300_final = dfs_concatenados["M300"]
        M350_final = dfs_concatenados["M350"]
        N630_final = dfs_concatenados["N630"]
        N670_final = dfs_concatenados["N670"]
'''