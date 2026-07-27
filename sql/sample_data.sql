-- A. Input Data Operator Admin (Password: admin123)
INSERT INTO admin (username, password, nama, email) 
VALUES ('admin', 'admin123', 'Super Admin LibHub', 'admin@libhub.co');

-- B. Input 3 Kategori Buku Wajib
INSERT INTO kategori (nama_kategori) VALUES
('Teknologi & Coding'),
('Sains Data & AI'),
('Fiksi & Novel');

-- C. Input 5 Entitas Data Anggota / Members (Sesuai Request Kelompok)
INSERT INTO anggota (nim_nik, nama_anggota, email, status) VALUES
('24.83.1120', 'Pandu Restu', 'pandu.restu@student.ac.id', 'Aktif'),
('24.83.1102', 'Haris', 'haris@student.ac.id', 'Aktif'),
('24.83.1143', 'Cadenza', 'cadenza@student.ac.id', 'Aktif'),
('24.83.9901', 'Rian Saputra', 'rian.saputra@student.ac.id', 'Aktif'),
('24.83.9902', 'Siti Aminah', 'siti.aminah@student.ac.id', 'Aktif');

-- D. Input Entitas Data Buku Sampel (Relasi ke Kategori)
INSERT INTO buku (judul, penulis, penerbit, tahun_terbit, id_kategori) VALUES
('Building Modern Web Apps with Flask', 'Robert C. Martin', 'O Reilly Media', 2024, 1),
('Python Crash Course for Data Science', 'Eric Matthes', 'No Starch Press', 2025, 2),
('Laskar Pelangi', 'Andrea Hirata', 'Bentang Pustaka', 2005, 3),
('Introduction to Cyber Security', 'Clifford Stoll', 'Prentice Hall', 2023, 1);

-- E. Input Entitas Alur Sirkulasi Peminjaman & Denda Keterlambatan
INSERT INTO peminjaman (id_anggota, id_buku, tanggal_pinjam, tanggal_kembali, status, denda) VALUES
(1, 1, '2026-07-10', '2026-07-17', 'Kembali', 0),
(3, 3, '2026-06-01', '2026-06-08', 'Kembali', 15000),
(4, 4, '2026-07-01', '2026-07-08', 'Dipinjam', 5000);
