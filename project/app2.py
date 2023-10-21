from flask import Flask, jsonify, request
from change_dataset import remove_nan
import pandas as pd
from pathlib import Path
from sodapy import Socrata


app = Flask(__name__)

THIS_FOLDER = Path(__file__).parent.resolve()
csv_file = THIS_FOLDER / 'static/data_nice2.csv'
df = pd.read_csv(csv_file, encoding = "iso-8859-1")

#Sin los cargos de juntas administradoras locales porque no nos vamos a poner a buscar por comuna
df = df[df['Descripción de la Corporación/Cargo'] != 'JUNTAS ADMINISTRADORAS LOCALES']
df.fillna('', inplace=True)
df['nombresApellidos'] = df['Primer Nombre'] + ' '  +df['Segundo Nombre'] + ' ' + df['Primer Apellido'] + ' ' + df['Segundo Apellido']

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/departamentos')
def get_departamentos():
    departamentos = remove_nan(df['Descripción del Departamento'].unique())

    response = jsonify(message = departamentos)
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response

@app.route('/municipios')
def get_municipios():
    departamento = request.args.get('departamento') 
    cargo = request.args.get('cargo') 
    municipios = remove_nan(df[df['Descripción del Departamento'] == departamento][df['Descripción de la Corporación/Cargo'] == cargo]
                            ['Descripción del Municipio'].unique())
    response = jsonify(municipios)
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response

@app.route('/cargos')
def get_cargos():
    departamento = request.args.get('departamento') 
    cargos = remove_nan(df[df['Descripción del Departamento'] == departamento]['Descripción de la Corporación/Cargo'].unique())
    response = jsonify(cargos)
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response

@app.route('/consultar')
def example():
    departamento = request.args.get('departamento') 
    cargo = request.args.get('cargo')  
    municipio = request.args.get('municipio') 

    if municipio == '':
        c = df[(df['Descripción del Departamento'] == departamento) & (df['Descripción de la Corporación/Cargo'] == cargo)]
    else:
        c = df[(df['Descripción del Departamento'] == departamento) & (df['Descripción de la Corporación/Cargo'] == cargo) & (df['Descripción del Municipio'] == municipio)]
        
    if c.empty == False:
        response =  jsonify(c['nombresApellidos'].values.tolist())
    else:
        response =  []
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response



# ROUTES PARAMS CONTRACTS

# Socrata client initialization
client = Socrata("www.datos.gov.co", None)




@app.route('/cantidadAspirado/<string:Nombre>')
def cargosAspirado(Nombre):

    # Filter the DataFrame for the given 'Nombre'
    filtered_df = df[df["nombresApellidos"] == Nombre]

    # If the name exists in the DataFrame, return the corresponding 'Cargo Counts' value
    if not filtered_df.empty:
        cargo_counts = filtered_df['Cargo Counts'].iloc[0]
        return jsonify(cargo_counts)
    else:
        return jsonify({"error": "Nombre not found in the DataFrame"}), 404



# This is the QUERY that give contracts in dates bigger that 2022-10-30
@app.route('/contracts/<int:number>')
def display_contracts_with_number(number):
    params = {
        "$select": "nombre_entidad, id_contrato, tipo_de_contrato, modalidad_de_contratacion, fecha_de_firma, fecha_de_fin_del_contrato, valor_del_contrato, objeto_del_contrato, departamento, ciudad, urlproceso",
        "$where": f"fecha_de_firma >= '2022-10-30T00:00:00' AND (documento_proveedor = '{number}' OR identificaci_n_representante_legal = '{number}')",
        "$limit": 100
    }

    results = client.get("jbjy-vk9h", **params)
    return jsonify(results)



# This QUERY shows all the contracts that the candidate has with the differents entities
@app.route('/entities/<int:number>')
def display_entities(number):
    params2 = {
        "$select": "nombre_entidad, count(id_contrato) as Numero_de_Contratos, sum(valor_del_contrato) as Valor_Total",
        "$where": f"documento_proveedor = '{number}' OR identificaci_n_representante_legal = '{number}'",
        "$group": "nombre_entidad",
        "$order": "Valor_Total DESC",
        "$limit": 100
    }

    results2 = client.get("jbjy-vk9h", **params2)

    return jsonify(results2)


# This QUERY show if is overlapping in the contracts
@app.route('/overlapping_contracts/<int:number>')
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
        
        if len(overlapping_ids) > max_overlap:
            max_overlap = len(overlapping_ids)
            max_overlap_ids = overlapping_ids

    response = {
        "message": f"El número maximo de contratos que ha tenido esta persona al tiempo son: {max_overlap}",
        "contract_ids": max_overlap_ids
    }
    
    return jsonify(response)



if __name__ == '__main__':
    app.run(debug=True)