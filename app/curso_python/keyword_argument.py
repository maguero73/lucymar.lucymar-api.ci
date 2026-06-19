#creando una funcion de 3 parametros
'''
def frase(nombre, apellido, descripcion):
    return f'Hola me llamo {nombre}, mi apellido es: {apellido}, y soy {descripcion}'

frase= frase('mariano', 'aguero', 'capo')
print(frase)

'''
#crear una funcion de 3 parametros con demostracion del concepto keyword argument


def frase(nombre, apellido, descripcion='capo', edad=41):
    return f'Hola me llamo {nombre}, mi apellido es: {apellido}, soy {descripcion} y tengo {edad} años'


# una cosa son los valores posicionales de los parámetros y otra cosa son los keyword argument se especifican nombre parametro= valor

frase= frase('aguero','mariano',descripcion='alto')
print(frase)