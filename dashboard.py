import streamlit as st
import requests
import pandas as pd

st.title("WSN Real-Time Fault Detection")

nodes = requests.get("http://127.0.0.1:5000/nodes").json()

if nodes:
    df = pd.DataFrame(nodes)
    st.subheader("Live Sensor Data")
    st.dataframe(df)

    st.subheader("Energy Distribution")
    st.bar_chart(df["energy"])
else:
    st.write("Waiting for sensor data...")