import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(layout="wide")

col1, col2, col3 = st.columns(3)

st.write('<h1>Gastos totais por estabelecimento</h1>', unsafe_allow_html=True)

if 'gsheets' not in st.session_state:
    url = "https://docs.google.com/spreadsheets/d/1lFJEqM_hJl4Ry_Z15Xha2a3ia-AhETVukVFKOTqp2L4/edit?gid=0#gid=0"
    conn = st.connection("gsheets", type=GSheetsConnection)
    existing_data = conn.read(spreadsheet=url, usecols=[0,1,2,3,4,5],ttl=5)
    existing_data2 = conn.read(spreadsheet=url, usecols=[0,6,7,8,9,10],ttl=5)
    
    existing_data = existing_data.dropna(how="any") 
    existing_data2 = existing_data2.dropna(how="any") 
    df = pd.DataFrame(existing_data)
    df1 = pd.DataFrame(existing_data2)
    
    with st.container():
        y = np.array(df1['Valor total nf'])
        mylabels = df1['Empresa']
    
        fig, ax = plt.subplots()
        ax.pie(y, labels=mylabels)
    
        st.pyplot(fig)
        
    #with st.container():
    #    with col2:
    #        df
    #    with col3:
    #        df1
