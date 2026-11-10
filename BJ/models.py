from django.db import models
from django.utils.text import slugify
from django.utils import timezone
from django.contrib.auth.models import User
import uuid

# =========================================================================
# 1. MODEL KEPENDUDUKAN & STATISTIK DESA
# =========================================================================

class StatistikPenduduk(models.Model):
    """Menyimpan data agregat penduduk (Bisa diperbarui tiap semester)"""
    tahun = models.IntegerField(help_text="Contoh: 2026")
    semester = models.CharField(max_length=20, choices=[('I', 'Semester I'), ('II', 'Semester II')])
    total_penduduk = models.IntegerField(default=0)
    laki_laki = models.IntegerField(default=0)
    perempuan = models.IntegerField(default=0)
    total_kk = models.IntegerField(default=0)
    tanggal_update = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Statistik Penduduk"
        verbose_name_plural = "Statistik Penduduk"

    def __str__(self):
        return f"Data Penduduk {self.semester} - {self.tahun}"


class Dusun(models.Model):
    """Daftar 6 Dusun di Desa Beriri Jarak"""
    nama = models.CharField(max_length=100)
    kepala_dusun = models.CharField(max_length=100)
    luas_ha = models.DecimalField(max_digits=8, decimal_places=2, help_text="Luas dalam Hektar")
    jumlah_kk = models.IntegerField()
    jumlah_jiwa = models.IntegerField()
    deskripsi = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Dusun"
        verbose_name_plural = "Data Dusun"

    def __str__(self):
        return self.nama


class StatistikPekerjaan(models.Model):
    """Data mata pencaharian warga"""
    nama_pekerjaan = models.CharField(max_length=100)
    sektor = models.CharField(max_length=100, help_text="Contoh: Agraris, Perdagangan, Jasa", blank=True, null=True)
    jumlah = models.IntegerField()
    
    def __str__(self):
        return self.nama_pekerjaan


class StatistikAgama(models.Model):
    """Data sebaran agama per dusun"""
    agama = models.CharField(max_length=50)
    jumlah_penganut = models.IntegerField()
    
    def __str__(self):
        return self.agama


# =========================================================================
# 2. MODEL LAYANAN SURAT & ADMINISTRASI
# =========================================================================

class LayananSurat(models.Model):
    """Katalog jenis surat yang tersedia di desa"""
    nama_layanan = models.CharField(max_length=150)
    kategori = models.CharField(max_length=100, help_text="Kependudukan, Usaha, Pertanahan, dll")
    deskripsi = models.TextField()
    persyaratan = models.TextField(help_text="Gunakan enter untuk memisahkan poin")
    estimasi_waktu = models.CharField(max_length=50, help_text="Contoh: 15 Menit, 1 Hari")
    biaya = models.CharField(max_length=50, default="Rp 0 (Gratis)")
    
    class Meta:
        verbose_name = "Katalog Layanan Surat"
        verbose_name_plural = "Katalog Layanan Surat"

    def __str__(self):
        return self.nama_layanan


class PengajuanSurat(models.Model):
    """Data antrean permohonan surat warga"""
    STATUS_CHOICES = [
        ('menunggu', 'Menunggu Verifikasi'),
        ('diproses', 'Sedang Diproses'),
        ('selesai', 'Selesai & TTE'),
        ('ditolak', 'Ditolak / Berkas Kurang'),
    ]
    
    # ID Tiket Unik untuk pelacakan
    id_tiket = models.CharField(max_length=20, unique=True, blank=True, null=True, help_text="Cth: BJ-20260510-001")
    
    layanan = models.ForeignKey(LayananSurat, on_delete=models.SET_NULL, null=True, blank=True)
    nik_pemohon = models.CharField(max_length=16)
    nama_pemohon = models.CharField(max_length=100)
    no_whatsapp = models.CharField(max_length=15)
    dusun_asal = models.CharField(max_length=100)
    keterangan_tambahan = models.TextField(blank=True, null=True)
    file_ktp = models.FileField(upload_to='dokumen_surat/', blank=True, null=True)
    file_kk = models.FileField(upload_to='dokumen_surat/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='menunggu')
    tanggal_pengajuan = models.DateTimeField(auto_now_add=True)
    waktu_selesai = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = "Pengajuan Surat Warga"
        verbose_name_plural = "Data Pengajuan Surat"

    def save(self, *args, **kwargs):
        # Otomatis generate ID Tiket jika belum ada
        if not self.id_tiket:
            # Menggunakan timezone lokal untuk menghindari error aware vs naive
            today = timezone.localdate()
            date_str = today.strftime('%Y%m%d')
            
            # Menggunakan 3 digit UUID acak untuk menghindari bentrok/race condition
            # Format: BJ-20260510-A1B
            unique_code = str(uuid.uuid4().int)[:3]
            self.id_tiket = f"BJ-{date_str}-{unique_code}"
            
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nama_pemohon} - {self.layanan}"


# =========================================================================
# 3. MODEL BERITA, PENGUMUMAN & KEGIATAN
# =========================================================================

class Kategori(models.Model):
    """Kategori untuk berita (Pembangunan, Kesehatan, dll)"""
    nama = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    
    class Meta:
        verbose_name = "Kategori Berita"
        verbose_name_plural = "Kategori Berita"
        
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nama)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nama


class Berita(models.Model):
    """Publikasi berita & artikel desa"""
    judul = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    kategori = models.ForeignKey(Kategori, on_delete=models.SET_NULL, null=True)
    penulis = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    gambar = models.ImageField(upload_to='berita/', blank=True, null=True) 
    ringkasan = models.TextField(help_text="Teks singkat untuk kartu di beranda")
    isi_berita = models.TextField(help_text="Gunakan editor / HTML")
    dilihat = models.IntegerField(default=0, editable=False)
    status = models.CharField(max_length=20, choices=[('draft', 'Draft'), ('tayang', 'Tayang')], default='draft')
    tanggal_rilis = models.DateField()
    
    class Meta:
        ordering = ['-tanggal_rilis']
        verbose_name = "Berita & Artikel"
        verbose_name_plural = "Berita & Artikel"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.judul)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.judul


class Pengumuman(models.Model):
    """Pengumuman resmi desa (Bisa mendesak/Penting)"""
    judul = models.CharField(max_length=255)
    isi_pengumuman = models.TextField()
    tanggal_rilis = models.DateField()
    is_penting = models.BooleanField(default=False, help_text="Centang jika ini pengumuman mendesak")
    file_lampiran = models.FileField(upload_to='pengumuman/', blank=True, null=True)
    
    # TAMBAHAN BARU: Field Gambar
    gambar = models.ImageField(upload_to='pengumuman/', blank=True, null=True)
    
    def __str__(self):
        return self.judul


# =========================================================================
# 4. MODEL UMKM & EKONOMI DESA
# =========================================================================

class ProdukUMKM(models.Model):
    """Katalog produk UMKM warga desa"""
    nama_produk = models.CharField(max_length=150)
    nama_penjual = models.CharField(max_length=100)
    dusun = models.ForeignKey(Dusun, on_delete=models.SET_NULL, null=True)
    kategori = models.CharField(max_length=100, help_text="Makanan, Kriya, Kopi, dll")
    harga = models.IntegerField(help_text="Masukkan angka saja, contoh: 45000")
    satuan = models.CharField(max_length=20, default="pcs")
    deskripsi = models.TextField()
    gambar_produk = models.ImageField(upload_to='umkm/', blank=True, null=True)
    kontak_whatsapp = models.CharField(max_length=15)
    is_unggulan = models.BooleanField(default=False)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=5.0)

    class Meta:
        verbose_name = "Produk UMKM"
        verbose_name_plural = "Katalog UMKM"

    def __str__(self):
        return self.nama_produk


# =========================================================================
# 5. MODEL TRANSPARANSI APBDES
# =========================================================================

class APBDes(models.Model):
    """Laporan realisasi keuangan desa"""
    tahun_anggaran = models.IntegerField()
    tahap = models.CharField(max_length=50, help_text="Contoh: Tahap I, Tahap II")
    
    # Rincian Pendapatan
    pendapatan_asli = models.BigIntegerField(default=0, help_text="Pendapatan Asli Desa")
    pendapatan_transfer = models.BigIntegerField(default=0, help_text="Pendapatan Transfer")
    pendapatan_lain = models.BigIntegerField(default=0, help_text="Pendapatan Lain-lain")

    # Total Pendapatan
    total_pendapatan = models.BigIntegerField(default=0)
    realisasi_pendapatan = models.BigIntegerField(default=0)
    
    # Belanja
    total_belanja = models.BigIntegerField(default=0)
    realisasi_belanja = models.BigIntegerField(default=0)
    
    file_laporan_pdf = models.FileField(upload_to='apbdes/', blank=True, null=True)
    tanggal_update = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Laporan APBDes"
        verbose_name_plural = "Laporan APBDes"

    def __str__(self):
        return f"APBDes {self.tahun_anggaran} - {self.tahap}"


class RincianBelanja(models.Model):
    """Rincian Belanja per Bidang/Sub Bidang (Sesuai Baliho)"""
    apbdes = models.ForeignKey(APBDes, on_delete=models.CASCADE, related_name='rincian_belanja')
    uraian = models.CharField(max_length=255, help_text="Cth: Bidang Penyelenggaraan Pemerintahan Desa")
    anggaran = models.BigIntegerField(default=0, help_text="Anggaran (Rp)")
    realisasi = models.BigIntegerField(default=0, help_text="Realisasi (Rp)")
    
    class Meta:
        verbose_name = "Rincian Belanja"
        verbose_name_plural = "Rincian Belanja"

    def __str__(self):
        return f"{self.uraian} - Rp {self.anggaran}"


# =========================================================================
# 6. MODEL GALERI & MEDIA DESA
# =========================================================================

class Galeri(models.Model):
    """Kumpulan foto kegiatan desa"""
    judul_kegiatan = models.CharField(max_length=200)
    kategori = models.CharField(max_length=100, help_text="Pembangunan, Budaya, Posyandu, dll")
    lokasi_dusun = models.CharField(max_length=100)
    tanggal_kegiatan = models.DateField()
    gambar = models.ImageField(upload_to='galeri/')
    deskripsi = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-tanggal_kegiatan']
        verbose_name = "Galeri Foto"
        verbose_name_plural = "Galeri Foto"

    def __str__(self):
        return self.judul_kegiatan


# =========================================================================
# 7. MODEL PESAN WARGA (PENGADUAN/KRITIK & SARAN)
# =========================================================================

class PesanKontak(models.Model):
    """Formulir kontak atau pesan masuk dari warga"""
    nama = models.CharField(max_length=100)
    # DIUBAH: Dari EmailField menjadi CharField agar bisa menerima No. WhatsApp atau Email
    email = models.CharField(max_length=150, help_text="Bisa diisi Email atau No. WhatsApp") 
    subjek = models.CharField(max_length=200)
    pesan = models.TextField()
    sudah_dibaca = models.BooleanField(default=False)
    tanggal_kirim = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.subjek


# =========================================================================
# 8. MODEL APARATUR DESA
# =========================================================================

class AparaturDesa(models.Model):
    """Data perangkat desa, kaur, kasi, kadus"""
    nama = models.CharField(max_length=150)
    jabatan = models.CharField(max_length=100, help_text="Cth: Kepala Desa, Kasi Pelayanan")
    nipd = models.CharField(max_length=50, blank=True, null=True, help_text="NIPD / NIAP")
    foto = models.ImageField(upload_to='aparatur/', blank=True, null=True)
    periode = models.CharField(max_length=50, blank=True, null=True, help_text="Cth: 2019 - Sekarang")
    tupoksi = models.TextField(blank=True, null=True, help_text="Tugas Pokok dan Fungsi")
    kontak_wa = models.CharField(max_length=15, blank=True, null=True)
    meja_layanan = models.CharField(max_length=50, blank=True, null=True, help_text="Cth: Meja Layanan No. 01")
    
    KATEGORI_CHOICES = [
        ('pimpinan', 'Pimpinan (Kades/Sekdes)'),
        ('kaur', 'Kepala Urusan (Kaur)'),
        ('kasi', 'Kepala Seksi (Kasi)'),
        ('kadus', 'Kepala Dusun (Kadus)'),
    ]
    kategori = models.CharField(max_length=20, choices=KATEGORI_CHOICES, default='kaur')
    urutan = models.IntegerField(default=0, help_text="Urutan tampil (angka kecil di atas)")

    class Meta:
        ordering = ['urutan']
        verbose_name = "Aparatur Desa"
        verbose_name_plural = "Data Aparatur Desa"

    def __str__(self):
        return f"{self.nama} - {self.jabatan}"


# =========================================================================
# 9. MODEL SEJARAH DESA
# =========================================================================

class SejarahDesa(models.Model):
    """Menyimpan naskah sejarah desa"""
    bab_1_judul = models.CharField(max_length=200, default="Jejak Krama di Bawah Lindungan Rinjani")
    bab_1_isi = models.TextField(help_text="Gunakan enter untuk paragraf baru")
    
    kutipan_falsafah = models.TextField(default="Adat Sasak mengajarkan kita: Inaq gumi, amaq langit...")
    
    bab_2_judul = models.CharField(max_length=200, default="Penetapan Batas Melalui Flora Jarak Pagar")
    bab_2_isi = models.TextField(help_text="Gunakan enter untuk paragraf baru")
    
    bab_3_judul = models.CharField(max_length=200, default="Pemekaran Menuju Kemandirian Pemerintahan")
    bab_3_isi = models.TextField(help_text="Gunakan enter untuk paragraf baru")
    
    tanggal_update = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Naskah Sejarah Desa"
        verbose_name_plural = "Naskah Sejarah Desa"

    def __str__(self):
        return "Naskah Sejarah Desa Beriri Jarak"


# =========================================================================
# 10. MODEL VISI & MISI
# =========================================================================

class VisiMisi(models.Model):
    """Menyimpan Visi dan Misi Desa"""
    visi = models.TextField(help_text="Tuliskan Visi Utama Desa")
    misi = models.TextField(help_text="Gunakan enter untuk memisahkan poin misi")
    tanggal_update = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Visi & Misi"
        verbose_name_plural = "Visi & Misi"

    def __str__(self):
        return "Visi & Misi Desa"


# =========================================================================
# 11. MODEL PETA DESA
# =========================================================================

class PetaDesa(models.Model):
    """Menyimpan link embed Google Maps dan info peta"""
    judul = models.CharField(max_length=200, default="Peta Spasial Desa Beriri Jarak")
    deskripsi = models.TextField(blank=True, null=True)
    link_embed_maps = models.TextField(help_text="Masukkan URL src dari iframe Google Maps (Share > Embed a map)")
    
    # Info Tambahan
    luas_wilayah = models.CharField(max_length=50, default="485,6", help_text="Cth: 485,6")
    jumlah_dusun = models.CharField(max_length=50, default="6", help_text="Cth: 6")
    elevasi = models.CharField(max_length=50, default="450–750", help_text="Cth: 450–750")
    
    tanggal_update = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Konfigurasi Peta Desa"
        verbose_name_plural = "Konfigurasi Peta Desa"

    def __str__(self):
        return self.judul