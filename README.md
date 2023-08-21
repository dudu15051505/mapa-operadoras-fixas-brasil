# Mapa com dados de Tecnologia e tipo de Cliente fornecidos pela operada a base da ANATEL

https://mapa-operadoras-fixas-brasil.dudu-lab.xyz/

Este mapa tem o objetivo de ver mais facilmente os dados informados pelas operadoras a ANATE, utilizando apenas para HTML, CSS e JS para manter compatibilidade com host Github Pages.

Para este objetivo, fora utilizado os dados em CSV disponibilizados pela ANATEL no seguinte link: https://www.anatel.gov.br/dadosabertos/paineis_de_dados/acessos/acessos_banda_larga_fixa.zip

Todas as informações de nome de empresas, cnpj, locais, quantidades de acessos, tipos de acessos foram informados por cada operadora a ANATEL, a única informação que fora ajustada foi a "Quantidade de acessos", pois a ANATEL disponibiliza esta numeração separada por um grupo de velocidade, com isto o mapa realiza a soma de todos os acessos informados por grupo de velocidade para a cidade e o apresenta no mapa.
