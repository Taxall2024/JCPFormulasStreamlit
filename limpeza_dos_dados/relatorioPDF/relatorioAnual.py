import pandas as pd
import streamlit as st
import numpy as np
from io import BytesIO

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer,Image,PageBreak
from reportlab.pdfgen import canvas

texto = """
O Juros sobre Capital Próprio – JCP é uma forma de remuneração dos sócios pelo capital investido na empresa. Uma das vantagens desse tipo de remuneração está no fato de que a base de cálculo do JCP é o patrimônio líquido aplicado à variação da Taxa de Juros de Longo Prazo – TJLP, ou seja, não depende diretamente do sucesso econômico da empresa como verificado em outros tipos de remuneração.
Essa metodologia possui respaldo legal no artigo 9º, da Lei nº 9.249/1995, como disposto abaixo: 

"""
def add_background(canvas, doc):

    canvas.drawImage("limpeza_dos_dados\\relatorioPDF\\Cabecalho.png", 0, 0, width=doc.pagesize[0], height=doc.pagesize[1])


class RelatorioPDFJSCP():

    def valorTotalTrimestral(self,uploaded_file_resultados):

        resultados = pd.read_excel(uploaded_file_resultados).fillna(np.nan)
        resultados = resultados.apply(lambda x: x.dropna().reset_index(drop=True))
        resultados = resultados.iloc[24:,[0,1,3,5,7,9,11,13,15,17,19,21,23,25,27,29,31,33,35,37,39]]
        
        colunas = [1,3,5,7,9,11,13,15,17,19,21,23,25,27,29,31,33,35,37,39]
        for col in colunas:
            resultados[col] = resultados[col].str.replace('.','_').str.replace(',','.').str.replace('_','').astype(float)
            
        resultados.at[25,'Value_2019'] = resultados.at[25,1]+resultados.at[25,3]+resultados.at[25,5]+resultados.at[25,7]
        resultados.at[24,'Value_2019'] = resultados.at[24,1]+resultados.at[24,3]+resultados.at[24,5]+resultados.at[24,7]
        
        resultados.at[25,'Value_2020'] = resultados.at[25,9]+resultados.at[25,11]+resultados.at[25,13]+resultados.at[25,15]
        resultados.at[24,'Value_2020'] = resultados.at[24,9]+resultados.at[24,11]+resultados.at[24,13]+resultados.at[24,15]  

        resultados.at[25,'Value_2021'] = resultados.at[25,17]+resultados.at[25,19]+resultados.at[25,21]+resultados.at[25,23]
        resultados.at[24,'Value_2021'] = resultados.at[24,17]+resultados.at[24,19]+resultados.at[24,21]+resultados.at[24,23]   

        resultados.at[25,'Value_2022'] = resultados.at[25,25]+resultados.at[25,27]+resultados.at[25,29]+resultados.at[25,31]
        resultados.at[24,'Value_2022'] = resultados.at[24,25]+resultados.at[24,27]+resultados.at[24,29]+resultados.at[24,31] 

        resultados.at[25,'Value_2023'] = resultados.at[25,33]+resultados.at[25,35]+resultados.at[25,37]+resultados.at[25,39]
        resultados.at[24,'Value_2023'] = resultados.at[24,33]+resultados.at[24,35]+resultados.at[24,37]+resultados.at[24,39] 

        resultados = resultados.iloc[:,[0,-5,-4,-3,-2,-1]].rename(columns={0:''}).reset_index(drop='index')

       
        valorTotal = resultados.iloc[-1,:]
        valorImposto = resultados.iloc[-2,:]

        self.valorTotalPeriodo = "{:,.2f}".format(round(sum([valorTotal['Value_2019'], valorTotal['Value_2020'],
                                                       valorTotal['Value_2021'], valorTotal['Value_2022'],
                                                       valorTotal['Value_2023'],]), 2)).replace('.','_').replace(',','.').replace('_',',')
        
        valor_somado = round(resultados[['Value_2019', 'Value_2020', 'Value_2021', 'Value_2022', 'Value_2023']].sum().sum(), 2)
        self.valorAntesImpostos = "{:,.2f}".format(valor_somado, grouping=True).replace('.','_').replace(',','.').replace('_',',')
                        
        self.valorImpostos = "{:,.2f}".format(sum([valorImposto['Value_2019'],valorImposto['Value_2020'],
                                                               valorImposto['Value_2021'],valorImposto['Value_2022'],
                                                               valorImposto['Value_2023'],]), grouping=True).replace('.','_').replace(',','.').replace('_',',')

        
        self.tabelaFinalDf = resultados.rename(columns={
                                                                      'Value_2019':'2019',
                                                                      'Value_2020':'2020',
                                                                      'Value_2021':'2021',
                                                                      'Value_2022':'2022',
                                                                      'Value_2023':'2023',})
        
        self.tabelaFinalDf['Total'] = sum([self.tabelaFinalDf['2019'],
                                          self.tabelaFinalDf['2020'],
                                          self.tabelaFinalDf['2021'],
                                          self.tabelaFinalDf['2022'],
                                          self.tabelaFinalDf['2023']])
        
        colunasParaFormatar = ['2019','2020','2021','2022','2023','Total']
        for col in colunasParaFormatar:
            self.tabelaFinalDf[col] = self.tabelaFinalDf[col].apply(lambda x: "{:,.2f}".format( x, grouping=True).replace('.','_').replace(',','.').replace('_',','))
        


    
    def valorTotal(self,uploaded_file_resultados):
        colunas = ['Value_2019','Value_2020','Value_2021','Value_2022','Value_2023']
        
        resultados = pd.read_excel(uploaded_file_resultados).fillna(np.nan)
        resultados = resultados.apply(lambda x: x.dropna().reset_index(drop=True))
        resultados = resultados.iloc[24:,:]
        
        for col in colunas:
            resultados[col] = resultados[col].replace('.','_').replace(',','.').replace('_',',').astype(float)
            
        valorTotal = resultados.iloc[-1,:]
        valorImposto = resultados.iloc[-2,:]


        self.valorTotalPeriodo = "{:,.2f}".format(round(sum([valorTotal['Value_2019'],valorTotal['Value_2020'],
                                                               valorTotal['Value_2021'],valorTotal['Value_2022'],
                                                               valorTotal['Value_2023'],]),2), grouping=True).replace('.','_').replace(',','.').replace('_',',')
        
        valor_somado = round(resultados[['Value_2019', 'Value_2020', 'Value_2021', 'Value_2022', 'Value_2023']].sum().sum(), 2)
        self.valorAntesImpostos = "{:,.2f}".format(valor_somado).replace('.','_').replace(',','.').replace('_',',')
                        
        valor_impuestos_sum = round(sum([
            valorImposto['Value_2019'],valorImposto['Value_2020'],valorImposto['Value_2021'],
            valorImposto['Value_2022'],valorImposto['Value_2023'],]), 2)

        self.valorImpostos = "{:,.2f}".format(valor_impuestos_sum).replace('.', '_').replace(',', '.').replace('_', ',')
        resultados.at[24,'Operation_2019'] = 'Redução no IRPJ/CSLL'
        
        self.tabelaFinalDf = resultados.iloc[:,[0,1,3,5,7,9]].rename(columns={'Operation_2019':'',
                                                                      'Value_2019':'2019',
                                                                      'Value_2020':'2020',
                                                                      'Value_2021':'2021',
                                                                      'Value_2022':'2022',
                                                                      'Value_2023':'2023',})
        
        
        self.tabelaFinalDf['Total'] = sum([self.tabelaFinalDf['2019'],
                                          self.tabelaFinalDf['2020'],
                                          self.tabelaFinalDf['2021'],
                                          self.tabelaFinalDf['2022'],
                                          self.tabelaFinalDf['2023']])
        
        colunasParaFormatar = ['2019','2020','2021','2022','2023','Total']
        for col in colunasParaFormatar:
            self.tabelaFinalDf[col] = self.tabelaFinalDf[col].map(lambda x: "{:,.2f}".format(x).replace('.','_').replace(',','.').replace('_',','))
       


    def create_pdf(self,nomeEmpresa,aliquota,observacoesDoAnalista,textoData):
        filename = 'Relatorio JCP.pdf'
        pdf_buffer = BytesIO()
        doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)
        story = []
        story.append(Spacer(1, 25))
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            name="Title",
            fontSize=18,  # Increase font size
            spaceAfter=20,  # Add space after the title
            alignment=1,  # Center the title
            fontName="Helvetica-Bold",  # Bold font
        )

        # Add title
        story.append(Paragraph("<b>Juros sobre Capital Próprio – JCP</b>", title_style))

        # Add a spacer between the title and the rest of the text
        story.append(Spacer(1, 25))

        styles = getSampleStyleSheet()
        texto = """
        O Juros sobre Capital Próprio – JCP é uma forma de remuneração dos sócios pelo capital investido na empresa. 
        Uma das vantagens desse tipo de remuneração está no fato de que a base de cálculo do JCP é o patrimônio 
        líquido aplicado à variação da Taxa de Juros de Longo Prazo – TJLP, ou seja, não depende diretamente do 
        sucesso econômico da empresa como verificado em outros tipos de remuneração.
        Essa metodologia possui respaldo legal no artigo 9º, da Lei nº 9.249/1995, como disposto abaixo:
        """
        story.append(Paragraph(texto, styles["Normal"]))  
        story.append(Spacer(1, 12))
        img_path = "limpeza_dos_dados\\relatorioPDF\\RespaldoJuridico1.png"
        img = Image(img_path, width=3.8*inch, height=0.9*inch)
        img.hAlign = 'RIGHT'
        story.append(img) 
        
        story.append(Spacer(1, 12)) 

        styles = getSampleStyleSheet()
        texto = """
        Consoante a este entendimento, a jurisprudência do Conselho Administrativo de Recursos Fiscais – CARF e
        dos Tribunais Superiores vêm sedimentando o entendimento de que é juridicamente viável o 
        uso do JCP como forma de remuneração dos sócios, como observa-se a seguir:  
        """
        story.append(Paragraph(texto, styles["Normal"]))

        story.append(Spacer(1, 12))
        img_path = "limpeza_dos_dados\\relatorioPDF\\RespaldoJuridico2.png"
        img = Image(img_path, width=3.8*inch, height=3.5*inch)
        img.hAlign = 'RIGHT'
        story.append(img) 
        
        story.append(Spacer(1, 12)) 

        styles = getSampleStyleSheet()
        texto = """
        Para mais, cumpre esclarecer que o uso de JCP referente a períodos 
        anteriores é plenamente possível conforme decisão proferida pelo CARF:  
        """
        story.append(Paragraph(texto, styles["Normal"]))

        story.append(PageBreak())

        story.append(Spacer(1, 12))
        img_path = "limpeza_dos_dados\\relatorioPDF\\RespaldoJuridico3.png"
        img = Image(img_path, width=3.8*inch, height=4.2*inch)
        img.hAlign = 'RIGHT'
        story.append(img) 
        
        story.append(Spacer(1, 12)) 

        styles = getSampleStyleSheet()
        texto = """
        Na esfera judicial, o uso de JCP retroativo possui jurisprudência favorável. Em 20/06/2023, o Superior Tribunal de Justiça – STJ finalizou o julgamento do REsp nº 1.971.537/SP, em que se discute a possibilidade de dedução dos juros sobre o capital próprio (JCP) retroativos da base de cálculo do IRPJ e da CSLL. Na oportunidade,
        houve a pacificação da tese de que é possível deduzir do lucro real os valores de JCP, ainda que tenham sido apurados em exercícios anteriores.
        """
        story.append(Paragraph(texto, styles["Normal"]))
        story.append(Spacer(1, 12)) 
        styles = getSampleStyleSheet()
        texto = """
            A principal vantagem trazida pelo uso de JCP é a redução da carga tributária da empresa, pois é considerado como despesa das organizações
            por ser descontado antes do lucro líquido, sendo assim dedutível do IRPJ e da CSLL, gerando uma economia tributária de 34% sobre o valor apurado de JCP.
        """
        story.append(Paragraph(texto, styles["Normal"]))

        story.append(Spacer(1, 12)) 
        styles = getSampleStyleSheet()
        texto = """
        Veja que, mesmo com a tributação de IRRF de 15%, ainda há economia futura.
        """
        story.append(Paragraph(texto, styles["Normal"]))
        
        story.append(Spacer(1, 12)) 
        styles = getSampleStyleSheet()
        texto = """
        Ademais, o JCP, considerado como despesa de remuneração ao sócio, irá trazer adicionalmente impactos positivos na apuração do IRPJ e da CSLL.
        Com a aplicação dessa inovação, o crédito identificado irá aumentar o saldo negativo, que poderá ser utilizado na compensação de débitos futuros.
        """
        story.append(Paragraph(texto, styles["Normal"]))

        story.append(PageBreak())

        story.append(Spacer(1, 12)) 
        styles = getSampleStyleSheet()
        texto = f"""
            Ao analisar a ECF, de abril de 2019 a dezembro de 2023 constatou-se que a  <font size="14" color="black"><b>{nomeEmpresa}</b></font>  não utilizou a metodologia do JCP como fonte de remuneração 
            dos sócios. 
            Diante disso, com a aplicação dessa inovação, a empresa observará um ganho econômico, de abril de 2019 a dezembro de 2023, 
            de aproximadamente R$ <font size="12" color="black"><b>{self.valorAntesImpostos}</b></font>, referente a dedução de IRPJ/CSLL de {aliquota}% sobre o JCP apurado.
            Lembrando que, com a utilização desta metodologia, deverá ser recolhido, a título de Imposto de Renda Retido na Fonte – IRRF e 
            multa moratória de 20%  o significa cerca de R$ <font size="12" color="black"><b>{self.valorImpostos}</b></font>. Ou seja, mesmo com a dedução dos impostos devidos, essa metodologia trará ganho 
            econômico de aproximadamente R$ <font size="12" color="green"><b>{self.valorTotalPeriodo}</b></font>, evidenciado abaixo:

        """
        story.append(Paragraph(texto, styles["Normal"]))

        story.append(Spacer(1, 32)) 

        col_widths = [2.1*inch, 1*inch, 1*inch, 1*inch, 1*inch, 1*inch,1*inch]
        data = [self.tabelaFinalDf.columns.tolist()] + self.tabelaFinalDf.values.tolist()

        table = Table(data,colWidths=col_widths)
        table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.transparent),
                                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                                ('ALIGN', (0, 0), (1, -1), 'CENTER'),
                                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                               # ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),  # Definindo a fonte
                                ('FONTSIZE', (0, 0), (-1, -1), 9), 
                                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                                ('BACKGROUND', (0, 1), (-1, -1), colors.transparent),
                                ('GRID', (0, 0), (-1, -1), 1, colors.black)]))
  
        story.append(table)

        story.append(Spacer(1, 32)) 

        styles = getSampleStyleSheet()
        texto = f"""
        Além dos ganhos pretéritos, ressalte-se que essa metodologia pode ser utilizada nas próximas apurações, gerando economia em escala. Para o uso correto do JCP,
          deve-se seguir as orientações contidas neste relatório e durante a execução do contrato realizado pela equipe técnica da Tax All.

        """
        story.append(Paragraph(texto, styles["Normal"]))

        story.append(Spacer(1, 12))

        story.append(Spacer(1, 32)) 

        styles = getSampleStyleSheet()
        texto = f"""
               <font size="14" color="black"><b>Observações da Tax All:</b></font>   {observacoesDoAnalista}

        """
        story.append(Paragraph(texto, styles["Normal"]))

        story.append(Spacer(1, 42))   
        styles = getSampleStyleSheet()
        texto = f"""
               <font size="16" color="black"><b>Total da Oportunidade : </b></font> <font size="16" color="orange"><b>{self.valorTotalPeriodo}</b></font>     

        """
        story.append(Paragraph(texto, styles["Normal"]))

        story.append(Spacer(1, 12))   

        story.append(PageBreak())

        story.append(Spacer(1, 12))
        story.append(Paragraph("<b>CONCLUSÃO</b>", title_style))

        story.append(Spacer(1, 12))
        styles = getSampleStyleSheet()
        texto = f"""
            Na revisão fiscal foi possível identificar, também, créditos não utilizados em sua totalidade e com a orientação deste relatório,
            proporcionará economia de caixa.

        """
        story.append(Paragraph(texto, styles["Normal"]))

        story.append(Spacer(1, 12))

        styles = getSampleStyleSheet()
        texto = f"""
            As inovações tributárias apresentadas pela Tax All podem ser aplicadas retroativamente – nos últimos 5
            (cinco) anos, conforme prazo do CTN – e, também, nos 60 meses futuros, gerando economia e fluxo de caixa para a empresa. 

        """
        story.append(Paragraph(texto, styles["Normal"]))

        story.append(Spacer(1, 12))

        styles = getSampleStyleSheet()
        texto = f"""
            Desta forma, as inovações tributárias e créditos identificados pela
            Tax All podem ser sintetizados em dois cenários, conforme explicitado abaixo:. 

        """
        story.append(Paragraph(texto, styles["Normal"]))

        story.append(Spacer(1, 32))  

        story.append(Paragraph("<b>INOVAÇÕES TRIBUTÁRIAS </b>",ParagraphStyle(
            name="Title",
            fontSize=15,  # Increase font size
            spaceAfter=15,  # Add space after the title
            alignment=1,  # Center the title
            fontName="Helvetica-Bold",  # Bold font
        )))
        story.append(Spacer(1, 32))  

        story.append(Paragraph(f"<b>1)	Juros sobre Capital Próprio – JCP de aproximadamente :  </b>",ParagraphStyle(
            name="Title", 
            fontSize=12,  # Increase font size
            spaceAfter=15,  # Add space after the title
            alignment=1,  # Center the title
            fontName="Helvetica-Bold",  # Bold font
        )))
        story.append(Paragraph(f"<b><font size='20' color='orange'>{self.valorTotalPeriodo}</font> </b>",ParagraphStyle(
            name="Title", 
            fontSize=30,  # Increase font size
            spaceAfter=15,  # Add space after the title
            alignment=1,  # Center the title
            fontName="Helvetica-Bold",  # Bold font
        )))
        story.append(Spacer(1, 25))

        styles = getSampleStyleSheet()
        texto = f"""
                Por fim, considerando os documentos/informações disponibilizadas, foi apurado crédito de aproximadamente R${self.valorTotalPeriodo} , valor que será atualizado no momento de sua utilização. 
        """
        story.append(Paragraph(texto, styles["Normal"]))

        story.append(Spacer(1, 32)) 

        styles = getSampleStyleSheet()
        texto = f"""
            Há que se ressaltar ainda a economia em escala, por prazo indeterminado, 
            uma vez que este estudo de Revisão Fiscal altera a forma de tributação atual, criando fluxo financeiro imediato e, também, no médio e longo prazo. 
         """
        story.append(Paragraph(texto, styles["Normal"]))

        story.append(Spacer(1, 32))

        styles = getSampleStyleSheet()
        textoData = f"""
            Brasília/DF, {textoData}
         """
        story.append(Paragraph(textoData, styles["Normal"]))

        story.append(Spacer(1, 24))  

        img_path = "limpeza_dos_dados\\relatorioPDF\\Assinaturas.png"
        img = Image(img_path, width=5.8*inch, height=1.9*inch)
        img.hAlign = 'CENTER'
        story.append(img) 
        # Add the background image by wrapping the build call
        doc.build(story, onFirstPage=add_background, onLaterPages=add_background)
        pdf_buffer.seek(0)
        return pdf_buffer
   
 
if __name__=='__main__':

    st.set_page_config(layout='wide')
    col1,col2,col3,col4,col5,col6 = st.columns(6)

    uploaded_file_resultados = st.sidebar.file_uploader("Upload arquivo de resultado", type="xlsx")
    if uploaded_file_resultados is not None:

        with col1:
            nomeDaEmepresa = st.text_input('Digite o nome da empresa')
            aliquotaImposto = st.text_input('Digite o valor da alíquota de imposto, ex(24,34)')
            dataAssinatura=st.text_input('Escreva a data da assinatura do contrato, ex. 23 de agosto de 2024 ')

        observacoesDoAnlista = st.text_input('Digite aqui suas observações :')    
        pdf = RelatorioPDFJSCP()
        pdf.valorTotal(uploaded_file_resultados)
        pdf.create_pdf(nomeDaEmepresa,aliquotaImposto,observacoesDoAnlista,dataAssinatura)




