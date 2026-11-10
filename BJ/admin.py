from django.contrib import admin
from .models import (
    StatistikPenduduk, Dusun, StatistikPekerjaan, StatistikAgama,
    LayananSurat, PengajuanSurat,
    Kategori, Berita, Pengumuman,
    ProdukUMKM, APBDes, Galeri, PesanKontak
)

# --- Kustomisasi Judul Admin ---
admin.site.site_header = "Administrator SID Beriri Jarak"
admin.site.site_title = "SID Beriri Jarak"
admin.site.index_title = "Panel Kontrol Basis Data Desa"

# --- Kustomisasi Tampilan Tabel di Admin ---
@admin.register(Berita)
class BeritaAdmin(admin.ModelAdmin):
    list_display = ('judul', 'kategori', 'status', 'tanggal_rilis', 'dilihat')
    list_filter = ('status', 'kategori')
    search_fields = ('judul', 'isi_berita')
    prepopulated_fields = {'slug': ('judul',)}
    readonly_fields = ('dilihat',)

@admin.register(PengajuanSurat)
class PengajuanSuratAdmin(admin.ModelAdmin):
    list_display = ('nama_pemohon', 'layanan', 'dusun_asal', 'status', 'tanggal_pengajuan')
    list_filter = ('status', 'dusun_asal', 'layanan')
    search_fields = ('nama_pemohon', 'nik_pemohon')

@admin.register(ProdukUMKM)
class ProdukUMKMAdmin(admin.ModelAdmin):
    list_display = ('nama_produk', 'nama_penjual', 'harga', 'is_unggulan')
    list_filter = ('kategori', 'is_unggulan')

@admin.register(Galeri)
class GaleriAdmin(admin.ModelAdmin):
    list_display = ('judul_kegiatan', 'kategori', 'tanggal_kegiatan')

@admin.register(Pengumuman)
class PengumumanAdmin(admin.ModelAdmin):
    list_display = ('judul', 'tanggal_rilis', 'is_penting')

@admin.register(LayananSurat)
class LayananSuratAdmin(admin.ModelAdmin):
    list_display = ('nama_layanan', 'kategori', 'estimasi_waktu')

@admin.register(APBDes)
class APBDesAdmin(admin.ModelAdmin):
    list_display = ('tahun_anggaran', 'tahap', 'total_pendapatan', 'total_belanja')

# Daftarkan model lainnya secara otomatis
admin.site.register(StatistikPenduduk)
admin.site.register(Dusun)
admin.site.register(StatistikPekerjaan)
admin.site.register(StatistikAgama)
admin.site.register(Kategori)
admin.site.register(PesanKontak)