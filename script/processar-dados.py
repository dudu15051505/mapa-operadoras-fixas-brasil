import os
import pandas as pd
import json
import io

# Lê o arquivo CSV de dados de trabalho
dados_df = pd.read_csv('dados-para-trabalho.csv', sep=';', low_memory=False)

# Lê o arquivo CSV de latitude e longitude
lat_lon_df = pd.read_csv('latitude-longitude-cidades-powershell.csv')

# Renomeia as colunas com espaços
dados_df = dados_df.rename(columns={'Pessoa Jurídica': 'Pessoa_Jurídica', 'Pessoa Física': 'Pessoa_Física'})

# Agrupa os dados por Município, UF, Tecnologia, Empresa e Tipo de Pessoa, e soma os valores dos meses
grouped_df = dados_df.groupby(['Município', 'UF', 'Tecnologia', 'Empresa', 'Tipo de Pessoa', 'Tipo de Produto', 'Meio de Acesso']).sum().reset_index()

# Itera sobre os grupos e atualiza os arquivos JSON existentes ou cria novos
output_folder = 'js'
os.makedirs(output_folder, exist_ok=True)

for index, row in grouped_df.iterrows():
    uf = row['UF']
    cidade = row['Município']
    tecnologia = row['Tecnologia']
    empresa = row['Empresa']
    tipo_pessoa = row['Tipo de Pessoa']
    tipo_de_produto = row['Tipo de Produto']
    meio_de_acesso = row['Meio de Acesso']
    
    # Encontra a latitude e longitude correspondentes
    lat_lon_rows = lat_lon_df[(lat_lon_df['uf'] == uf) & (lat_lon_df['municipio'] == cidade)]

    if not lat_lon_rows.empty:
        lat_lon_row = lat_lon_rows.iloc[0]
        latitude = lat_lon_row['latitude']
        longitude = lat_lon_row['longitude']
    else:
        # Lida com o caso em que não há correspondência para a UF e cidade
        latitude = None
        longitude = None
    
    # Monta o objeto JSON
    json_data = {
        'cidade': cidade,
        'uf': uf,
        'latitude': latitude,
        'longitude': longitude,
        'empresa': empresa,
        'pf-ou-pj': tipo_pessoa,
        'tecnologia': tecnologia,
        'tipo-de-Produto': tipo_de_produto,
        'meio-de-acesso': meio_de_acesso
    }
    
    # Gera o nome do arquivo JSON baseado no tipo de pessoa (PF ou PJ)
    if tipo_pessoa == 'Pessoa Física':
        json_filename = f'locations-{uf}-PF.json'
    elif tipo_pessoa == 'Pessoa Jurídica':
        json_filename = f'locations-{uf}-PJ.json'
    else:
        # Trate outros tipos de pessoa aqui, se necessário
        continue
    
    json_path = os.path.join(output_folder, json_filename)
    
    # Se o arquivo JSON já existe, carrega os dados existentes e atualiza
    if os.path.exists(json_path):
        with open(json_path, 'r', encoding='utf-8') as json_file:
            existing_data = json.load(json_file)
        existing_data.append(json_data)
    else:
        existing_data = [json_data]
    
    # Escreve o JSON no arquivo
    with io.open(json_path, 'w', encoding='utf-8') as json_file:
        json.dump(existing_data, json_file, ensure_ascii=False, indent=4)

print('Arquivos JSON criados/atualizados com sucesso!')
