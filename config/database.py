from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config.environ import settings





SQLALCHEMY_DATABASE_URL_DEVELOPMENT = f"postgresql://{settings.database_username_dev}:{settings.database_password_dev}@{settings.database_hostname_dev}:{settings.database_port_dev}/{settings.database_name_dev}"
SQLALCHEMY_DATABASE_URL_PRODUCTION = f"postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}?sslmode=require"


if settings.database_production_server == 'false':
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL_DEVELOPMENT
    )
else :
     engine = create_engine(
        SQLALCHEMY_DATABASE_URL_PRODUCTION
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()