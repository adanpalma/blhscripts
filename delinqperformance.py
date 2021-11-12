import sqlalchemy
from pandas import DataFrame
from sqlalchemy.engine import URL
import pandas as pd
import plotly.express as px

from timeit import default_timer as timer

start = timer()

# pyodbc parameter for conections to database
driver = '{SQL Server}'
server = '10.10.20.37'
database = 'RISKPAN'
trust_connection = 'yes'

db_flavor = 'mssql+pyodbc'

# Conection String
conn_string = f'DRIVER={driver};'
conn_string += f'SERVER={server};'
conn_string += f'DATABASE={database};'
conn_string += f'TRUSTED_CONNECTION={trust_connection}'

# Sqlalchemy engine connection URL
conn_url = URL.create(db_flavor, query={"odbc_connect": conn_string})

##Create engine connection
engine = sqlalchemy.create_engine(conn_url)

# Read periodos_transcurridos_x_coshechas from sql to pandas.data frame
df_periodosbyvintages = pd.read_sql_table('periodos_transcurridos_x_cosecha', engine)

# Agrego campo para crear el campo acumulado
df_periodosbyvintages["Hipotecas_deemed_acumulado"] = 0
df_periodosbyvintages["Hipotecas_default_acumulado"] = 0
df_periodosbyvintages["personal_deemed_acumulado"] = 0
df_periodosbyvintages["personal_default_acumulado"] = 0

# Se lee el deemdefault de cada cosecha, se une al dataframe periodos y se genera un cumsum()
df_deemed_total: DataFrame = pd.DataFrame()
primera_vez = 1
vintage1 = df_periodosbyvintages['vintage'].min()
vintageN = df_periodosbyvintages['vintage'].max() + 1



for vvintage in range(vintage1,vintageN):
    qry_deemed = """ select * from DEEMED_DEFAULT_POR_COSECHAS_HIPO where vintage = {} order by 2""".format(vvintage)
    df_deemed_defaults_vintage = pd.read_sql(qry_deemed, engine)
    if primera_vez:
        df_deemed_total = df_deemed_defaults_vintage
        primera_vez = 0
    else:
        df_deemed_total = df_deemed_total.append(df_deemed_defaults_vintage)

df_periodosbyvintages = pd.merge(df_periodosbyvintages, df_deemed_total, how='left', on=['vintage', 'period'])
df_periodosbyvintages.fillna(0, inplace=True)
df_periodosbyvintages['Hipotecas_deemed_acumulado'] = df_periodosbyvintages.groupby('vintage')['percentage_deemed_defaulted'].cumsum()


# TODO: cambiar el codigo para que grabe en csv los deemed procesados y en otro script graficar ese csv
df_plotear = df_periodosbyvintages[['vintage','period','Hipotecas_deemed_acumulado']]

plt = px.line(df_plotear,x='period',y='Hipotecas_deemed_acumulado',color='vintage')
plt.show()

print(f"tiempo transcurrido = {timer()-start}")


