from  pathlib import Path

filename = Path("data\\archmoro-pan-921.txt")

with open(filename) as filename:
    #Salto  lineas de titulos
    next(filename)



    for row in filename:
        #en archmoro hay prestamos que tiene que se pegan a la cartera y quitan
        #el espacio en blanco que hay entre prestamo y cartera y esto daña la lectura usando
        #read csv with space delimiter por eso valido si hay espacio en blanco en ese
        #rango de caracteres, si no lo hay los separo para poder grabar cada columna
        prestamo = row[0:11]
        cartera = row[11:15]
        periodo = row[15:20]
        delinquency    = row[20:24]
        saldoactual = row[24:35]
        sprogramado = row[35:46]
        ipagado = row[46:54]
        tasainteres = row[54:62]
        cobrador = row[62:70]
        print(prestamo,cartera,periodo,delinquency,saldoactual,sprogramado, ipagado,tasainteres,cobrador)
        print(row)

        registro = dict(zip(("Prestamo","cartera","periodo","delinquency","saldoactual","sprogramado","ipagado","tasaint","cobrador"), (prestamo,cartera,periodo,delinquency,saldoactual,sprogramado,ipagado,tasainteres,cobrador)))
        print(registro)
        #TODO: Guardar este dict en una lista de al menos 50K filas una vez lleno,guardar ese arreglo de dict en una tabla en SQL SERVER

        break







