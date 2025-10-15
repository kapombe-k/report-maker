from flask import Flask
from flask_restful import Api
from flask_cors import CORS
from flask_migrate import Migrate
from models import db
from resources.collections import CollectionResource
from resources.expenses import ExpenseResource
from resources.reports import ReportResource
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# Database configuration
environment = os.getenv('ENVIRONMENT')
print(f"Environment: {environment}")
if environment == 'production':
    database_url = os.environ.get('SUPABASE_URL')
else:
    database_url = os.environ.get('DATABASE_URL')
    print(f"Development DATABASE_URL: {database_url}")

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db)
api = Api(app)

# Register resources
api.add_resource(CollectionResource, '/api/collections', '/api/collections/<string:date>')
api.add_resource(ExpenseResource, '/api/expenses', '/api/expenses/<string:date>')
api.add_resource(ReportResource, '/api/reports/<string:type>/<string:param>')

if __name__ == '__main__':
    app.run(debug=True, port=5000)