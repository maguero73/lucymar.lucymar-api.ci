#import calculadora

#from calculadora import sumar, restar
import sys

sys.path.append("/home/20310607992@samba.afip.gob.ar/Backup/DATOS/gitlab/mi_proyecto_python/backend_fastapi/app/curso_python/modulos")

print(sys.path)


import calculadora as calc

#print(sys.path)

#sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))





#import app.curso_python.modulos.calculadora as calc

#con la segunda forma no es necesario llamarlo con calculadora

print(calc.sumar(2,2))
#print (calc.restar(5,3))
#print(calc.multiplicar(3, 3))