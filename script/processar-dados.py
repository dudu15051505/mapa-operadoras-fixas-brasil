import os
import pandas as pd
import json
import io
import shutil
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import ProcessPoolExecutor

anos = ["2021", "2022" , "2023"]
meses = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"]

def process_data(ano, mes):
    selecionar_data = ano + "-" + mes
    
    print(f'Inicio processamento {selecionar_data}')
    
    # Limpa a pasta de saída js
    output_folder = f"{selecionar_data}"

    def delete_folder(path):
        try:
            shutil.rmtree(path)
            print(f"A pasta {path} foi deletada com sucesso.")
        except Exception as e:
            print(f"Erro ao deletar a pasta {path}: {e}")
                
    if os.path.exists(output_folder):
        delete_folder(output_folder)

    os.makedirs(output_folder)

    # Lê o arquivo CSV de dados de trabalho
    dados_df = pd.read_csv(f'Acessos_Banda_Larga_Fixa_{ano}_Colunas.csv', sep=';', low_memory=False)

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
        'SKY/AT&T': 'dados-sky'
        # Adicione mais empresas aqui, se necessário
    }

    # Agrupa os dados por CNPJ, Município, UF, Empresa, Tipo de Pessoa, Tecnologia, Tipo de Produto e Meio de Acesso
    # e soma os valores dos meses
    grouped_df = dados_df.groupby(['CNPJ', 'Município', 'UF', 'Empresa', 'Tipo de Pessoa', 'Tecnologia', 'Tipo de Produto', 'Meio de Acesso']).sum().reset_index()

    # Criar um dicionário para armazenar os dados fixos
    output_data = {}

    # Cria uma lista para armazenar as cidades com problemas de geolocalização
    cidades_com_problema_geo = []

    # Itera sobre os grupos e atualiza os dados no dicionário
    for index, row in grouped_df.iterrows():
        cnpj = row['CNPJ']
        uf = row['UF']
        cidade = row['Município']
        empresa = row['Empresa']
        tipo_pessoa = row['Tipo de Pessoa']
        quantidade_acesso = int(row[selecionar_data])  # Você pode escolher qual mês utilizar para a quantidade de acesso
            
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
                
            # Verifica se a cidade e UF já foram inseridas na lista de cidades com problema de geo
            if (cidade, uf) not in cidades_com_problema_geo:
                cidades_com_problema_geo.append((cidade, uf))
                problema_geo_txt = os.path.join(output_folder, 'cidades-com-problema-geo.txt')
                with open(problema_geo_txt, 'a', encoding='utf-8') as txt_file:
                    txt_file.write(f"{cidade}, {uf}\n")

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
                'identifier' : identifier,
                'cidade': cidade,
                'uf': uf,
                'latitude': latitude,
                'longitude': longitude,
                'empresa': empresa,
                'cnpj': cnpj,
                'data-dados': selecionar_data,
                'pf-ou-pj': tipo_pessoa,
                'info-tecnologia': [info_tecnologia]  # Cria um array com o primeiro item
            }
        else:
            # Se o identificador já existe, adiciona os dados de "info-tecnologia" ao array existente
            output_data[identifier]['info-tecnologia'].append(info_tecnologia)

    # Converte o dicionário em uma lista para gerar a saída JSON
    output_list = list(output_data.values())

    # Criar dicionários separados para armazenar dados por empresa e tipo de pessoa
    output_data_by_company = {}
       
    # Cria os arquivos JSON
    for data in output_list:
        empresa = data['empresa']
        if empresa in special_companies:
            company_folder = special_companies[empresa]
        else:
            company_folder = 'dados-pequenas'
           
        if data['pf-ou-pj'] == 'Pessoa Física':
            json_filename = f'locations-{data["uf"]}-PF.json'
        elif data['pf-ou-pj'] == 'Pessoa Jurídica':
            json_filename = f'locations-{data["uf"]}-PJ.json'
        else:
            json_filename = f'locations-{data["uf"]}-outras.json'
            
        json_path = os.path.join(output_folder, company_folder, json_filename)
            
        if empresa not in output_data_by_company:
            output_data_by_company[empresa] = {}
           
        if json_path not in output_data_by_company[empresa]:
            output_data_by_company[empresa][json_path] = []
            
        output_data_by_company[empresa][json_path].append(data)

    # Loop para gravar os arquivos JSON
    for empresa, file_data in output_data_by_company.items():
        for json_path, data_list in file_data.items():
            os.makedirs(os.path.dirname(json_path), exist_ok=True)
            with open(json_path, 'w', encoding='utf-8') as json_file:
                json.dump(data_list, json_file, ensure_ascii=False, indent=4)

    print(f'Arquivos JSON criados/atualizados com sucesso! ano {selecionar_data}')

# Usando ThreadPoolExecutor para executar em paralelo
#with ThreadPoolExecutor(max_workers=16) as executor:  # Defina o número máximo de threads
#    for ano in anos:
#        for mes in meses:
#            executor.submit(process_data, ano, mes)
#   print("Todas as tarefas foram concluídas.")

# Usando ProcessPoolExecutor para executar em paralelo
if __name__ == '__main__':
    with ProcessPoolExecutor(max_workers=16) as executor:  # Defina o número máximo de processos
        for ano in anos:
            for mes in meses:
                executor.submit(process_data, ano, mes)
    
    print("Todas as tarefas foram concluídas.")