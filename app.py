import os
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
from extensions import db
from flask_jwt_extended import JWTManager

# 1. Load env (untuk lokal)
load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# 2. Konfigurasi Database (Koyeb & Supabase Friendly)
db_url = os.getenv("DATABASE_URL")

if not db_url:
    # Jika variabel di dashboard Koyeb belum diisi, gunakan SQLite agar tidak crash
    print("--- WARNING: DATABASE_URL tidak ditemukan, menggunakan SQLite sementara ---")
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fallback.db'
else:
    # Perbaikan prefix untuk PostgreSQL (Wajib untuk SQLAlchemy)
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'dwsatya') 

# 3. Hubungkan app dengan db & JWT
db.init_app(app)
jwt = JWTManager(app)

# 4. Register Blueprints (Import di sini untuk menghindari circular import)
from routes.auth import auth_bp
from routes.events import events_bp

app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(events_bp, url_prefix='/events')

# 5. Otomatis buat tabel saat aplikasi start di Cloud (Koyeb)
with app.app_context():
    try:
        db.create_all()
        print("--- Database Berhasil Sinkron ---")
    except Exception as e:
        print(f"--- Gagal sinkronisasi Database: {e} ---")

# 6. Jalankan Server (Hanya untuk lokal)
if __name__ == '__main__':
    app.run(debug=True, port=5000)