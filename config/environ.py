from pydantic_settings import BaseSettings




class Settings(BaseSettings):
    database_hostname: str
    database_port: str
    database_password: str
    database_name:str
    database_username:str
    database_hostname_dev: str
    database_port_dev: str
    database_password_dev: str
    database_name_dev:str
    database_username_dev:str
    database_production_server:str
    secret_key:str
    algorithm:str
    access_token_expire_minutes: int
    refresh_token_expire_days: int
    reset_password_token_expire_minutes: int
    email: str
    email_password: str
    email_port:int
    email_server: str
    stripe_secret_key : str
    
    class Config:
        env_file= ".env"


settings = Settings()


