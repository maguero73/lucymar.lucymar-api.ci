#funciones lambda: se utiliza para crear funciones anónimas

#son funciones acotadas se utilizan para simplificar el codigo

#Sintaxis básica:

#lambda argumentos: expresión

#lambda devuelve una función que evalúa una expresión utilizando los argumentos dados

#Ejemplo:
'''

multiplicar_por_dos = lambda x : x*2

resultado= multiplicar_por_dos(5)

print (resultado)

'''
# uso de Filter

numeros=[1,2,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19]

multiplicar_por_dos = lambda x : x*2

#crear una funcion comun que me diga si los numeros de la lista son pares o no

def es_par(n):
    if (n%2==0):
        return True
    

numeros_pares=filter(es_par, numeros)

print (list(numeros_pares))



