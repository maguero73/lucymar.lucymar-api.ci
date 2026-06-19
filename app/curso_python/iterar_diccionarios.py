diccionario={
    "nombre": "mariano",
    "apellido": "aguero",
    "edad": 41


}

#print(diccionario)





# Recorriendo diccionarios con items() para obtener la clave y el valor

for datos in diccionario.items():
    key= datos[0]
    value=datos[1]
    print(f"la clave es: {key} y el valor es {value}")


    #otra forma

for key, value in diccionario.items():
    print(f"La clave es: {key} y el valor es {value}")



