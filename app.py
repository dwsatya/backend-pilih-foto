import os
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
from extensions import db
from flask_jwt_extended import JWTManager
from routes.events import events_bp
from routes.auth import auth_bp

# 1. Load env
load_dotenv()

app = Flask(__name__)
CORS(app)

# 2. Ambil URL dari .env
# Hapus logika db_user, db_pass, db_host yang lama!
db_url = os.getenv("DATABASE_URL")

# 3. FIX: SQLAlchemy butuh prefix 'postgresql://' dan handle karakter khusus
if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

# Pastikan password yang mengandung '@' sudah di-encode manual di .env menjadi '%40'
app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'dwsatya') 

# 4. Hubungkan app dengan db
db.init_app(app)
jwt = JWTManager(app)

# 5. Register Blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(events_bp, url_prefix='/events')

if __name__ == '__main__':
    with app.app_context():
        try:
            db.create_all()
            print("--- Berhasil Terhubung ke Supabase (PostgreSQL) ---")
        except Exception as e:
            print(f"--- Gagal terhubung ke database: {e} ---")
            
    app.run(debug=True, port=5000)