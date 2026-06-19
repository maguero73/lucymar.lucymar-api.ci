import pyapiafip as paa
from app.services import database_service, http_service, elastic_service, s3_service, smtp_service

#--------------------------------------------------------------------------------------
def get_db_event_service()->database_service.Database:
    service:database_service.Database = paa.get_fastapi_app().get_service("pub_app@event")
    return service

#--------------------------------------------------------------------------------------
def get_db_fisco_service()->database_service.Database:
    service:database_service.Database = paa.get_fastapi_app().get_service("pub_app@fisco")
    return service