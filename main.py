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
import subprocess
import os

if os.getenv('HOME') == '/home/adminuser':
    subprocess.call(['./setup.sh'])

def decode_qr_code(frame):
    """
    Decodes QR codes in the given image frame.

    Parameters:
    frame (numpy.ndarray): The image frame to scan for QR codes.

    Returns:
    list: A list of decoded QR code data.
    """
    decoded_objects = pyzbar.decode(frame)
    qr_codes = [obj.data.decode('utf-8') for obj in decoded_objects]
    return qr_codes


def scan_qr_code():
    st.title("QR Code Scanner")
    st.write("Click the button below to start the camera and scan a QR code.")

    # Initialize session state for control buttons and decoded message
    if "scanning" not in st.session_state:
        st.session_state.scanning = False

    if "decoded_message" not in st.session_state:
        st.session_state.decoded_message = None

    def start_scanning():
        st.session_state.scanning = True

    def stop_scanning():
        st.session_state.scanning = False

    if not st.session_state.scanning:
        if st.button('Start Scanning', key='start'):
            start_scanning()

    if st.session_state.scanning:
        cap = cv2.VideoCapture(0)
        stframe = st.empty()

        while st.session_state.scanning:
            ret, frame = cap.read()
            if not ret:
                st.write("Failed to capture image.")
                break

            qr_codes = decode_qr_code(frame)

            # Display the frame
            stframe.image(frame, channels="BGR")

            # Display the decoded QR codes if it's a new message
            if qr_codes:
                if st.session_state.decoded_message != qr_codes[0]:
                    st.session_state.decoded_message = qr_codes[0]
                    st.success(f"Decoded QR Code: {qr_codes[0]}")
                    break

        if st.button('Stop Scanning', key='stop', on_click=stop_scanning):
            cap.release()
            cv2.destroyAllWindows()

st.write('''
         <h1>Escanei o QR code</h1>
         ''',unsafe_allow_html=True)

scan_qr_code()

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