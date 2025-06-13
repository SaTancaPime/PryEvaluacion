from decouple import config

class Config:
    SECRET_KEY = config('SECRET_KEY')
    
    POSTGRES_USER = config('POSTGRES_USER')
    POSTGRES_PASSWORD = config('POSTGRES_PASSWORD')
    POSTGRES_HOST = config('POSTGRES_HOST')
    POSTGRES_DB = config('POSTGRES_DB')
    
    DATABASE_URI = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}/{POSTGRES_DB}"
    
class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False
    
class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    
configurations = {
    'development': DevelopmentConfig,
    'production': ProductionConfig
}