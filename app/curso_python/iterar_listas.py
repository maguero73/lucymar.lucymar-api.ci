frutas= ["manzana", "pera", "naranja", "granada", "durazno"]




'''
# filtrar con continue evita que se coma una manzana
for fruta in frutas:
    if fruta == "pera":
        continue
    print(f"me voy a comer una {fruta}")
'''


for fruta in frutas:
    if fruta == "pera":
        print(f"me voy a comer una {fruta}")
        break
        
print("bucle terminado")