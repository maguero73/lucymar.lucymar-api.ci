import sys
import os
from datetime import datetime
import oracledb
from sqlalchemy import create_engine, inspect
from sqlalchemy.engine.interfaces import ReflectedColumn
import test_generator as test_gen

# print("Directorio actual:", os.getcwd())

#--------------------------------------------------------------------------------------
# MODEL_PATH="app/dbmodels"
# ROUTE_PATH="app/routers/v1_0"
# Obtener ruta absoluta de la carpeta donde está el script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Obtener carpeta raíz del proyecto
ROOT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))

MODEL_PATH = os.path.join(ROOT_DIR, "app", "dbmodels")
ROUTE_PATH = os.path.join(ROOT_DIR, "app", "routers", "v1_0")

#--------------------------------------------------------------------------------------
def get_table_metadata(ip, port, sid, user, password, table_name):
    dsn = oracledb.makedsn(ip, port, sid)
    oracledb.init_oracle_client(lib_dir="/opt/oracle/instantclient")  # Cambia la ruta según tu configuración
    engine = create_engine(f'oracle+oracledb://{user}:{password}@{dsn}')

    print("Inicializando inspección")
    insp = inspect(engine)
    print("Obteniendo columnas")
    columns = insp.get_columns(table_name)
    print(f"Columnas: {len(columns)}")
    primary_key_constraints = insp.get_pk_constraint(table_name)
    print("Obteniendo PK")
    foreign_keys = insp.get_foreign_keys(table_name)
    print("Obteniendo FK")
    indexes = insp.get_indexes(table_name)
    print("Obteniendo indices")
    constraints = insp.get_check_constraints(table_name)
    print("Obteniendo constraints")
    primary_keys = primary_key_constraints#['constrained_columns']
    print("Obteniendo constraints pk")
    

    # Obtén la lista de columnas que son claves primarias
    pk_columns = primary_key_constraints.get('constrained_columns', [])
    print("lista de columnas pk")
    # Crear un diccionario para un acceso rápido a las columnas por nombre
    columns_dict = {col['name']: col for col in columns}
    print("Obteniendo diccionario")
    # Ordenar las columnas: primero las de clave primaria, luego el resto
    ordered_columns = [columns_dict[name] for name in pk_columns if name in columns_dict]
    print("Ordenando las columnas")
    non_pk_columns = [col for col in columns if col['name'] not in pk_columns]
    print("non_pk")
    ordered_columns.extend(non_pk_columns)
    print("Ordenando las columnas")
    
    es_vista = False
    print("sigue")
    if table_name in insp.get_view_names():
        es_vista = True
        print("entra")
    return ordered_columns, primary_keys, foreign_keys, indexes, constraints, es_vista
    print("Fin de obtención metadata")
#--------------------------------------------------------------------------------------
def get_python_type(column_type):
    if 'INTEGER' in str(column_type).upper():
        return 'int'
    elif 'NUMBER' in str(column_type).upper():
        if column_type.scale and column_type.scale>0: # Si tiene decimales
            return 'float'
        return 'int'
    elif 'VARCHAR' in str(column_type).upper() or 'CHAR' in str(column_type).upper():
        return 'str'
    elif 'DATE' in str(column_type).upper():
        return 'datetime'
    elif 'TIMESTAMP' in str(column_type).upper():
        return 'datetime'
    elif 'BLOB' in str(column_type).upper() or 'RAW' in str(column_type).upper():
        return 'bytes'
    elif 'CLOB' in str(column_type).upper() or 'NCLOB' in str(column_type).upper():
        return 'str'
    else:
        return 'str'

#--------------------------------------------------------------------------------------
def get_db_type(column_type):
    if 'INTEGER' in str(column_type).upper():
        return 'Integer'
    elif 'NUMBER' in str(column_type).upper():
        if column_type.scale and column_type.scale>0:
            return f'Numeric({column_type.precision},{column_type.scale})'
        elif column_type.precision and column_type.precision<=9:
            return f'Integer'
        elif column_type.precision and column_type.precision<=18:
            return f'BigInteger'
        else:
            return 'Numeric'
    elif 'VARCHAR' in str(column_type).upper() or 'CHAR' in str(column_type).upper():
        return f'String({column_type.length})'
    elif 'DATE' in str(column_type).upper():
        return 'DateTime'
    elif 'TIMESTAMP' in str(column_type).upper():
        return 'TIMESTAMP'
    elif 'BLOB' in str(column_type).upper() or 'RAW' in str(column_type).upper():
        return 'LargeBinary'
    elif 'CLOB' in str(column_type).upper() or 'NCLOB' in str(column_type).upper():
        return 'Text'
    else:
        return 'String'
    
#--------------------------------------------------------------------------------------
def add_imports_db(lines:list[str])->None:
    lines.append('"""\n    Creado con generador de modelos py-api-factory\n')
    lines.append(f'    Fecha: {datetime.now()}\n"""\n')
    lines.append("from datetime import datetime, timezone\n")
    lines.append("from sqlalchemy import PrimaryKeyConstraint, ForeignKeyConstraint, Index, CheckConstraint, ForeignKey\n")
    lines.append("from sqlalchemy import Numeric, String, DateTime, Sequence, LargeBinary, Text, TIMESTAMP, Integer, BigInteger\n")
    lines.append("from sqlalchemy import func, select as sa_select, update as sa_update, delete as sa_delete\n")
    lines.append("from sqlalchemy.orm import Session, Mapped, mapped_column, relationship\n")
    lines.append("from app.dbmodels.db_base import DBBase\n")
    lines.append("from pyapiafip.utils import sync_to_async\n")
    lines.append("\n")

#--------------------------------------------------------------------------------------
def add_class_db(lines:list[str], table_name:str)->None:
    class_name = "".join(word.capitalize() for word in table_name.split("_"))
    class_name = f"DB{class_name}"
    class_str = f"class {class_name}(DBBase):\n"
    class_str += f"    __tablename__ = '{table_name}'\n\n"

    lines.append(class_str)
#--------------------------------------------------------------------------------------
def add_imports_api(lines:list[str], table_name:str)->None:
    class_name = "".join(word.capitalize() for word in table_name.split("_"))
    class_name = f"DB{class_name}"
    lines.append('"""\n    Creado con generador de modelos py-api-factory\n')
    lines.append(f'    Fecha: {datetime.now()}\n"""\n')
    lines.append("from datetime import datetime, timezone\n")
    lines.append("from pydantic import BaseModel, ConfigDict\n")
    lines.append("from fastapi import APIRouter, Request, status, Depends, Header\n")
    lines.append("from sqlalchemy.orm import Session\n")
    lines.append("import pyapiafip as paa\n")
    lines.append("from app.services.database_service import Database\n")
    lines.append(f"from app.dbmodels import db_{table_name.lower()}")
    lines.append("\n")
    lines.append("#--------------------------------------------------------------------------------------\n")
    lines.append("router = APIRouter()\n")
    lines.append("#--------------------------------------------------------------------------------------\n\n")

#--------------------------------------------------------------------------------------
def add_class_model_api(lines:list[str], table_name:str)->None:
    class_name = "".join(word.capitalize() for word in table_name.split("_"))
    api_model_class_str = f"class {class_name}(BaseModel):\n"
    lines.append(api_model_class_str)

#--------------------------------------------------------------------------------------
def add_class_create_api(lines:list[str], table_name:str)->None:
    class_name = "".join(word.capitalize() for word in table_name.split("_"))
    api_create_class_str = f"class {class_name}Create(BaseModel):\n"
    lines.append(api_create_class_str)

#--------------------------------------------------------------------------------------
def add_class_update_api(lines:list[str], table_name:str)->None:
    class_name = "".join(word.capitalize() for word in table_name.split("_"))
    api_update_class_str = f"class {class_name}Update(BaseModel):\n"
    lines.append(api_update_class_str)

#--------------------------------------------------------------------------------------
def get_default(col_default:str):
    default:str|None=None
    if col_default:
        col_default = col_default.strip()
    # if 'DATE' in default or 'TIME' in default:
    if col_default and ('DATE' in col_default or 'TIME' in col_default):
        default = 'datetime.now(timezone.utc)'
    elif col_default and col_default.isdigit():
        default = int(col_default)
    elif col_default and col_default.startswith("'") and col_default.endswith("'"):
        default = col_default.strip("'")
        default = f'"{default}"'
    elif col_default and col_default.replace('.', '', 1).isdigit():
        default = float(col_default)
    elif col_default and 'CURRENT_TIMESTAMP' in col_default:
        default = 'server_default=func.now()'

    return default

#--------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------
def get_col_data (column):
    colname = column['name']
    coltype = column['type']
    nullable = column['nullable']
    colcomment = column['comment']
    coldefault = column.get('default', None)    

    default:str = get_default(col_default=coldefault)
    bd_type:str = get_db_type(column_type=coltype)
    python_type:str = get_python_type(column_type=column['type'])

    return colname, nullable, colcomment, default, bd_type, python_type

#--------------------------------------------------------------------------------------
def get_db_args (bd_type, nullable, default, colcomment):
    field_args = []
    field_args.append(bd_type)
    if nullable and default is None:
        field_args.append('default=None')
    if default is not None:
        field_args.append(f'default={default}')
    if colcomment:
        field_args.append(f'comment="{colcomment}"')

#--------------------------------------------------------------------------------------
def get_relations (colname, primary_keys, foreign_keys):
    relations = ""
    for fk in foreign_keys:
        if colname in fk['constrained_columns']:
            # field_args.append(f'ForeignKey({fk["referred_table"]}.{fk["referred_columns"][0]}")')
            relations += "    # parent = relationship ('Parent', back_populates='children')\n"
    if colname in primary_keys['constrained_columns']:
        # field_args.append('primary_key=True')
        relations += "    # children = relationship ('Child', back_populates='parent', cascade='all, delete')\n"

    return relations
#--------------------------------------------------------------------------------------

#--------------------------------------------------------------------------------------
def get_field(column, primary_keys, foreign_keys):
    colname = column['name']
    coltype = column['type']
    nullable = column['nullable']
    colcomment = column['comment']
    coldefault = column.get('default', None)    

    default:str = get_default(col_default=coldefault)
    bd_type:str = get_db_type(column_type=coltype)
    python_type:str = get_python_type(column_type=column['type'])

    field_args = []
    relations = ""
    field_args.append(bd_type)
    if default is not None:
        field_args.append(f'default={default}')
    if 'TIMESTAMP' in bd_type and 'CURRENT_TIMESTAMP' in coldefault:
        field_args.append('server_default=func.now()')
    for fk in foreign_keys:
        if colname in fk['constrained_columns']:
            # field_args.append(f'ForeignKey({fk["referred_table"]}.{fk["referred_columns"][0]}")')
            relations += "    # parent = relationship ('Parent', back_populates='children')\n"
    if colname in primary_keys['constrained_columns']:
        # field_args.append('primary_key=True')
        relations += "    # children = relationship ('Child', back_populates='parent', cascade='all, delete')\n"
    if colcomment:
        field_args.append(f'comment="{colcomment}"')

    field_args_str = ", ".join(field_args)    
    field_type_str = "Mapped[" + f"{python_type}" + ("|None" if nullable else "") + "]"

    class_db_str = f"    {colname.lower()}:{field_type_str} = mapped_column({field_args_str})\n"
    
    api_type_str = f"{python_type}" + ("|None = None" if nullable else "")
    api_model_class_str = f"    {colname.lower()}:{api_type_str}\n"
    api_create_class_str=""
    api_update_class_str=""
    api_create_class_str = f"{colname.lower()}:{api_type_str}"
    if colname.lower() not in primary_keys['constrained_columns']:
        api_update_class_str = f"{colname.lower()}:{python_type}|None = None"
        
    primary_key_type = f"{colname.lower()}:{python_type}"
    return class_db_str, api_model_class_str, api_create_class_str, api_update_class_str, relations, primary_key_type

#--------------------------------------------------------------------------------------
def add_config_db(lines:list[str], primary_keys, foreign_keys, indexes, constraints):
    # Configuración (primary key, foreing keys, indices y constraints)
    lines.append("    __table_args__ = (\n")
    if len(primary_keys['constrained_columns'])>0:
        pk_columns = ', '.join([f"{item}" for item in primary_keys['constrained_columns']])
        lines.append(f"        PrimaryKeyConstraint({pk_columns}, name='{primary_keys['name']}'),\n")
    else:
        lines.append(f"        PrimaryKeyConstraint(pk_columns, name='pk_name'), # TODO: Debe definir una PK para que sqlalchemy maneje correctamente los querys, aunque no este definida en la BD.\n")
    for fk in foreign_keys:
        fk_columns = ', '.join([f"{item}" for item in fk['constrained_columns']])
        fk_tablecol = ", ".join([f"'{fk['referred_table']}.{col}'" for col in fk['referred_columns']])
        lines.append("        # Descomentar la ForeignKeyConstraint una vez incoporado los modelos de las tablas foráneas\n")
        lines.append(f"        # ForeignKeyConstraint([{fk_columns}], [{fk_tablecol}]),\n")

    # SI SE DESEA DEFINIR LOS INDICES EN EL MODELO SE DEBE DESCOMENTAR LAS SIG 3 LINEAS DE CODIGO
    # SQLALCHEMY HACE USO DE ESTA DEFINICION SOLO AL MOMENTO DE CREAR LA TABLA, COSA QUE NO UTILIZAMOS            
    # for index in indexes:
    #     idx_columns = ', '.join([f"{item}" for item in index['column_names']])
    #     lines.append(f"        Index('{index['name']}', {idx_columns}, unique={index['unique']}),\n")

    for const in constraints:
        lines.append(f'        CheckConstraint(sqltext="{const['sqltext']}", name="{const['name']}"),\n')
    lines.append("    )\n")

    # lines.extend(relations)

#--------------------------------------------------------------------------------------
def add_crud(lines:list[str], table_name, primary_keys, primary_keys_type, es_vista):
    class_name = "".join(word.capitalize() for word in table_name.split("_"))
    db_class_name = f"DB{class_name}"
    table = table_name.lower()
    pk_columns = ', '.join([f"{item}" for item in primary_keys['constrained_columns']])
    pk_args = ', '.join([f"{item}" for item in primary_keys_type])
    if not pk_args:
        pk_args = "# TODO: completar argumentos con la lista de columnas PK"
    pk_params = ', \n'.join([f"        {db_class_name}.{item} == {item}" for item in primary_keys['constrained_columns']])
    if not pk_params:
        pk_params = f" # TODO: completar con los argumentos PK recibidos, ej: {db_class_name}.pk_column==pk_argument, {db_class_name}.pk_column2==pk_argument2"
    funciones_dbmodel = f'''
#--------------------------------------------------------------------------------------
def read(
    session:Session, 
    {pk_args}
):
    stm=sa_select({db_class_name}).where(
{pk_params}
    )
    result = session.execute(stm).scalar_one_or_none()
    return result

#--------------------------------------------------------------------------------------
def read_all(session:Session, offset:int=0, limit:int=100, order:str="asc"):
    stm = sa_select({db_class_name}).offset(offset).limit(limit)
    if order == "desc":
        stm = stm.order_by({', '.join([f"{db_class_name}.{item}.desc()" for item in primary_keys['constrained_columns']])})
    else:
        stm = stm.order_by({', '.join([f"{db_class_name}.{item}.asc()" for item in primary_keys['constrained_columns']])})

    result = session.execute(statement=stm).scalars().all()
    return result

'''
    if not es_vista:
        funciones_dbmodel = f'''{funciones_dbmodel}
#--------------------------------------------------------------------------------------
def create(session:Session, {table}:{db_class_name}):
    session.add({table})
    return {table}

# Alias para usar create o insert alternativamente
insert = create

#--------------------------------------------------------------------------------------
def update(
    session:Session, 
    {pk_args}, 
    {table}:{db_class_name}
):
    stm = sa_update({db_class_name}).where(
{pk_params}
    ).values({table}.model_dump(exclude_unset=True))
    result = session.execute(stm)
    return result.rowcount

#--------------------------------------------------------------------------------------
def delete(
    session:Session, 
    {pk_args}
):
    stm = sa_delete({db_class_name}).where(
{pk_params}    
    )
    result = session.execute(stm)
    return result.rowcount

#--------------------------------------------------------------------------------------
# Async functions
#--------------------------------------------------------------------------------------
async def read_async(
    session:Session, 
    {pk_args}
):
    return await sync_to_async.run_async(read, session, {pk_columns})

#--------------------------------------------------------------------------------------
async def read_all_async(session:Session, offset:int=0, limit:int=100, order:str="asc"):
    return await sync_to_async.run_async(read_all, session, offset, limit, order)

#--------------------------------------------------------------------------------------
async def create_async(session:Session, {table}:{db_class_name}):
    return await sync_to_async.run_async(create, {table})

#--------------------------------------------------------------------------------------
async def update_async(
    session:Session, 
    {pk_args}, 
    {table}:{db_class_name}
):
    return await sync_to_async.run_async(update, session, {pk_columns}, {table})

#--------------------------------------------------------------------------------------
async def delete_async(
    session:Session, 
    {pk_args}
):
    return await sync_to_async.run_async(delete, session, {pk_columns})    
'''
    
    lines.append(funciones_dbmodel)

#--------------------------------------------------------------------------------------
def add_routes(lines:list[str], table_name:str, sid, user, primary_keys, primary_keys_type, es_vista:bool):
    class_name = "".join(word.capitalize() for word in table_name.split("_"))
    db_class_name = f"DB{class_name}"
    table = table_name.lower()
    pk_args = ', '.join([f"{item}" for item in primary_keys_type])
    if not pk_args:
        pk_args = "# TODO: debe completar con los argumentos de las columnas PK que espera el método read del modelo de DB."
    pk_path = '/'.join([f"{{{item}}}" for item in primary_keys['constrained_columns']])
    pk_params = ', \n'.join([f"            {item}={item}" for item in primary_keys['constrained_columns']])
    if not pk_params:
        pk_params = "            # TODO: debe completar con los argumentos de las PK recibidos y que espera la función read del modelo de BD."
    pk_str = '[' + ', '.join([f"{item}={{{item}}}" for item in primary_keys['constrained_columns']]) + ']'

    router_lines = f"""
#--------------------------------------------------------------------------------------    
# Obtengo la sesion de la BD ('usuario@sid' del datasource)
def get_session():
    db:Database = paa.PyApiAFIP().get_service('{user}@{sid}')
    sess = db.get_session()
    yield from sess
"""
    router_lines += f'''
#--------------------------------------------------------------------------------------    
@router.get(
    "/{table}/{pk_path}", 
    response_model={class_name}, 
    status_code=status.HTTP_200_OK,
    responses={{**paa.responses.getOneCommonResponses, 200:{{ "model": {class_name} }}}}
)
# TODO: Para activar la auditoría de esta ruta, descomentar el decorador sig y el argumento audit de la función
#@audit_decorator(
#    db_service_name="{user}@{sid}",
#    descripcion="Consulta {table_name}")
def read(
    request:Request, 
    {pk_args}, 
    session:Session=Depends(get_session),
    # audit:str|None=Header(None,example='{{"id_token": "111111", "id_usuario": 20111111112, "id_representado": 20222222223}}')
):
    {table}=None
    try:
        {table} = db_{table}.read(
            session=session, 
{pk_params}
        )
        if {table} is None:
            raise paa.APIException (
                status_code=404, 
                developer_message=f"{pk_str} not found in {table}", 
                user_message="No se encuentra el registro buscado.",
                error_code=1001, 
                request=request 
            )
        return {table}
    except paa.APIException as err:
        raise err
    except Exception as err:
        raise paa.APIException (
            status_code=500, 
            developer_message=f"{{err}}", 
            user_message="Error al recuperar {table}.",
            error_code=1002, 
            request=request 
        )
            
#--------------------------------------------------------------------------------------    
@router.get(
    '/{table}',
    response_model=list[{class_name}], 
    status_code=status.HTTP_200_OK, 
    responses={{**paa.responses.getManyCommonResponses, 200:{{'model': list[{class_name}]}}}}
)
# TODO: Para activar la auditoría de esta ruta, descomentar el decorador sig y el argumento audit de la función
#@audit_decorator(
#    db_service_name="{user}@{sid}",
#    descripcion="Consulta todo {table_name}")
def read_all(
    request:Request, 
    offset:int=0, 
    limit:int=100, 
    session:Session=Depends(get_session),
    # audit:str|None=Header(None,example='{{"id_token": "111111", "id_usuario": 20111111112, "id_representado": 20222222223}}')
):
    try:
        {table} = db_{table}.read_all(session=session, offset=offset, limit=limit)
        return {table}
    except Exception as err:
        raise paa.APIException (
            status_code=500, 
            developer_message=f'{{err}}', 
            user_message="Error al recuperar {table}.",
            error_code=2001, 
            request=request 
        )
'''
    if not es_vista:
        router_lines = f'''{router_lines}

#--------------------------------------------------------------------------------------
@router.post(
    "/{table}", 
    response_model={class_name}, 
    status_code=status.HTTP_201_CREATED, 
    responses={{**paa.responses.postCommonResponses}}
)
# TODO: Para activar la auditoría de esta ruta, descomentar el decorador sig y el argumento audit de la función
#@audit_decorator(
#    db_service_name="{user}@{sid}",
#    descripcion="Crea {table_name}")
def create(
    request:Request, 
    {table}:{class_name}Create, 
    session:Session=Depends(get_session),
    # audit:str|None=Header(None,example='{{"id_token": "111111", "id_usuario": 20111111112, "id_representado": 20222222223}}')
):
    try:
        db_reg = db_{table}.{db_class_name}(**{table}.model_dump())
        registro = db_{table}.create(session=session, {table}=db_reg)
        session.commit()
        return registro
    except Exception as err:
        session.rollback()
        raise paa.APIException (
            status_code=500, 
            developer_message=f"{{err}}", 
            user_message="Error al intentar crear {table}.",
            error_code=3001, 
            request=request 
        )    

#--------------------------------------------------------------------------------------
@router.patch(
    "/{table}/{pk_path}", 
    response_model=UpdateResponse, 
    status_code=status.HTTP_200_OK, 
    responses={{**paa.responses.putCommonResponses}}
)
# TODO: Para activar la auditoría de esta ruta, descomentar el decorador sig y el argumento audit de la función
#@audit_decorator(
#    db_service_name="{user}@{sid}",
#    descripcion="Actualiza {table_name}")
def update(
    request:Request, 
    {pk_args}, 
    {table}:{class_name}Update, 
    session:Session=Depends(get_session),
    # audit:str|None=Header(None,example='{{"id_token": "111111", "id_usuario": 20111111112, "id_representado": 20222222223}}')
):
    try:
        result = db_{table}.update (
            session=session, 
{pk_params}, 
            {table}={table}
        )
        session.commit()
        if result < 1:
            raise paa.APIException (
                status_code=404, 
                developer_message=f"{pk_str} not found in {table}", 
                user_message="No se encuentra el registro a actualizar.",
                error_code=4001, 
                request=request 
            )
        return UpdateResponse(rows_affected=result)
    except paa.APIException as err:
        session.rollback()
        raise err
    except Exception as err:
        session.rollback()
        raise paa.APIException (
            status_code=500, 
            developer_message=f"{{err}}", 
            user_message="Error al actualizar {table}.", 
            error_code=4002, 
            request=request
        )        

#--------------------------------------------------------------------------------------
@router.delete(
    "/{table}/{pk_path}", 
    status_code=status.HTTP_204_NO_CONTENT, 
    responses={{**paa.responses.deleteCommonResponses}}
)
# TODO: Para activar la auditoría de esta ruta, descomentar el decorador sig y el argumento audit de la función
#@audit_decorator(
#    db_service_name="{user}@{sid}",
#    descripcion="Elimina {table_name}")
def delete(
    request:Request, 
    {pk_args}, 
    session:Session=Depends(get_session),
    # audit:str|None=Header(None,example='{{"id_token": "111111", "id_usuario": 20111111112, "id_representado": 20222222223}}')
):
    try:
        result = db_{table}.delete(
            session=session, 
{pk_params}
        )
        session.commit()
        if result<1:
            raise paa.APIException (
                status_code=404, 
                developer_message=f"{pk_str} not found in {table}", 
                user_message="No se encuentra el registro a eliminar.",
                error_code=5001, 
                request=request
            )    
        return result
    except paa.APIException as err:
        session.rollback()
        raise err
    except Exception as err:
        session.rollback()
        raise paa.APIException (
            status_code=500, 
            developer_message=f"{{err}}", 
            user_message="No se puedo eliminar {table}.",
            error_code=5002, 
            request=request
        )   
'''
    lines.append(router_lines)

#--------------------------------------------------------------------------------------
def add_update_response(lines:list[str]):
    class_ud_response:str = """
class UpdateResponse(BaseModel):
    rows_affected:int
"""
    lines.append(class_ud_response)

#--------------------------------------------------------------------------------------
def add_func_separator(lines:list[str]):
    lines.append("#--------------------------------------------------------------------------------------")

#--------------------------------------------------------------------------------------
def generate_model_code(table_name, columns:list[ReflectedColumn], primary_keys, foreign_keys, indexes, constraints, sid, user, es_vista:bool):
    db_lines:list[str]=[]
    api_lines:list[str]=[]
    test_lines:list[str]=[]
    api_model_lines:list[str]=[]
    api_create_lines:list[str]=[]
    api_update_lines:list[str]=[]
    add_imports_db(db_lines)
    add_imports_api(api_lines, table_name=table_name)
    
    add_class_db(lines=db_lines, table_name=table_name)
    print("Agregando clases")
    add_class_model_api(lines=api_model_lines, table_name=table_name)
    if not es_vista:
        add_class_create_api(lines=api_create_lines, table_name=table_name)
        add_class_update_api(lines=api_update_lines, table_name=table_name)

    relations=[]
    primary_keys_type=[]
    create_fields=[]
    all_cols = []
    no_pk_cols = []

    for column in columns:
        field_db, field_model, field_create, field_update, field_relations, primary_key_type = get_field(
            column=column, 
            primary_keys=primary_keys,
            foreign_keys=foreign_keys
        )
        db_lines.append(field_db)
        api_model_lines.append(field_model)
        if not es_vista:
            api_create_lines.append(f"    {field_create}\n")
        relations.append(field_relations)
        if column['name'] in primary_keys['constrained_columns']:
            primary_keys_type.append(primary_key_type)
        else:
            if not es_vista:
                api_update_lines.append(f"    {field_update}\n")
            no_pk_cols.append(f"{column['name']}")
        all_cols.append(f"{column['name']}")

        create_fields.append(f"{field_create}")

    api_model_lines.append("\n    model_config = ConfigDict(from_attributes=True)\n")

    db_lines.append("\n")
    add_config_db(db_lines, primary_keys, foreign_keys, indexes, constraints)
    print("Agregando configuraciones")
    db_lines.append("\n")
    db_lines.append("    # Si la tabla posee relaciones con otras se pueden incorporar descomentando y configurando las siguientes lineas\n")
    db_lines.extend(relations)
    db_lines.append("\n")
    add_crud(lines=db_lines, table_name=table_name, primary_keys=primary_keys, primary_keys_type=primary_keys_type, es_vista=es_vista)
    db_lines.append("\n")

    api_lines.extend(api_model_lines)
    api_lines.append("\n")
    api_lines.append("# El modelo para crear solo precisa los campos no autogenerados (secuencias o defaults)\n")
    api_lines.append("# Eliminar del siguiente modelo si se da el caso\n")
    api_lines.extend(api_create_lines)
    api_lines.append("\n")
    api_lines.append("# El modelo para actualizar solo precisa los campos que no son primary keys\n")
    api_lines.extend(api_update_lines)
    if not es_vista:
        add_update_response(lines=api_lines)
    add_routes(lines=api_lines, table_name=table_name, sid=sid, user=user, primary_keys=primary_keys, primary_keys_type=primary_keys_type, es_vista=es_vista)

    test_gen.add_imports(lines=test_lines)
    add_func_separator(lines=test_lines)
    print("agregando separadores")
    test_gen.add_pytest_fixture(lines=test_lines)
    test_gen.add_tests(lines=test_lines, table_name=table_name, primary_keys=primary_keys, create_fields=create_fields, all_cols=all_cols, no_pk_cols=no_pk_cols, es_vista=es_vista)
    print("terminando model code")
    return "".join(db_lines), "".join(api_lines), "".join(test_lines)
#--------------------------------------------------------------------------------------
def generate_base_class():
    base_class:str = """
from sqlalchemy.orm import DeclarativeBase

class DBBase(DeclarativeBase):
    def dict(self,exclude_unset:bool=False):
        data = {field.name:getattr(self, field.name) for field in self.__table__.c}
        if exclude_unset:
            # Excluir atributos sin valor (None)
            data = {key: value for key, value in data.items() if value is not None}
        return data

    def model_dump(self,exclude_unset:bool=False):
        data = {field.name:getattr(self, field.name) for field in self.__table__.c}
        if exclude_unset:
            # Excluir atributos sin valor (None)
            data = {key: value for key, value in data.items() if value is not None}
        return data
"""
    return base_class

#--------------------------------------------------------------------------------------
def question(question:str):
    done=False
    while not done:
        rta = input(f"{question}")
        if rta.lower() in ["s", "n"]:
            done = True    
    return rta

#--------------------------------------------------------------------------------------
def generate_file(file_name:str, model:str):
    rta:str='s'
    if os.path.isfile(file_name):
        rta = question(f"El archivo {file_name} ya existe, desea sobreescribirlo (s/n)?")
    if rta.lower() == 's':
        with open(f"{file_name}", "w") as file:
            file.write(model)
        print(f"El modelo se escribió en {file_name}\n")
    else:
        print(f"El archivo {file_name} NO se generó.\n")

#--------------------------------------------------------------------------------------
def main(ip, port, sid, user, password, table_name):
    model_file=f"{MODEL_PATH}/db_{table_name.lower()}.py"
    route_file=f"{ROUTE_PATH}/{table_name.lower()}.py"
    test_file=f"{test_gen.TEST_PATH}/test_{table_name.lower()}.py"
    try:
        #base_class = generate_base_class()
        columns, primary_keys, foreign_keys, indexes, constraints, es_vista = get_table_metadata(ip, port, sid, user, password, table_name)
        if es_vista:
            print("\nSE ESTA CREANDO EL MODELO DE UNA VISTA.\n")
        db_model, api_model, test_model = generate_model_code(table_name, columns, primary_keys, foreign_keys, indexes, constraints, sid, user, es_vista)
        print(f"Model file path: {model_file}")
        generate_file(file_name=model_file, model=db_model)
        print("generacion de archivo model")
        generate_file(file_name=route_file, model=api_model)
        print("generacion de archivo route")
        generate_file(file_name=test_file, model=test_model)
        print(f"{test_model=}")

    except Exception as err:
        print(f"{err.__doc__}: {err}")

#--------------------------------------------------------------------------------------
if __name__ == "__main__":
    if len(sys.argv) != 7:
        print("Usage: python model_generator.py <ip> <port> <sid> <user> <password> <table_name>")
        print("<ip>: ip de la BD")
        print("<port>: puerto de la BD")
        print("<sid>: sid de la BD")
        print("<user>: usuario de conexión a la BD")
        print("<password>: clave del usuario de conexión a la BD")
        print("<table_name>: nombre de la tabla que se generará el modelo")
        sys.exit(1)
    
    print("\nLOS MODELOS GENERADOS PRECISAN DE PRIMARY KEYS, DE OTRA FORMA SQLALCHEMY NO PUEDE MANEJAR LAS TABLAS CORRECTAMENTE.")
    print("\nSi la tabla no posee primery keys o se trata de una vista, las PK deben ser definidas en el modelo sqlalchemy de todas maneras.")
    print("\nPara incorporar el route generado debe agregar el import y agregar la ruta a la app (app.include_router) en main.py")

    ip = sys.argv[1]
    port = sys.argv[2]
    sid = sys.argv[3]
    user = sys.argv[4]
    password = sys.argv[5]
    table_name = sys.argv[6]

    print(f"\nProcesando {user}.{table_name}@{sid}...\n")

    main(ip, port, sid, user, password, table_name)

    print("\nVERIFICAR EN LOS MODELOS LOS COMENTARIOS CON LA LEYENDA TODO, YA QUE PRECISAN DE SU CORRECCIÓN MANUAL.")
    print("\n\nFIN de la generación.")
