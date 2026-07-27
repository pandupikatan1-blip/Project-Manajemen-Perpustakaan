CREATE TABLE admin (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    nama VARCHAR(100),
    email VARCHAR(100)
);

CREATE TABLE kategori (
    id SERIAL PRIMARY KEY,
    nama_kategori VARCHAR(100) NOT NULL
);

CREATE TABLE buku (
    id SERIAL PRIMARY KEY,
    judul VARCHAR(255) NOT NULL,
    penulis VARCHAR(100),
    penerbit VARCHAR(100),
    tahun_terbit INT,
    id_kategori INT REFERENCES kategori(id) ON DELETE SET NULL
);

CREATE TABLE anggota (
    id SERIAL PRIMARY KEY,
    nim_nik VARCHAR(50) UNIQUE NOT NULL,
    nama_anggota VARCHAR(100) NOT NULL,
    email VARCHAR(100),
    status VARCHAR(20) DEFAULT 'Aktif'
);

CREATE TABLE peminjaman (
    id SERIAL PRIMARY KEY,
    id_anggota INT REFERENCES anggota(id) ON DELETE CASCADE,
    id_buku INT REFERENCES buku(id) ON DELETE CASCADE,
    tanggal_pinjam DATE NOT NULL DEFAULT CURRENT_DATE,
    tanggal_kembali DATE,
    status VARCHAR(20) DEFAULT 'Dipinjam',
    denda INT DEFAULT 0
);
