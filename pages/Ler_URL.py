import streamlit as st
import pyqrcode
from io import BytesIO
from PIL import Image
import cv2
from pyzbar import pyzbar
import re
from bs4 import BeautifulSoup
import requests
import math
import pandas as pd
import numpy as np
import subprocess
import os


st.set_page_config(layout="wide")

def decode_qr_code(image):
    qr_codes = pyzbar.decode(image)
    decoded_messages = [qr.data.decode('utf-8') for qr in qr_codes]
    return decoded_messages
    
# Função principal para Upload de Imagem e Decodificação do QR code
if "decoded_message" not in st.session_state:
    st.session_state.decoded_message = None

nfe_url = st.text_input("Insira a URL da nota fiscal aqui")

if nfe_url:
    nfe_url = st.session_state_decoded_message

if st.session_state.decoded_message:
    url = st.session_state.decoded_message
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
        'Nome do produto': nome,
        'Código do produto': cod,
        'Unidade': unid,
        'Valor da unidade': RsUnit,
        'Valor total': Vtotal
        }

    df = pd.DataFrame(data)
    df
    
    data1 = {
        'Empresa': Empresa,
        'Valor total': VMax,
        'Imposto': Imp_pago,
        'Porcentagem': Imp
    }
    
    df1 = pd.DataFrame(data1, index=[0])
    df1