#crear lo mismo que lo anterior pero con Lambda

#Uso de filter:

#Filtra elementos que cumplan una condición.

numeros=[1,2,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19]

multiplicar_por_dos = lambda x : x*2


numeros_pares=filter(lambda numero:numero%2 ==0, numeros)

print (list(numeros_pares))


