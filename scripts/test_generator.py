import os
import sys
from datetime import datetime
from typing import List, Dict
import model_generator as model_gen

#--------------------------------------------------------------------------------------
TEST_PATH="test"

#--------------------------------------------------------------------------------------
def add_imports(lines:list[str]) -> None:
    lines.append('"""\n    Creado con generador de tests py-api-factory\n')
    lines.append(f'    Fecha: {datetime.now()}\n"""\n')    
    lines.append("import pytest\n")
    lines.append("from datetime import datetime\n")
    lines.append("from fastapi.testclient import TestClient\n")
    lines.append("from app.main import app\n")
    lines.append("from pyapiafip.utils.config import app_conf, app_version\n")
    lines.append("from test import sign_token, get_jwt\n")
    lines.append("from pyapiafip.utils import config\n\n")
    lines.append('SECURITY_PATH=f"{config.app_conf["security_base_path"]}/v1.0"\n')
    lines.append('MONITORING_PATH=f"{config.app_conf["monitoring_base_path"]}/v1.0"\n')
    lines.append('API_PATH=f"{config.app_conf["api_base_path"]}/v1.0"\n')
    lines.append("\n")
    lines.append("client = TestClient(app)\n")
    lines.append("\n")
    lines.append("TOKEN, SIGN = sign_token.get_sua_token_sign()\n")
    # lines.append("JWT = get_jwt.main()\n")
    lines.append("\n")

#--------------------------------------------------------------------------------------
def add_pytest_fixture(lines:list[str]):
    pytest_fixture = '''
@pytest.fixture(scope='module')
def global_data():
    response = client.post(
        f"{SECURITY_PATH}/authorization",
        json={"token": TOKEN, "sign": SIGN},
        headers={'origin': 'http://localhost'}
    )
    response_dict = response.json()
    return response_dict['auth_token']
'''
    lines.append(pytest_fixture)

#--------------------------------------------------------------------------------------
def add_tests(lines:list[str], table_name:str, primary_keys, create_fields, all_cols, no_pk_cols, es_vista:bool):
    table = table_name.lower()
    pk_path = '/'.join([f"{{{item}}}" for item in primary_keys['constrained_columns']])
    no_pk_json = ',\n'.join([f'        "{item}": f"{{{item}}}" if {item} else None' for item in no_pk_cols])
    create_str = '\n'.join([f"{item} {'' if '=' in item else '='}" for item in create_fields])
    resultados=[]
    for campo in create_fields:
        nombre, tipo = campo.split(":")
        valor:str=""
        if "int" in tipo:
            valor = f'{nombre} if {nombre} else None'
        else:
            valor = f'f"{{{nombre}}}" if {nombre} else None'
        resultados.append(f'    "{nombre}": {valor}')
    # Junta los elementos de la lista en una cadena JSON
    fields_json = ",\n".join(resultados)

    contenido_pruebas = f'''
#--------------------------------------------------------------------------------------
# TODO: ASIGNAR VALORES A LAS SIG. VARIABLES PARA EL CASO DE PRUEBA DESEADO
#--------------------------------------------------------------------------------------
{create_str}

#--------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------
fields_json = {{
{fields_json}
}}
'''
    if not es_vista:
        contenido_pruebas = f'''{contenido_pruebas}

#--------------------------------------------------------------------------------------
def test_add_{table}(global_data):
    response = client.post(f"{{API_PATH}}/{table}",
        json= fields_json, 
        headers={{
            'origin': 'http://localhost',
            "Authorization": f"Bearer {{global_data}}",
            "Audit": '{{"id_token": "1234567", "id_usuario": 20111111112, "id_representado": 20222222223}}'
        }},
    )
    assert response.status_code == 201
    response_dict = response.json()

    # TODO test_generator: Se debe completar los datos esperados
    expected_data = fields_json
    assert response_dict == expected_data
'''
    
    contenido_pruebas = f'''{contenido_pruebas}

#--------------------------------------------------------------------------------------
def test_get_{table}(global_data):
    response = client.get(f"{{API_PATH}}/{table}/{pk_path}",
        headers={{
            'origin': 'http://localhost',
            "Authorization": f"Bearer {{global_data}}",
            "Audit": '{{"id_token": "1234567", "id_usuario": 20111111112, "id_representado": 20222222223}}'
        }}
    )
    assert response.status_code == 200
    response_dict = response.json()

    # TODO test_generator: Se debe completar los datos esperados
    expected_data = fields_json
    assert response_dict == expected_data

#--------------------------------------------------------------------------------------
def test_getall_{table}(global_data):
    response = client.get(f"{{API_PATH}}/{table}",
        headers={{
            'origin': 'http://localhost',
            "Authorization": f"Bearer {{global_data}}",
            "Audit": '{{"id_token": "1234567", "id_usuario": 20111111112, "id_representado": 20222222223}}'
        }}
    )
    assert response.status_code == 200
    response_dict = response.json()

    # TODO test_generator: Se debe completar los datos esperados
    expected_data = fields_json
    assert expected_data in response_dict
'''

    if not es_vista:
        contenido_pruebas = f'''{contenido_pruebas}

#--------------------------------------------------------------------------------------
def test_update_{table}(global_data):
    req_json = {{
{no_pk_json}
    }}
    response = client.patch(f"{{API_PATH}}/{table}/{pk_path}",
        json= req_json, 
        headers={{
            'origin': 'http://localhost',
            "Authorization": f"Bearer {{global_data}}",
            "Audit": '{{"id_token": "1234567", "id_usuario": 20111111112, "id_representado": 20222222223}}'
        }}
    )
    assert response.status_code == 200
    response_dict = response.json()
    expected_data = {{"rows_affected": 1}}
    assert expected_data == response_dict

    response = client.get(f"{{API_PATH}}/{table}/{pk_path}",
        headers={{
            'origin': 'http://localhost',
            "Authorization": f"Bearer {{global_data}}" }}
    )
    assert response.status_code == 200
    response_dict = response.json()

    # TODO test_generator: Se debe completar los datos esperados
    expected_data = fields_json
    assert response_dict == expected_data

#--------------------------------------------------------------------------------------
def test_delete_{table}(global_data):
   response = client.delete(f"{{API_PATH}}/{table}/{pk_path}",
        headers={{
            'origin': 'http://localhost',
            "Authorization": f"Bearer {{{{global_data}}}}",
            "Audit": '{{"id_token": "1234567", "id_usuario": 20111111112, "id_representado": 20222222223}}'
        }}
   )
   assert response.status_code == 204

   response = client.get(f"{{API_PATH}}/{table}/{pk_path}",
        headers={{
            'origin': 'http://localhost',
            "Authorization": f"Bearer {{{{global_data}}}}" }}
   )
   assert response.status_code == 404


#--------------------------------------------------------------------------------------
'''
    lines.append(contenido_pruebas)


#--------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------
if __name__ == "__main__":
    if len(sys.argv) != 7:
        print("Usage: python test_generator.py <ip> <port> <sid> <user> <password> <table_name>")
        print("<ip>: ip de la BD")
        print("<port>: puerto de la BD")
        print("<sid>: sid de la BD")
        print("<user>: usuario de conexión a la BD")
        print("<password>: clave del usuario de conexión a la BD")
        print("<table_name>: nombre de la tabla que se generará el modelo")
        sys.exit(1)
    
    ip = sys.argv[1]
    port = sys.argv[2]
    sid = sys.argv[3]
    user = sys.argv[4]
    password = sys.argv[5]
    table_name = sys.argv[6]

    print(f"\nProcesando {user}.{table_name}@{sid}...\n")

    test_lines:list[str]=[]
    columns, primary_keys, foreign_keys, indexes, constraints, es_vista = model_gen.get_table_metadata(ip, port, sid, user, password, table_name)
    create_types=[]
    create_fields=[]
    all_cols = []
    no_pk_cols = []

    for column in columns:
        field_db, field_model, field_create, field_update, field_relations, primary_key_type = model_gen.get_field(
            column=column, 
            primary_keys=primary_keys,
            foreign_keys=foreign_keys
        )
        if column['name'] not in primary_keys['constrained_columns']:
            no_pk_cols.append(f"{column['name']}")
        create_types.append(field_create)
        all_cols.append(f"{column['name']}")

        create_fields.append(f"{field_create}")

    add_imports(lines=test_lines)
    model_gen.add_func_separator(lines=test_lines)
    add_pytest_fixture(lines=test_lines)    
    # add_tests(lines=test_lines, table_name=table_name, primary_keys=primary_keys, primary_keys_type=primary_keys_type, create_fields=create_types, update_fields=update_fields)
    add_tests(lines=test_lines, table_name=table_name, primary_keys=primary_keys, create_fields=create_fields, all_cols=all_cols, no_pk_cols=no_pk_cols, es_vista=es_vista)

    test_file=f"{TEST_PATH}/test_{table_name.lower()}.py"
    model_gen.generate_file(file_name=test_file, model="".join(test_lines))


    print("\nFIN de la generación.")

