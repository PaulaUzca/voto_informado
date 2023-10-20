from change_dataset import remove_nan
import pandas as pd

# Replace 'your_file.csv' with the path to your CSV file
csv_file = '../resources/data_nice.csv'

# Read the CSV file into a Pandas DataFrame
df = pd.read_csv(csv_file, encoding = "iso-8859-1")

#Sin los cargos de juntas administradoras locales porque no nos vamos a poner a buscar por comuna
df = df[df['Descripción de la Corporación/Cargo'] != 'JUNTAS ADMINISTRADORAS LOCALES']
df.fillna('', inplace=True)
df['nombresApellidos'] = df['Primer Nombre'] + ' '  +df['Segundo Nombre'] + ' ' + df['Primer Apellido'] + ' ' + df['Segundo Apellido']
departamentos = remove_nan(df['Descripción del Departamento'].unique())
municipios = remove_nan(df['Descripción del Municipio'].unique())
cargos = remove_nan(df['Descripción de la Corporación/Cargo'].unique())
print(departamentos)
print(cargos)
print(municipios)