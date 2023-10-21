from flask import Flask, jsonify, request
from change_dataset import remove_nan
import pandas as pd
from pathlib import Path


app = Flask(__name__)

THIS_FOLDER = Path(__file__).parent.resolve()
csv_file = THIS_FOLDER / 'static/data_nice.csv'
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


if __name__ == '__main__':
    app.run(debug=True)