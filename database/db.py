import sqlite3

DB = "wsn.db"


def connect():
    return sqlite3.connect(DB, check_same_thread=False)


def init_db():

    conn = connect()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS sensor_data(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        node_id INTEGER,
        temperature REAL,
        humidity REAL,
        pressure REAL,
        light REAL,
        energy REAL,
        packet_loss REAL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS faults(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        node_id INTEGER,
        sensor TEXT,
        fault_type TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()


def insert_sensor(node):

    conn = connect()
    c = conn.cursor()

    c.execute("""
    INSERT INTO sensor_data
    (node_id,temperature,humidity,pressure,light,energy,packet_loss)
    VALUES(?,?,?,?,?,?,?)
    """, (
        node["node_id"],
        node["temperature"],
        node["humidity"],
        node["pressure"],
        node["light"],
        node["energy"],
        node["packet_loss"]
    ))

    conn.commit()
    conn.close()


def insert_fault(node_id, sensor, fault):

    conn = connect()
    c = conn.cursor()

    c.execute("""
    INSERT INTO faults(node_id,sensor,fault_type)
    VALUES(?,?,?)
    """, (node_id, sensor, fault))

    conn.commit()
    conn.close()