from flask import Blueprint, request, jsonify
from extensions import db
from sqlalchemy import text
from flask_jwt_extended import jwt_required

events_bp = Blueprint('events', __name__)

# --- 1. CREATE EVENT (Ditambah edited_id) ---
@events_bp.route('/add', methods=['POST'])
@jwt_required()
def add_event():
    data = request.json
    nama = data.get('nama_events')
    kode = data.get('kode_folder')
    edited_id = data.get('edited_id') # Ambil nilai edited_id dari request

    if not nama or not kode:
        return jsonify({"message": "Nama event dan kode folder wajib diisi"}), 400

    try:
        # Masukkan edited_id ke dalam query insert
        query = text("INSERT INTO events (nama_events, kode_folder, edited_id) VALUES (:n, :k, :eid)")
        db.session.execute(query, {'n': nama, 'k': kode, 'eid': edited_id})
        db.session.commit()
        return jsonify({"status": "success", "message": "Event berhasil ditambahkan"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500

# --- 2. READ ALL EVENTS (Ditambah kolom edited_id) ---
@events_bp.route('/', methods=['GET'])
def get_all_events():
    # Tambahkan edited_id dalam SELECT
    query = text("SELECT id, nama_events, kode_folder, created_at, edited_id FROM events")
    result = db.session.execute(query).fetchall()
    
    events = []
    for row in result:
        events.append({
            "id": row[0],
            "nama_events": row[1],
            "kode_folder": row[2],
            "created_at": row[3],
            "edited_id": row[4] # Masukkan ke dalam list
        })
    return jsonify(events), 200

# --- 3. UPDATE EVENT (Ditambah update edited_id) ---
@events_bp.route('/update/<int:id>', methods=['PUT'])
@jwt_required()
def update_event(id):
    data = request.json
    nama = data.get('nama_events')
    kode = data.get('kode_folder')
    edited_id = data.get('edited_id') # Ambil nilai baru edited_id

    try:
        # Tambahkan edited_id di query UPDATE
        query = text("UPDATE events SET nama_events = :n, kode_folder = :k, edited_id = :eid WHERE id = :id")
        db.session.execute(query, {'n': nama, 'k': kode, 'eid': edited_id, 'id': id})
        db.session.commit()
        return jsonify({"message": "Event berhasil diperbarui"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# --- 4. DELETE EVENT (Tetap sama) ---
@events_bp.route('/delete/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_event(id):
    try:
        query = text("DELETE FROM events WHERE id = :id")
        db.session.execute(query, {'id': id})
        db.session.commit()
        return jsonify({"message": "Event berhasil dihapus"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500