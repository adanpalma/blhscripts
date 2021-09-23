import csv
from timeit import default_timer as timer

import pyodbc

query = (
    "select riesgopa_noprestamo,riesgopa_fechasubida,riesgopa_producto,riesgopa_fechadesem, riesgopa_estatusmora,"
    "riesgopa_empresadeud1,riesgopa_empnomdeud1 from dbo.PAN_SQT_RIESGOPA where year(riesgopa_fechadesem) >= 2011 order by 1"
)
prestamos = {}
filename = "mesesprimer31plusmora.csv"
mora = "31-60 DAYS"

conn = pyodbc.connect(
    "Driver={SQL Server Native Client 11.0}; "
    "Server=10.10.20.37;"
    "Database=RISKPAN;"
    "Trusted_Connection=yes;"
)


def createcursor(conn):
    print("Estableciendo Coneccion.....")
    cursor = conn.cursor()
    return cursor


start = (
    timer()
)  # solo para tener idea del tiempo que consume usando pyodbc.. Otra opcion es usando pandas
cursor = createcursor(conn)


def executeqry(cursor, query):
    return cursor.execute(query)


rows = executeqry(cursor, query)

# delinquency = {'Producto': '', 'Empleador ':0, Delinquency': []}
def inserta_llave_dict(no_prestamo, diccionario, row):
    delinquency = {
        "Producto": "",
        "EmpleadorDesembolso": "",
        "EmpleadorActual": "",
        "NombreEmpDesembolso": "",
        "NombreEmpActual": "",
        "Delinquency": [],
    }
    diccionario[no_prestamo] = delinquency
    diccionario[no_prestamo]["Producto"] = row.riesgopa_producto
    diccionario[no_prestamo]["EmpleadorDesembolso"] = (row.riesgopa_empresadeud1,)
    diccionario[no_prestamo]["NombreEmpDesembolso"] = (row.riesgopa_empnomdeud1,)
    diccionario[no_prestamo]["Delinquency"].append(row.riesgopa_estatusmora)


def actualiza_empleador_actual(rowanterior, diccionario):
    diccionario[rowanterior.riesgopa_noprestamo][
        "EmpleadorActual"
    ] = rowanterior.riesgopa_empresadeud1
    diccionario[rowanterior.riesgopa_noprestamo][
        "NombreEmpActual"
    ] = rowanterior.riesgopa_empnomdeud1


# Al tener varios registros del mismo prestamo, se lee el primer registro de
# de toda la tabla para controlar cuando se esta leyendo el mismo prestamo
# y cuando se cambia de prestamo, esto permite agregar el nuevo prestmo
# al dictionary
row = next(rows)
inserta_llave_dict(row.riesgopa_noprestamo, prestamos, row)
rowanterior = row
ultimoregistro: pyodbc.Row

for row in rows:

    if rowanterior.riesgopa_noprestamo == row.riesgopa_noprestamo:
        prestamos[row.riesgopa_noprestamo]["Delinquency"].append(
            row.riesgopa_estatusmora
        )
        ultimoregistro = row

    else:
        # En este punto se leyo un credito diferente usando el objeto rowanterior
        # procedo a actualizar con que empleador se mantiene el prestamo anterior.  Empleador actual
        actualiza_empleador_actual(ultimoregistro, prestamos)
        inserta_llave_dict(row.riesgopa_noprestamo, prestamos, row)
        rowanterior = row

# Se revisa el dictionary para buscar los prestamos
# que han tenido moras 61+ dias  y en la posicion o index+
# donde encuentre el primer 61+ indica cuantos meses posteriores al desembolso empezo
# a pagar mal
try:
    with open(filename, "w", newline="") as f:
        fcsv = csv.writer(f)
        titulo = [
            "Prestamo",
            "Producto",
            "MesesPrimer31+",
            "Empleador Desembolso",
            "Nombre Empleador Desembolso",
            "Empleador Actual",
            "Nombre Empleador Actual",
        ]
        fcsv.writerow(titulo)
        for loan in prestamos.keys():
            meses = 0
            try:
                meses = prestamos[loan]["Delinquency"].index(mora) + 1
            except ValueError:
                meses = 0
            fila = [
                str(loan),
                prestamos[loan]["Producto"],
                str(meses),
                prestamos[loan]["EmpleadorDesembolso"],
                prestamos[loan]["NombreEmpDesembolso"],
                prestamos[loan]["EmpleadorActual"],
                prestamos[loan]["NombreEmpActual"],
            ]
            fcsv.writerow(fila)
except PermissionError:
    print(
        f"Favor revisar si el archivo {filename} esta siendo usado por otra aplicacion"
    )

print(f"Usando pyodbc el tiempo de proceso fue de ....{timer() - start}")
