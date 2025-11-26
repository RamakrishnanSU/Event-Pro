import pandas as pd
import streamlit as st
from streamlit_gsheets import GSheetsConnection

class DataHandler:
    def __init__(self):
        try:
            self.conn = st.connection("gsheets", type=GSheetsConnection)
        except Exception as e:
            st.error(f"⚠️ Connection Error: {e}")

    def load_data(self, worksheet_name):
        try:
            df = self.conn.read(worksheet=worksheet_name, ttl="0")
            return df if not df.empty else pd.DataFrame()
        except Exception as e:
            return pd.DataFrame()

    def save_data(self, data, worksheet_name):
        try:
            df = pd.DataFrame(data if isinstance(data, list) else [data])
            self.conn.update(worksheet=worksheet_name, data=df)
            return "Saved to Cloud"
        except Exception as e:
            return f"Error saving: {e}"

    def delete_data(self, worksheet_name, column_name, value_to_delete):
        """Removes rows where column_name matches value_to_delete"""
        try:
            df = self.load_data(worksheet_name)
            if df.empty: return "Sheet is empty"
            
            # 1. Normalize the column to standard Integers (removes .0 issues)
            # Coerce errors turns bad data into NaN, then we fill with 0, then make int, then string
            df[column_name] = pd.to_numeric(df[column_name], errors='coerce').fillna(0).astype(int).astype(str)
            
            # 2. Normalize the value to delete
            val_str = str(int(value_to_delete))
            
            # 3. Filter
            df = df[df[column_name] != val_str]
            
            self.conn.update(worksheet=worksheet_name, data=df)
            return "Deleted"
        except Exception as e:
            return f"Error deleting: {e}"
