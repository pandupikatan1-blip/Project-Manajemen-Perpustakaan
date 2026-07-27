from flask import Flask, render_template, request, redirect, url_for, session, flash
import psycopg2
from functools import wraps

app = Flask(__name__)
app.secret_key = 'libhub_executive_secure_key_2026'

DB_URL = "postgresql://postgres:%23Adminlib1234@db.qdxxultnxzwvcmgqxeck.supabase.co:6543/postgres"

def get_db_connection():
    return psycopg2.connect(DB_URL)

# Decorator untuk mengamankan halaman agar wajib login
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, username, nama FROM admin WHERE username = %s AND password = %s;", (username, password))
        admin_user = cur.fetchone()
        cur.close()
        conn.close()
        
        if admin_user:
            session['logged_in'] = True
            session['admin_id'] = admin_user[0]
            session['admin_name'] = admin_user[2]
            return redirect(url_for('dashboard'))
        else:
            flash('Kredensial salah. Silakan periksa kembali username dan password Anda.', 'danger')
            return redirect(url_for('login'))
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def dashboard():
    search_query = request.args.get('search_query', '').strip()
    search_results = []
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Metrik Dashboard
    cur.execute("SELECT COUNT(*) FROM anggota;")
    total_anggota = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM buku;")
    total_buku = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM kategori;")
    total_kategori = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM peminjaman WHERE status = 'Dipinjam';")
    pinjam_aktif = cur.fetchone()[0]
    
    cur.execute("SELECT COALESCE(SUM(denda), 0) FROM peminjaman;")
    total_denda = cur.fetchone()[0]
    
    # Fitur Pencarian Status Buku
    if search_query:
        cur.execute("""
            SELECT b.id, b.judul, b.penulis, 
                   CASE WHEN EXISTS (
                       SELECT 1 FROM peminjaman p WHERE p.id_buku = b.id AND p.status = 'Dipinjam'
                   ) THEN 'Dipinjam' ELSE 'Tersedia' END as status_pinjam
            FROM buku b
            WHERE b.judul ILIKE %s OR b.penulis ILIKE %s
            ORDER BY b.judul ASC;
        """, (f"%{search_query}%", f"%{search_query}%"))
        search_results = cur.fetchall()
        
    cur.close()
    conn.close()
    
    return render_template('dashboard.html', 
                           total_anggota=total_anggota, 
                           total_buku=total_buku, 
                           total_kategori=total_kategori, 
                           pinjam_aktif=pinjam_aktif, 
                           total_denda=total_denda,
                           search_query=search_query,
                           search_results=search_results)

# --- CRUD KATEGORI ---
@app.route('/kategori', methods=['GET'])
@login_required
def kategori():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, nama_kategori FROM kategori ORDER BY id ASC;")
    kategori_list = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('kategori.html', kategori=kategori_list)

@app.route('/kategori/add', methods=['POST'])
@login_required
def kategori_add():
    nama_kategori = request.form['nama_kategori']
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO kategori (nama_kategori) VALUES (%s);", (nama_kategori,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('kategori'))

@app.route('/kategori/edit/<int:id>', methods=['POST'])
@login_required
def kategori_edit(id):
    nama_kategori = request.form['nama_kategori']
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE kategori SET nama_kategori = %s WHERE id = %s;", (nama_kategori, id))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('kategori'))

@app.route('/kategori/delete/<int:id>', methods=['POST'])
@login_required
def kategori_delete(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM kategori WHERE id = %s;", (id,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('kategori'))

# --- CRUD BUKU ---
@app.route('/buku', methods=['GET'])
@login_required
def buku():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT b.id, b.judul, b.penulis, b.penerbit, b.tahun_terbit, k.nama_kategori, b.id_kategori 
        FROM buku b 
        LEFT JOIN kategori k ON b.id_kategori = k.id 
        ORDER BY b.id ASC;
    """)
    buku_list = cur.fetchall()
    cur.execute("SELECT id, nama_kategori FROM kategori ORDER BY nama_kategori ASC;")
    kategori_options = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('buku.html', buku=buku_list, kategori_options=kategori_options)

@app.route('/buku/add', methods=['POST'])
@login_required
def buku_add():
    judul = request.form['judul']
    penulis = request.form['penulis']
    penerbit = request.form['penerbit']
    tahun_terbit = request.form['tahun_terbit']
    id_kategori = request.form['id_kategori']
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO buku (judul, penulis, penerbit, tahun_terbit, id_kategori) 
        VALUES (%s, %s, %s, %s, %s);
    """, (judul, penulis, penerbit, tahun_terbit, id_kategori if id_kategori else None))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('buku'))

@app.route('/buku/edit/<int:id>', methods=['POST'])
@login_required
def buku_edit(id):
    judul = request.form['judul']
    penulis = request.form['penulis']
    penerbit = request.form['penerbit']
    tahun_terbit = request.form['tahun_terbit']
    id_kategori = request.form['id_kategori']
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE buku SET judul = %s, penulis = %s, penerbit = %s, tahun_terbit = %s, id_kategori = %s 
        WHERE id = %s;
    """, (judul, penulis, penerbit, tahun_terbit, id_kategori if id_kategori else None, id))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('buku'))

@app.route('/buku/delete/<int:id>', methods=['POST'])
@login_required
def buku_delete(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM buku WHERE id = %s;", (id,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('buku'))

# --- CRUD ANGGOTA ---
@app.route('/anggota', methods=['GET'])
@login_required
def anggota():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, nim_nik, nama_anggota, email, status FROM anggota ORDER BY id ASC;")
    anggota_list = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('anggota.html', anggota=anggota_list)

@app.route('/anggota/add', methods=['POST'])
@login_required
def anggota_add():
    nim_nik = request.form['nim_nik']
    nama_anggota = request.form['nama_anggota']
    email = request.form['email']
    status = request.form['status']
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO anggota (nim_nik, nama_anggota, email, status) VALUES (%s, %s, %s, %s);",
                (nim_nik, nama_anggota, email, status))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('anggota'))

@app.route('/anggota/edit/<int:id>', methods=['POST'])
@login_required
def anggota_edit(id):
    nim_nik = request.form['nim_nik']
    nama_anggota = request.form['nama_anggota']
    email = request.form['email']
    status = request.form['status']
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE anggota SET nim_nik = %s, nama_anggota = %s, email = %s, status = %s WHERE id = %s;",
                (nim_nik, nama_anggota, email, status, id))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('anggota'))

@app.route('/anggota/delete/<int:id>', methods=['POST'])
@login_required
def anggota_delete(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM anggota WHERE id = %s;", (id,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('anggota'))

# --- CRUD PEMINJAMAN ---
@app.route('/peminjaman', methods=['GET'])
@login_required
def peminjaman():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT p.id, a.nama_anggota, b.judul, p.tanggal_pinjam, p.tanggal_kembali, p.status, p.denda, p.id_anggota, p.id_buku 
        FROM peminjaman p
        JOIN anggota a ON p.id_anggota = a.id
        JOIN buku b ON p.id_buku = b.id
        ORDER BY p.id ASC;
    """)
    peminjaman_list = cur.fetchall()
    
    cur.execute("SELECT id, nama_anggota, nim_nik FROM anggota WHERE status = 'Aktif' ORDER BY nama_anggota ASC;")
    anggota_options = cur.fetchall()
    
    cur.execute("SELECT id, judul FROM buku ORDER BY judul ASC;")
    buku_options = cur.fetchall()
    
    cur.close()
    conn.close()
    return render_template('peminjaman.html', peminjaman=peminjaman_list, anggota_options=anggota_options, buku_options=buku_options)

@app.route('/peminjaman/add', methods=['POST'])
@login_required
def peminjaman_add():
    id_anggota = request.form['id_anggota']
    id_buku = request.form['id_buku']
    tanggal_pinjam = request.form['tanggal_pinjam']
    tanggal_kembali = request.form['tanggal_kembali']
    status = request.form['status']
    denda = request.form['denda']
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO peminjaman (id_anggota, id_buku, tanggal_pinjam, tanggal_kembali, status, denda) 
        VALUES (%s, %s, %s, %s, %s, %s);
    """, (id_anggota, id_buku, tanggal_pinjam, tanggal_kembali if tanggal_kembali else None, status, denda if denda else 0))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('peminjaman'))

@app.route('/peminjaman/edit/<int:id>', methods=['POST'])
@login_required
def peminjaman_edit(id):
    id_anggota = request.form['id_anggota']
    id_buku = request.form['id_buku']
    tanggal_pinjam = request.form['tanggal_pinjam']
    tanggal_kembali = request.form['tanggal_kembali']
    status = request.form['status']
    denda = request.form['denda']
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE peminjaman SET id_anggota = %s, id_buku = %s, tanggal_pinjam = %s, tanggal_kembali = %s, status = %s, denda = %s 
        WHERE id = %s;
    """, (id_anggota, id_buku, tanggal_pinjam, tanggal_kembali if tanggal_kembali else None, status, denda if denda else 0, id))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('peminjaman'))

@app.route('/peminjaman/delete/<int:id>', methods=['POST'])
@login_required
def peminjaman_delete(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM peminjaman WHERE id = %s;", (id,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('peminjaman'))

if __name__ == '__main__':
    app.run(debug=True)
