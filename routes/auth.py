from flask import Blueprint, request, jsonify
from extensions import db
from sqlalchemy import text 
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

auth_bp = Blueprint('auth', __name__)

# --- 1. REGISTER ---
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    # Default role ke 'user' jika tidak diisi
    role = data.get('role') if data.get('role') else 'user'

    if not username or not email or not password:
        return jsonify({"message": "Data tidak lengkap"}), 400

    hashed_pw = generate_password_hash(password)

    try:
        query = text("INSERT INTO users (username, email, password, role) VALUES (:u, :e, :p, :r)")
        db.session.execute(query, {'u': username, 'e': email, 'p': hashed_pw, 'r': role})
        db.session.commit()
        
        return jsonify({"status": "success", "message": "User berhasil terdaftar!"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500


# --- 2. LOGIN ---
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"message": "Username dan password wajib diisi"}), 400

    query = text("SELECT id, username, password, role FROM users WHERE username = :u")
    result = db.session.execute(query, {'u': username}).fetchone()

    if result and check_password_hash(result[2], password):
        # Buat Token JWT
        access_token = create_access_token(
            identity=str(result[0]), 
            additional_claims={"role": result[3], "username": result[1]}
        )
        
        return jsonify({
            "status": "success",
            "message": "Login Berhasil",
            "access_token": access_token,
            "user": {
                "id": result[0],
                "username": result[1],
                "role": result[3]
            }
        }), 200
    
    return jsonify({"status": "error", "message": "Username atau password salah"}), 401


# --- 3. GET SEMUA USER (Daftar User & Fotonya) ---
@auth_bp.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    query = text("SELECT id, username, email, role, foto_yang_dipilih FROM users")
    result = db.session.execute(query).fetchall()
    
    users = []
    for row in result:
        users.append({
            "id": row[0],
            "username": row[1],
            "email": row[2],
            "role": row[3],
            "foto_yang_dipilih": row[4] if row[4] else "" # Handle null jadi string kosong
        })
    return jsonify(users), 200


# --- 4. GET PROFIL SAYA (Detail User Login) ---
@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    user_id = get_jwt_identity()
    query = text("SELECT id, username, email, role, foto_yang_dipilih FROM users WHERE id = :id")
    user = db.session.execute(query, {'id': user_id}).fetchone()
    
    if not user:
        return jsonify({"message": "User tidak ditemukan"}), 404

    return jsonify({
        "id": user[0],
        "username": user[1],
        "email": user[2],
        "role": user[3],
        "foto_yang_dipilih": user[4] if user[4] else ""
    }), 200


# --- 5. UPDATE FOTO YANG DIPILIH ---
@auth_bp.route('/update-photos', methods=['POST'])
@jwt_required()
def update_photos():
    data = request.json
    # Data dari frontend berupa string: "foto1.jpg, foto2.jpg"
    foto_string = data.get('foto_yang_dipilih') 
    user_id = get_jwt_identity()

    if foto_string is None:
        return jsonify({"message": "Pilihan foto tidak boleh kosong"}), 400

    try:
        query = text("UPDATE users SET foto_yang_dipilih = :f WHERE id = :id")
        db.session.execute(query, {'f': foto_string, 'id': user_id})
        db.session.commit()

        return jsonify({
            "status": "success",
            "message": "Daftar foto berhasil disimpan!"
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500


# --- 6. DELETE USER ---
@auth_bp.route('/delete/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_user(id):
    try:
        query = text("DELETE FROM users WHERE id = :id")
        db.session.execute(query, {'id': id})
        db.session.commit()
        return jsonify({"status": "success", "message": f"User ID {id} berhasil dihapus"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500