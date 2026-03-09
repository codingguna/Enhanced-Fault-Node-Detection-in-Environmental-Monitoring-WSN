import streamlit as st
import requests
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from streamlit_autorefresh import st_autorefresh

SERVER = "http://127.0.0.1:5000"

st.set_page_config(layout="wide")

st.title("Environmental Monitoring WSN System")

# auto refresh every 5 seconds
st_autorefresh(interval=5000, key="refresh")

tab1, tab2 = st.tabs(["Monitoring Dashboard", "Data Injection"])

# -------------------------------------------------
# TAB 1 : MONITORING DASHBOARD
# -------------------------------------------------

with tab1:

    try:
        data = requests.get(f"{SERVER}/nodes").json()
    except:
        st.error("Server not running")
        st.stop()

    if not data:
        st.warning("Waiting for sensor data...")
        st.stop()

    df = pd.DataFrame(data)

    # ------------------------------------------------
    # TOP METRICS
    # ------------------------------------------------

    total_nodes = len(df)
    fault_nodes = len(df[df["status"] == "FAULT"])
    active_nodes = total_nodes
    health = int(((total_nodes - fault_nodes) / total_nodes) * 100)

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Total Nodes", total_nodes)
    c2.metric("Active Nodes", active_nodes)
    c3.metric("Fault Nodes", fault_nodes)
    c4.metric("Network Health", f"{health}%")

    st.divider()

    # ------------------------------------------------
    # NETWORK MAP + FAULT ALERTS
    # ------------------------------------------------

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("Network Map")

        G = nx.Graph()

        for node in df["node_id"]:
            G.add_node(node)

        for i in range(len(df)-1):
            G.add_edge(df["node_id"][i], df["node_id"][i+1])

        pos = nx.spring_layout(G)

        colors = []

        for _, row in df.iterrows():

            if row["status"] == "FAULT":
                colors.append("red")
            else:
                colors.append("green")

        fig, ax = plt.subplots()

        nx.draw(G, pos, node_color=colors, with_labels=True, ax=ax)

        st.pyplot(fig)

    with col2:

        st.subheader("Fault Alerts")

        faults = df[df["status"] == "FAULT"]

        if len(faults) > 0:
            st.error(faults[["node_id", "fault"]])
        else:
            st.success("No faults detected")

    st.divider()

    # ------------------------------------------------
    # NODE TABLE + BATTERY CHART
    # ------------------------------------------------

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("Live Node Table")

        st.dataframe(df)

    with col2:

        st.subheader("Battery Levels")

        st.bar_chart(df.set_index("node_id")["energy"])

    st.divider()

    # ------------------------------------------------
    # SENSOR CHART + FAULT STATS
    # ------------------------------------------------

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("Temperature Chart")

        st.line_chart(df.set_index("node_id")["temperature"])

    with col2:

        st.subheader("Fault Statistics")

        fault_counts = df["fault"].value_counts()

        if len(fault_counts) > 1:
            st.bar_chart(fault_counts)
        else:
            st.write("No faults recorded")

    st.divider()

    # ------------------------------------------------
    # FAULT TIMELINE
    # ------------------------------------------------

    st.subheader("Fault Timeline")

    faults = df[df["status"] == "FAULT"]

    if len(faults) > 0:
        st.table(faults[["node_id", "fault"]])
    else:
        st.write("No faults in timeline")


# -------------------------------------------------
# TAB 2 : DATA INJECTION PANEL
# -------------------------------------------------

with tab2:

    st.subheader("Node Data Injection Panel")

    node_id = st.number_input("Node ID", 0, 100, 1)

    temperature = st.number_input("Temperature", value=28.0)
    humidity = st.number_input("Humidity", value=65.0)
    pressure = st.number_input("Pressure", value=1012.0)
    light = st.number_input("Light", value=300.0)

    energy = st.number_input("Energy", value=90.0)
    packet_loss = st.number_input("Packet Loss", value=0.01)

    mode = st.radio(
        "Data Type",
        ["Normal Data", "Fault Data"]
    )

    if mode == "Fault Data":

        fault_type = st.selectbox(
            "Fault Type",
            [
                "Temperature Outlier",
                "Battery Failure",
                "Communication Failure"
            ]
        )

        if fault_type == "Temperature Outlier":
            temperature = 80

        if fault_type == "Battery Failure":
            energy = 5

        if fault_type == "Communication Failure":
            packet_loss = 0.8

    data = [{
        "node_id": node_id,
        "temperature": temperature,
        "humidity": humidity,
        "pressure": pressure,
        "light": light,
        "energy": energy,
        "packet_loss": packet_loss
    }]

    if st.button("Send Data"):

        requests.post(
            f"{SERVER}/data",
            json=data
        )

        st.success("Data sent to server")