from flask import Flask, jsonify, request
from sodapy import Socrata
from pathlib import Path
import pandas as pd

client = Socrata("www.datos.gov.co", None)

THIS_FOLDER = Path(__file__).parent.resolve()
csv_file = THIS_FOLDER / 'static/data_nice2.csv'
df = pd.read_csv(csv_file, encoding = "iso-8859-1")

def cargosAspirado(Nombre):

    # Filter the DataFrame for the given 'Nombre'
    filtered_df = df[df["nombresApellidos"] == Nombre]

    # If the name exists in the DataFrame, return the corresponding 'Cargo Counts' value
    if not filtered_df.empty:
        cargo_counts = filtered_df['Cargo Counts'].iloc[0]
        print(filtered_df['Cargo Counts'])
        print(cargo_counts)
        return cargo_counts
    else:
        return []
    

    """ if not filtered_df.empty:
        cargo_counts = filtered_df['Cargo Counts'].iloc[0]
        return jsonify(cargo_counts)
    else:
        return jsonify({"error": "Nombre not found in the DataFrame"}), 404
 """