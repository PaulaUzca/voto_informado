from flask import Flask, jsonify, request
from pathlib import Path
import pandas as pd
import json
from change_dataset import remove_nan
from news_scrapping import search_person_news
from gpt_summary import get_chatgpt_response
import jorge 
from sodapy import Socrata

app = Flask(__name__)

THIS_FOLDER = Path(__file__).parent.resolve()
csv_file = THIS_FOLDER / 'static/data_nice2.csv'
df = pd.read_csv(csv_file, encoding = "iso-8859-1")

#Sin los cargos de juntas administradoras locales porque no nos vamos a poner a buscar por comuna
#df = df[df['Descripción de la Corporación/Cargo'] != 'JUNTAS ADMINISTRADORAS LOCALES']

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

@app.route('/consultar/all')
def consultar_personas():
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


@app.route('/consultar/persona')
def get_persona():
    nombre = request.args.get('nombre')
    persona = df[df['nombresApellidos'] == nombre]
    number = persona['Número de Cédula de Ciudadanía'].values[0]
    # Group by 'nombre_etidad' and sum the other two columns
    
    contratos = {
        "entities": jorge.display_entities(number),
        "hallazgos": jorge.get_overlapping_contracts(number),
        "inhabilita": jorge.display_contracts_with_number(number)
    }
    

    dto = {
        "nombres": persona['nombresApellidos'].values[0],
        "cargo": persona['Descripción de la Corporación/Cargo'].values[0],
        "departamento": persona['Descripción del Departamento'].values[0],
        "municipio": persona['Descripción del Municipio'].values[0],
        "tipo_agrupacion": persona['Descripción del Tipo de Agrupación Política'].values[0],
        "partido": persona['Nombre de la Agrupación Política'].values[0],
        "candidaturas": {
            "info": jorge.cargosAspirado(nombre),
        },
        "contratos":contratos
    } 
    response = jsonify(dto)
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response
    

@app.route('/filter')
def filter():
    departamento = request.args.get('departamento') 
    filterData = jorge.filter_contracts(departamento)
    response = jsonify(filterData)
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


@app.route('/noticias')
def noticias():
    nombre = request.args.get('nombre')
    news = search_person_news(nombre)
    response = jsonify([{
        "contenido": news
        }])
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response

@app.route('/resumen')
def get_summary():
    nombre = request.args.get('nombre')
    news = search_person_news(nombre)
    news_txt = json.dumps(news, indent=4, ensure_ascii=False)
    print(len(news_txt))
    summary = get_chatgpt_response(news_txt)
    response = jsonify([{
        "news": news,
        "summary": summary
        }])
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


if __name__ == '__main__':
    app.run(debug=True)

    


