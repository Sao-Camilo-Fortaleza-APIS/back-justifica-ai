import pyodbc
import cx_Oracle
import os
from dotenv import load_dotenv
load_dotenv()


USER_ORA = os.getenv("ORACLE_USER")
PASS_ORA = os.getenv("ORACLE_PASS")
IP_CONNECT_ORA = os.getenv("ORACLE_HOST")
PORT_DB_ORA = os.getenv("ORACLE_PORT")
SID_ORA = os.getenv("ORACLE_SID")
INSTANTCLIENT_ORA = os.getenv("INSTANTCLIENT")

IP_CONNECT_SQL_SERV = os.getenv("SQL_SERVER")
USER_SQL_SERV = os.getenv("SQL_SERVER_USER")
PASS_SQL_SERV = os.getenv("SQL_SERVER_PASS")
DB_SQL_SERV = os.getenv("SQL_SERVER_DATABASE")

lib = cx_Oracle.init_oracle_client(INSTANTCLIENT_ORA)

def connect_oracle_bd():
    try:
        connection = cx_Oracle.connect(f"{USER_ORA}/{PASS_ORA}@{IP_CONNECT_ORA}:{PORT_DB_ORA}/{SID_ORA}")
    except Exception as e:
        return str(e),500
    except cx_Oracle.DatabaseError as ebd:
        return str(ebd.args),500
    return connection


def connect_sql_server_bd():
    try:
        connection = pyodbc.connect(f'DRIVER={{SQL Server}};SERVER={IP_CONNECT_SQL_SERV};DATABASE={DB_SQL_SERV};UID={USER_SQL_SERV};PWD={PASS_SQL_SERV}')
    except Exception as e:
        return str(e), 300
    except pyodbc.DatabaseError as ebd:
        return str(ebd.args),500
    return connection
