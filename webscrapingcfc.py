import ssl

import requests as rq
import wget as wget
from bs4 import BeautifulSoup as bs
from bs4 import SoupStrainer as ss

# ssl.create_default_https_context allow download files
# from a https protocol
ssl._create_default_https_context = ssl._create_unverified_context

url = "https://www.superfinanciera.gov.co/inicio/informes-y-cifras/cifras" \
      "/establecimientos-de-credito/informacion-periodica/mensual/evolucion" \
      "-cartera-de-creditos-60950 "
main_url = "https://www.superfinanciera.gov.co"

file_types = {"xls": ".xls", "xlsx": ".xlsx", "csv": ".csv"}
output_directory = "cfc_moras_mensuales/"

# Aqui hacemos un request a la direccion url para obtener el content de la
# pagina

htmlpage = rq.get(url)

if htmlpage.status_code != 200:
    print(f"Error Request status code {htmlpage}")
    exit()

# Aqui pasamos el contenido de la pagina a beatifulsoup
# y extraemos todos los tag "a" que son donde estan los arhivos a descargar
bspage = bs(htmlpage.content, "html.parser", parse_only=ss("a"))

for link in bspage:

    if link.has_attr("href"):
        if file_types["xls"] in link["href"]:
            full_path = main_url + link["href"]
            print(f"%%% Downloading {full_path}.....")
            wget.download(full_path, output_directory)
            # download(full_path, output_directory)
