#falto el profesor y los pibes quieren armar la clase

#lo que quiere el ejercicio es ordenar a todos los alumnos por edad y el profesor será el de mayor edad y el asistente el más joven

#pedir nombre y edad de los compañeros que vinieron hoy a clase

#crear una tupla llamada compañero con su nombre y edad

#funcion para obtener el asistente y el profesor segun la edad
def obtener_compañeros(cantidad_de_compañeros):


    #creando la lista con los compañeros
    compañeros =[]


    #ejecuto un for para pedir informacion de cada compañero
    for i in range(cantidad_de_compañeros):
        nombre = input("ingrese el nombre del compañero")
        edad = int(input("ingrese la edad del compañero"))
        compañero = (nombre, edad)

        #agrego la informacion a la lista
        compañeros.append(compañero)

    #ordeno de menor a mayor segun la edad    
    compañeros.sort(key=lambda x:x[1])

    #compañeros[0] devuelve una tupla con (nombre,edad) y despues accedemos al nombre, otro: [0]
    #todo esto para definir al asistente y al profesor:
    asistente=compañeros[0][0]
    profesor=compañeros[-1][0]

    #retornamos una tupla
    return asistente,profesor

#desempaquetamos lo que nos retorna la funcion
asistente, profesor=obtener_compañeros(3)


#mostramos el resultado
print(f"el profesor es {profesor} y su asistente es {asistente}")


#para ver las propiedades y metodos de el namespace

print(dir(asistente))

#para ver el nombre de este modulo
print(__name__)

