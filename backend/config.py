from dotenv import load_dotenv   #for python-dotenv method
load_dotenv()
import os

USER = os.environ.get('US')
PASSWORD = os.environ.get('PASSWORD')
#print("USER: " + USER)
#print("PASSWORD: " + PASSWORD)

class Config:
   SQLALCHEMY_TRACK_MODIFICATIONS = False

   @staticmethod
   def init_app(app):
       pass

class DevelopmentConfig(Config):
   DEBUG=True
   SQLALCHEMY_DATABASE_URI = f'postgresql://{USER}:{PASSWORD}@localhost:5432/trivia'

class TestingConfig(Config):
   DEBUG = True
   TESTING = True
   SQLALCHEMY_DATABASE_URI = f'postgresql://{USER}:{PASSWORD}@localhost:5432/trivia_test'


config = {
   'development': DevelopmentConfig,
   'testing': TestingConfig,

   'default': DevelopmentConfig}
