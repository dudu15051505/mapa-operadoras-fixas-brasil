import os
import pandas as pd
import json
import io

# Limpa a pasta de saída js
output_folder = 'js'
if os.path.exists(output_folder):
    for filename in os.listdir(output_folder):
        file_path = os.path.join(output_folder, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)
        else:
            os.rmdir(file_path)
else:
    os.makedirs(output_folder)

# Lê o arquivo CSV de dados de trabalho
dados_df = pd.read_csv('dados-para-trabalho.csv', sep=';', low_memory=False)

# Lê o arquivo CSV de latitude e longitude
lat_lon_df = pd.read_csv('latitude-longitude-cidades-powershell.csv')

# Renomeia as colunas com espaços
dados_df = dados_df.rename(columns={'Pessoa Jurídica': 'Pessoa_Jurídica', 'Pessoa Física': 'Pessoa_Física'})

# Define empresas especiais e suas respectivas pastas
special_companies = {
    'OI': 'dados-oi',
    'VIVO': 'dados-vivo',
    'CLARO': 'dados-claro',
    'TIM': 'dados-tim',
    'ALGAR (CTBC TELECOM)': 'dados-algar',
    'BRISANET': 'dados-brisanet',
    'EB FIBRA': 'dados-ebfibra',
    'DESKTOP': 'dados-desktop',
    'VERO': 'dados-vero',
    'STARLINK BRAZIL SERVICOS DE INTERNET LTDA.': 'dados-starlink',
    'HUGHES': 'dados-hughes',
    'TELEBRAS': 'dados-telebras'
    # Adicione mais empresas aqui, se necessário
}

# Agrupa os dados por CNPJ, Município, UF, Empresa, Tipo de Pessoa, Tecnologia, Tipo de Produto e Meio de Acesso
# e soma os valores dos meses
grouped_df = dados_df.groupby(['CNPJ', 'Município', 'UF', 'Empresa', 'Tipo de Pessoa', 'Tecnologia', 'Tipo de Produto', 'Meio de Acesso']).sum().reset_index()

# Criar um dicionário para armazenar os dados fixos
output_data = {}

# Itera sobre os grupos e atualiza os dados no dicionário
for index, row in grouped_df.iterrows():
    cnpj = row['CNPJ']
    uf = row['UF']
    cidade = row['Município']
    empresa = row['Empresa']
    tipo_pessoa = row['Tipo de Pessoa']
    quantidade_acesso = int(row['2023-06'])  # Você pode escolher qual mês utilizar para a quantidade de acesso
    
    if quantidade_acesso == 0:
        continue

    # Encontra a latitude e longitude correspondentes
    lat_lon_rows = lat_lon_df[(lat_lon_df['uf'] == uf) & (lat_lon_df['municipio'] == cidade)]

    if not lat_lon_rows.empty:
        lat_lon_row = lat_lon_rows.iloc[0]
        latitude = lat_lon_row['latitude']
        longitude = lat_lon_row['longitude']
    else:
        latitude = None
        longitude = None

    # Cria um dicionário para armazenar os dados de "info-tecnologia"
    info_tecnologia = {
        'tecnologia': row['Tecnologia'],
        'tipo-de-Produto': row['Tipo de Produto'],
        'meio-de-acesso': row['Meio de Acesso'],
        'quantidade-acesso': quantidade_acesso
    }

    # Cria um identificador único para cada combinação de cidade, UF, Empresa e Tipo de Pessoa
    identifier = f"{cnpj}-{cidade}-{uf}-{empresa}-{tipo_pessoa}"

    # Se o identificador ainda não existe no dicionário, cria o registro
    if identifier not in output_data:
        output_data[identifier] = {
            'cidade': cidade,
            'uf': uf,
            'latitude': latitude,
            'longitude': longitude,
            'empresa': empresa,
            'cnpj': cnpj,
            'pf-ou-pj': tipo_pessoa,
            'info-tecnologia': [info_tecnologia]  # Cria um array com o primeiro item
        }
    else:
        # Se o identificador já existe, adiciona os dados de "info-tecnologia" ao array existente
        output_data[identifier]['info-tecnologia'].append(info_tecnologia)

# Converte o dicionário em uma lista para gerar a saída JSON
output_list = list(output_data.values())

# Cria os arquivos JSON
for data in output_list:
    empresa = data['empresa']
    if empresa in special_companies:
        company_folder = special_companies[empresa]
    else:
        company_folder = 'dados-pequenas'
    
    json_path = os.path.join(output_folder, company_folder)
    os.makedirs(json_path, exist_ok=True)

    if data['pf-ou-pj'] == 'Pessoa Física':
        json_filename = f'locations-{data["uf"]}-PF.json'
    elif data['pf-ou-pj'] == 'Pessoa Jurídica':
        json_filename = f'locations-{data["uf"]}-PJ.json'
    else:
        json_filename = f'locations-{data["uf"]}-outras.json'
    
    json_path = os.path.join(json_path, json_filename)

    if os.path.exists(json_path):
        with open(json_path, 'r', encoding='utf-8') as json_file:
            existing_data = json.load(json_file)
        existing_data.append(data)
    else:
        existing_data = [data]

    with io.open(json_path, 'w', encoding='utf-8') as json_file:
        json.dump(existing_data, json_file, ensure_ascii=False, indent=4)

print('Arquivos JSON criados/atualizados com sucesso!')
