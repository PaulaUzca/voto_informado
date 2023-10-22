from flask import Flask, jsonify, request
from sodapy import Socrata
from pathlib import Path
import pandas as pd

client = Socrata("www.datos.gov.co", "GZkG1KvXYiXI86YBJKHrDbhl4")

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


def display_contracts_with_number(number):
    params = {
        "$select": "nombre_entidad, id_contrato, tipo_de_contrato, modalidad_de_contratacion, fecha_de_firma, fecha_de_fin_del_contrato, valor_del_contrato, objeto_del_contrato, departamento, ciudad, urlproceso",
        "$where": f"fecha_de_firma >= '2022-10-30T00:00:00' AND (documento_proveedor = '{number}' OR identificaci_n_representante_legal = '{number}')",
        "$limit": 100
    }

    results = client.get("jbjy-vk9h", **params)
    return results

def display_entities(number):
    params2 = {
        "$select": "nombre_entidad, fecha_de_firma, count(id_contrato) as Numero_de_Contratos, sum(valor_del_contrato) as Valor_Total",
        "$where": f"documento_proveedor = '{number}' OR identificaci_n_representante_legal = '{number}'",
        "$group": "nombre_entidad, fecha_de_firma",
        "$order": "Valor_Total DESC",
        "$limit": 100
    }

    results2 = client.get("jbjy-vk9h", **params2)

    return results2

def filter_contracts(departamento):
    params2 = {
        "$select": "documento_proveedor, identificaci_n_representante_legal, nombre_representante_legal, count(id_contrato) as Numero_de_Contratos, sum(valor_del_contrato) as Valor_Total, departamento, ciudad",
        "$where": f"fecha_de_firma >= '2022-10-30T00:00:00' AND departamento= '{departamento}'",
        "$group": "documento_proveedor, identificaci_n_representante_legal, nombre_representante_legal, departamento, ciudad",
        "$limit": 100
    }

    results2 = client.get("jbjy-vk9h", **params2)

    return results2

def get_overlapping_contracts(number):
    # Assuming you've initialized your Socrata client as client somewhere
    
    # Define the query parameters to find overlapping contracts
    params3 = {
        "$select": "id_contrato, tipo_de_contrato, modalidad_de_contratacion, fecha_de_firma, fecha_de_inicio_del_contrato, fecha_de_fin_del_contrato, valor_del_contrato",
        "$where": f"(documento_proveedor = '{number}' OR identificaci_n_representante_legal = '{number}')",
        "$limit": 100
    }

    # Retrieve the contracts data based on the modified query
    results3 = client.get("jbjy-vk9h", **params3)

    # Convert to pandas DataFrame
    results_df3 = pd.DataFrame.from_records(results3)

    max_overlap = 0
    max_overlap_ids = []

    for _, contract in results_df3.iterrows():
        overlap_condition = (
            (contract['fecha_de_inicio_del_contrato'] <= results_df3['fecha_de_fin_del_contrato']) & 
            (contract['fecha_de_fin_del_contrato'] >= results_df3['fecha_de_inicio_del_contrato'])
        )
        
        overlapping_ids = results_df3[overlap_condition]['id_contrato'].tolist()
        
    if max_overlap_ids !=1:
        response = {
            "message": f"El número maximo de contratos que ha tenido esta persona al tiempo son: {max_overlap}",
            "contract_ids": max_overlap_ids
        }
    else:
        response = {
            "message: La persona solo tiene un contrato al tiempo"
        }

    
    return response
