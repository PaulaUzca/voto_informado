# 🗳️​​ Backend Radiografía electoral Colombia 🔍
Construimos una API para consultar información de los candidatos en Colombia

## Teconologías:
🌶️​ Flask
💬​ Api de ChatGPT
🕸️​ Web scrapping
🐍 Python

## Equipo
[@brayanb1701](https://github.com/brayanb1701)
[@Jhosgun](https://github.com/Jhosgun)
[@Camilo0529](https://github.com/Camilo0529)
[@PaulaUzca](https://github.com/PaulaUzca)

## API
Alojamos nuestra API en un servidor de ```pythonanywhere```
https://pauzca.pythonanywhere.com/

Desarrollamos varios métodos para consultar información sobre los candidatos:

Obtener todos los departamentos, municipios y cargos:
* https://pauzca.pythonanywhere.com/departamento=
* https://pauzca.pythonanywhere.com/municipios?departamento=&cargo=
* https://pauzca.pythonanywhere.com/cargos?departamento=

Obtener a todos los candidatos
* https://pauzca.pythonanywhere.com/consultar/all?departamento=&municipio=&cargo=

Obtener el perfil de un candidato
* https://pauzca.pythonanywhere.com/consultar/persona?nombre=

Obtener noticias que hablen de un candidato
* https://pauzca.pythonanywhere.com/noticias?nombre=

Obtener noticias y un resumen generado por chatgpt de lo que estas dicen de un candidato
* https://pauzca.pythonanywhere.com/resumen?nombre=


