import streamlit as st
from io import BytesIO
from PIL import Image
from pyzbar import pyzbar
import re
from bs4 import BeautifulSoup
import requests
import math
import pandas as pd
import numpy as np
from streamlit_gsheets import GSheetsConnection
from datetime import datetime


st.set_page_config(layout="wide")

agora = datetime.now()
dia = agora.strftime("%d/%m/%Y") 

col1, col2 = st.columns(2)

def decode_qr_code(image):
    qr_codes = pyzbar.decode(image)
    decoded_messages = [qr.data.decode('utf-8') for qr in qr_codes]
    return decoded_messages

with st.form(key='revisar_casos_form'):
    
    if "decoded_message" not in st.session_state:
        st.session_state.decoded_message = None
    
    if "df" not in st.session_state:
        st.session_state.df = None
        
    if "df1" not in st.session_state:
        st.session_state.df1 = None
        
    url = st.text_input("Insira a URL da nota fiscal aqui")    
    submit_button = st.form_submit_button(label='Submeter')
    if submit_button:    
# Função principal para Upload de Imagem e Decodificação do QR code

        st.success(f"Decoded QR Code: {url}")
        print(url)
    
        headers = {'User Agent' :'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'}
        site = requests.get(url, headers=headers)
        soup = BeautifulSoup(site.content, 'html.parser')
        total_itens = soup.find('div', id='linhaTotal').get_text().strip()
        #print(total_itens)
        index = total_itens.find(':') + 1
        #print(index)
        qtde = total_itens[index:]
        #print(qtde)
    
        items = soup.find_all('span', class_='txtTit')
        nome=[]
        for item in items:
            nome.append(item.get_text().strip())

        print(nome)    

        codigos = soup.find_all('span', class_='RCod')
        cod = []
        for codigo in codigos:
            cod.append(codigo.get_text().strip().replace('Código:','').replace('\n','').replace('\t','').replace('(','').replace(')',''))

        print(cod)

        unidades = soup.find_all('span', class_='Rqtd')
        unid = []
        for unidade in unidades:
            unid.append(unidade.get_text().strip().replace("Qtde.:","").replace(',','.'))

        print(unid)

        RsUnit = []
        real_units = soup.find_all('span', class_='RvlUnit')
        for real_unit in real_units:
            RsUnit.append(real_unit.get_text().strip().replace('Vl. Unit.:\n\t\t\t\t\t\t\t\t\t\t\xa0\n\t\t\t\t\t\t\t\t\t\t','').replace(',','.'))
        print(RsUnit)

        Vtotal = []
        valores_totais = soup.find_all('span', class_='valor')
        for valor_total in valores_totais:
            Vtotal.append(valor_total.get_text().strip().replace('Vl. Unit.:\n\t\t\t\t\t\t\t\t\t\t\xa0\n\t\t\t\t\t\t\t\t\t\t','').replace(',','.'))
        print(Vtotal)

        VMax = soup.find('span', class_='txtMax').get_text().strip().replace(',','.')
        Imp_pago = soup.find('span', class_='txtObs').get_text().strip().replace(',','.')
        Empresa = soup.find('div', class_='txtTopo').get_text().strip()
        Imp = float(Imp_pago)*100/float(VMax)

        data = {
            'Dia': dia,
            'Nome do produto': nome,
            'Código do produto': cod,
            'Unidade': unid,
            'Valor da unidade': RsUnit,
            'Valor total': Vtotal
            }

        df = pd.DataFrame(data)
        st.session_state.df = df
        
        data1 = {
            'Dia': dia,
            'Empresa': Empresa,
            'Valor total nf': VMax,
            'Imposto': Imp_pago,
            'Porcentagem': Imp
        }
            
        df1 = pd.DataFrame(data1, index=[0])
        st.session_state.df1 = df1
        
        with col1:
            st.session_state.df
        
        with col2:
            st.session_state.df1
            
with st.form(key="form"):
                
    submit_button = st.form_submit_button(label='Salvar')
    if submit_button:
        url_gsheets = "https://docs.google.com/spreadsheets/d/1lFJEqM_hJl4Ry_Z15Xha2a3ia-AhETVukVFKOTqp2L4/edit?gid=0#gid=0"
        conn = st.connection("gsheets", type=GSheetsConnection)
        st.session_state['gsheets'] = conn.read(spreadsheet=url_gsheets, usecols=[0,1,2,3,4,5,6,7,8,9],ttl=0)
        st.session_state['gsheets'] = st.session_state['gsheets'].dropna(how="all")
        new_data = pd.concat([st.session_state.df,st.session_state.df1], ignore_index=True)
        updated_df = pd.concat([st.session_state['gsheets'], new_data], ignore_index=True)
        #st.session_state['df'].to_csv('dados.csv', index=False)
        st.success("Dados adicionados com sucesso!")
        #Atualizando a planilha
        conn.update(spreadsheet=url_gsheets, data=updated_df)
        st.rerun()
