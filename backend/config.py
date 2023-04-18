class Config:
   SQLALCHEMY_TRACK_MODIFICATIONS = False

   @staticmethod
   def init_app(app):
       pass

class DevelopmentConfig(Config):
   DEBUG=True
   SQLALCHEMY_DATABASE_URI = 'postgresql://hui:yji3jo6@localhost:5432/trivia'

class TestingConfig(Config):
   DEBUG = True
   TESTING = True
   SQLALCHEMY_DATABASE_URI = 'postgresql://hui:yji3jo6@localhost:5432/trivia_test'


config = {
   'development': DevelopmentConfig,
   'testing': TestingConfig,

   'default': DevelopmentConfig}
