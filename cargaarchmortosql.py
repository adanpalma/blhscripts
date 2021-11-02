from  pathlib import Path
import pyodbc

filename = Path("data\\archmoro-pan-921.txt")

rowstosql = []
registros_procesados = 0
max_registros_a_grabar = 500000

#Conexion a la base de datos
# dsn= odbcR_to_Sql_RiskPan  es un dsn que debes crear en Windows
myDb = pyodbc.connect("dsn=odbcR_to_Sql_RiskPan")
mySqlStr = f'INSERT INTO archmoroPan(Prestamo,cartera,periodo,delinquency,saldoactual,saldoprogramado,interespagado,tasainteres,cobrador) VALUES(?,?,?,?,?,?,?,?,?)'


def graba_registros(myDb,sqlstr, rowstoSql):

    try:

        myCursor = myDb.cursor()
        myCursor.executemany(mySqlStr, rowstosql)
        myDb.commit()

    except Exception as e:
        print(e)
        exit(1)

    finally:
        myCursor.close()


with open(filename) as filename:
    #Salto  lineas de titulos
    next(filename)

    for row in filename:
        #en archmoro hay prestamos que tiene que se pegan a la cartera y quitan
        #el espacio en blanco que hay entre prestamo y cartera y esto daña la lectura usando
        #read csv with space delimiter por eso valido si hay espacio en blanco en ese
        #rango de caracteres, si no lo hay los separo para poder grabar cada columna

        prestamo = row[0:11]
        cartera = row[11:17]
        periodo = int(row[17:23])
        delinquency    = int(row[23:27])
        # uso replace porque a veces los saldos vinen coneste formato 999.98- y ese signo al final no permite la
        #conversion a float
        saldoactual = float(row[27:38]) if "-" not in row[27:38] else  float(row[27:38].replace('-','')) * -1
        saldoprogramado = float(row[38:49]) if "-" not in row[38:49] else  float(row[38:49].replace('-','')) * -1
        interespagado = float(row[49:57])   if "-" not in row[49:57] else  float(row[49:57].replace('-','')) * -1
        tasainteres = float(row[57:65])
        cobrador = int(row[65:70])


       # registro = dict(zip(("Prestamo","cartera","periodo","delinquency","saldoactual","saldoprogramado","interespagado","tasainteres","cobrador"), (prestamo,cartera,periodo,delinquency,saldoactual,saldoprogramado,interespagado,tasainteres,cobrador)))
        registro =  (prestamo,cartera,periodo,delinquency,saldoactual,saldoprogramado,interespagado,tasainteres,cobrador)
        rowstosql.append(registro)
        registros_procesados += 1

        if registros_procesados == max_registros_a_grabar:

            graba_registros(myDb, mySqlStr, rowstosql)
            rowstosql.clear()
            registros_procesados = 0


    #Si hay registros_procesdos se llama a graba_registros ya que termino el cliclo y quedaron registros sin grabar
    if registros_procesados > 0:
        graba_registros(myDb,mySqlStr, rowstosql )

    #Cierro la conexion a la BD
    myDb.close()








