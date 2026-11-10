from django.urls import path
from . import views

urlpatterns = [
    # =====================================================================
    # 1. HALAMAN UTAMA & PROFIL DESA
    # =====================================================================
    path('', views.beranda, name='beranda'),
    path('visi-misi/', views.visi_misi, name='visi_misi'),
    path('sejarah/', views.sejarah, name='sejarah'),
    path('wilayah/', views.wilayah, name='wilayah'),
    path('perangkat-desa/', views.perangkat_desa, name='perangkat_desa'),
    path('peta-lokasi/', views.peta_lokasi, name='peta_lokasi'),
    
    # =====================================================================
    # 2. BERITA, PENGUMUMAN & GALERI
    # =====================================================================
    path('berita/', views.berita_list, name='berita'),
    path('berita/<slug:slug>/', views.detail_berita, name='detail_berita'), 
    path('pengumuman/', views.pengumuman_list, name='pengumuman'),
    path('galeri/', views.galeri_list, name='galeri'),
    
    # =====================================================================
    # 3. LAYANAN PUBLIK & UMKM
    # =====================================================================
    path('layanan/', views.layanan_publik, name='layanan'),
    path('layanan/formulir/', views.formulir_pengajuan, name='formulir_pengajuan'),
    path('layanan/sukses/<str:id_tiket>/', views.sukses_pengajuan, name='sukses_pengajuan'),
    path('layanan/lacak/', views.lacak_tiket, name='lacak_tiket'),
    path('katalog-umkm/', views.katalog_umkm, name='katalog_umkm'),
    
    # =====================================================================
    # 4. DATA DESA & TRANSPARANSI
    # =====================================================================
    path('data-statistik/', views.data_statistik, name='data_statistik'),
    path('apbdes/', views.apbdes, name='apbdes'),

    # =====================================================================
    # 5. PENGADUAN, KRITIK & SARAN WARGA (PUBLIK)
    # =====================================================================
    path('pengaduan/', views.pengaduan_warga, name='pengaduan_warga'),
    
    # =====================================================================
    # 6. DASHBOARD & AUTENTIKASI
    # =====================================================================
    path('dashboard/', views.dashboard_admin, name='dashboard'),
    path('portal-masuk/', views.proses_login, name='portal_masuk'), 
    path('logout/', views.proses_logout, name='logout'), 

    # =====================================================================
    # 7. DASHBOARD KELOLA (READ)
    # =====================================================================
    path('dashboard/layanan-surat/', views.kelola_layanan_surat, name='kelola_layanan_surat'),
    path('dashboard/pengumuman/', views.kelola_pengumuman, name='kelola_pengumuman'),
    path('dashboard/berita/', views.kelola_berita, name='kelola_berita'),
    path('dashboard/galeri/', views.kelola_galeri, name='kelola_galeri'),
    path('dashboard/apbdes/', views.kelola_apbdes, name='kelola_apbdes'),
    path('dashboard/umkm/', views.kelola_umkm, name='kelola_umkm'),
    path('dashboard/dusun/', views.kelola_dusun, name='kelola_dusun'),
    path('dashboard/statistik/', views.kelola_statistik, name='kelola_statistik'),
    path('dashboard/aparatur/', views.kelola_aparatur, name='kelola_aparatur'),
    path('dashboard/visi-misi/', views.kelola_visi_misi, name='kelola_visi_misi'),
    path('dashboard/sejarah/', views.kelola_sejarah, name='kelola_sejarah'),
    path('dashboard/peta/', views.kelola_peta, name='kelola_peta'),

    # =====================================================================
    # 8. DASHBOARD KELOLA PENGAJUAN SURAT & KRITIK SARAN
    # =====================================================================
    path('dashboard/pengajuan-surat/', views.kelola_pengajuan_surat, name='kelola_pengajuan_surat'),
    path('dashboard/pengajuan-surat/ubah-status/<int:id>/', views.ubah_status_pengajuan, name='ubah_status_pengajuan'),
    path('dashboard/pengajuan-surat/hapus/<int:id>/', views.hapus_pengajuan_surat, name='hapus_pengajuan_surat'),
    
    # Kelola Kritik & Saran
    path('dashboard/kritik-saran/', views.kelola_kritik_saran, name='kelola_kritik_saran'),
    path('dashboard/kritik-saran/tandai/<int:id>/', views.tandai_sudah_dibaca, name='tandai_sudah_dibaca'),
    path('dashboard/kritik-saran/hapus/<int:id>/', views.hapus_pesan_warga, name='hapus_pesan_warga'),

    # =====================================================================
    # 9. DASHBOARD TAMBAH DATA (CREATE)
    # =====================================================================
    path('dashboard/layanan-surat/tambah/', views.tambah_layanan_surat, name='tambah_layanan_surat'),
    path('dashboard/pengumuman/tambah/', views.tambah_pengumuman, name='tambah_pengumuman'),
    path('dashboard/berita/tambah/', views.tambah_berita, name='tambah_berita'),
    path('dashboard/galeri/tambah/', views.tambah_galeri, name='tambah_galeri'),
    path('dashboard/apbdes/tambah/', views.tambah_apbdes, name='tambah_apbdes'),
    path('dashboard/umkm/tambah/', views.tambah_umkm, name='tambah_umkm'),
    path('dashboard/dusun/tambah/', views.tambah_dusun, name='tambah_dusun'),
    path('dashboard/aparatur/tambah/', views.tambah_aparatur, name='tambah_aparatur'),

    # =====================================================================
    # 10. DASHBOARD EDIT DATA (UPDATE)
    # =====================================================================
    path('dashboard/berita/edit/<int:id>/', views.edit_berita, name='edit_berita'),
    path('dashboard/umkm/edit/<int:id>/', views.edit_umkm, name='edit_umkm'),
    path('dashboard/pengumuman/edit/<int:id>/', views.edit_pengumuman, name='edit_pengumuman'),
    path('dashboard/aparatur/edit/<int:id>/', views.edit_aparatur, name='edit_aparatur'),
    path('dashboard/dusun/edit/<int:id>/', views.edit_dusun, name='edit_dusun'),
    # Tambahan rute edit layanan & APBDes
    path('dashboard/layanan-surat/edit/<int:id>/', views.edit_layanan_surat, name='edit_layanan_surat'),
    path('dashboard/apbdes/edit/<int:id>/', views.edit_apbdes, name='edit_apbdes'),

    # =====================================================================
    # 11. DASHBOARD HAPUS DATA (DELETE)
    # =====================================================================
    path('dashboard/berita/hapus/<int:id>/', views.hapus_berita, name='hapus_berita'),
    path('dashboard/umkm/hapus/<int:id>/', views.hapus_umkm, name='hapus_umkm'),
    path('dashboard/layanan-surat/hapus/<int:id>/', views.hapus_layanan_surat, name='hapus_layanan_surat'),
    path('dashboard/galeri/hapus/<int:id>/', views.hapus_galeri, name='hapus_galeri'),
    path('dashboard/apbdes/hapus/<int:id>/', views.hapus_apbdes, name='hapus_apbdes'),
    path('dashboard/pengumuman/hapus/<int:id>/', views.hapus_pengumuman, name='hapus_pengumuman'),
    path('dashboard/dusun/hapus/<int:id>/', views.hapus_dusun, name='hapus_dusun'),
    path('dashboard/aparatur/hapus/<int:id>/', views.hapus_aparatur, name='hapus_aparatur'),
    
    # Hapus Khusus (Sejarah & Peta)
    path('dashboard/sejarah/hapus/', views.hapus_sejarah, name='hapus_sejarah'),
    path('dashboard/peta/hapus/', views.hapus_peta, name='hapus_peta'),
    
    # Simpan Statistik
    path('dashboard/statistik/simpan/', views.simpan_statistik, name='simpan_statistik'),
]