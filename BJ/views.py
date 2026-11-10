import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils.text import slugify
from django.views.decorators.http import require_POST
from django.http import JsonResponse

from .models import (
    Berita, Kategori, Pengumuman, ProdukUMKM,
    LayananSurat, PengajuanSurat, Galeri,
    APBDes, RincianBelanja, StatistikPenduduk, Dusun, StatistikPekerjaan, StatistikAgama,
    AparaturDesa, VisiMisi, SejarahDesa, PetaDesa, PesanKontak
)

# =========================================================================
# 1. HALAMAN UTAMA & UMUM
# =========================================================================

def beranda(request):
    berita_terbaru = Berita.objects.filter(status='tayang').order_by('-tanggal_rilis')[:3]
    umkm_unggulan = ProdukUMKM.objects.filter(is_unggulan=True)[:4]
    if not umkm_unggulan:
        umkm_unggulan = ProdukUMKM.objects.all()[:4]
    pengumuman_penting = Pengumuman.objects.filter(is_penting=True).order_by('-tanggal_rilis')[:1]
    stat_penduduk = StatistikPenduduk.objects.order_by('-tahun', '-semester').first()

    context = {
        'berita_terbaru': berita_terbaru,
        'umkm_unggulan': umkm_unggulan,
        'pengumuman_penting': pengumuman_penting,
        'stat_penduduk': stat_penduduk,
        'total_umkm': ProdukUMKM.objects.count(),
    }
    return render(request, 'themes/beranda.html', context)


def visi_misi(request):
    data = VisiMisi.objects.first()
    return render(request, 'themes/visi_misi.html', {'data': data})


def sejarah(request):
    data_sejarah = SejarahDesa.objects.first()
    return render(request, 'themes/sejarah.html', {'data': data_sejarah})


def wilayah(request):
    daftar_dusun = Dusun.objects.all()
    data_peta = PetaDesa.objects.first()
    return render(request, 'themes/wilayah.html', {
        'daftar_dusun': daftar_dusun,
        'data_peta': data_peta,
    })


def perangkat_desa(request):
    pimpinan = AparaturDesa.objects.filter(kategori='pimpinan').order_by('urutan')
    kaur_kasi = AparaturDesa.objects.filter(kategori__in=['kaur', 'kasi']).order_by('urutan')

    context = {
        'pimpinan': pimpinan,
        'kaur_kasi': kaur_kasi,
    }
    return render(request, 'themes/Perangkat_desa.html', context)


def peta_lokasi(request):
    data_peta = PetaDesa.objects.first()
    return render(request, 'themes/peta_lokasi.html', {'data_peta': data_peta})


# =========================================================================
# 2. BERITA, PENGUMUMAN & GALERI
# =========================================================================

def berita_list(request):
    berita_list = Berita.objects.filter(status='tayang').order_by('-tanggal_rilis')
    kategori_list = Kategori.objects.all()
    kategori_aktif = request.GET.get('kategori')
    q = request.GET.get('q')

    if kategori_aktif:
        berita_list = berita_list.filter(kategori__slug=kategori_aktif)
    if q:
        berita_list = berita_list.filter(
            Q(judul__icontains=q) | Q(ringkasan__icontains=q)
        )

    paginator = Paginator(berita_list, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'berita_list': page_obj,
        'page_obj': page_obj,
        'kategori_list': kategori_list,
        'kategori_aktif': kategori_aktif,
        'q': q,
    }
    return render(request, 'themes/berita.html', context)


def detail_berita(request, slug):
    berita = get_object_or_404(Berita, slug=slug, status='tayang')
    
    # Tambah jumlah dilihat
    berita.dilihat += 1
    berita.save()

    berita_lain = Berita.objects.filter(
        status='tayang', kategori=berita.kategori
    ).exclude(id=berita.id).order_by('-tanggal_rilis')[:3]
    return render(request, 'themes/detail_berita.html', {
        'berita': berita,
        'berita_lain': berita_lain,
    })


def pengumuman_list(request):
    pengumuman_list = Pengumuman.objects.all().order_by('-tanggal_rilis')
    paginator = Paginator(pengumuman_list, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'themes/pengumuman.html', {'pengumuman_list': page_obj, 'page_obj': page_obj})


def galeri_list(request):
    galeri_list = Galeri.objects.all().order_by('-tanggal_kegiatan')
    paginator = Paginator(galeri_list, 12)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'themes/galeri.html', {'galeri_list': page_obj, 'page_obj': page_obj})


# =========================================================================
# 3. LAYANAN PUBLIK & UMKM
# =========================================================================

def layanan_publik(request):
    katalog_surat = LayananSurat.objects.all()
    return render(request, 'themes/Layanan.html', {'katalog_surat': katalog_surat})


def katalog_umkm(request):
    umkm_list = ProdukUMKM.objects.all().order_by('-is_unggulan', 'nama_produk')
    dusun_aktif = request.GET.get('dusun')
    q = request.GET.get('q')

    if dusun_aktif:
        umkm_list = umkm_list.filter(dusun__nama=dusun_aktif)
    if q:
        umkm_list = umkm_list.filter(
            Q(nama_produk__icontains=q) | Q(nama_penjual__icontains=q)
        )

    paginator = Paginator(umkm_list, 12)
    page_obj = paginator.get_page(request.GET.get('page'))

    context = {
        'umkm_list': page_obj,
        'page_obj': page_obj,
        'daftar_dusun': Dusun.objects.all(),
        'dusun_aktif': dusun_aktif,
        'q': q,
    }
    return render(request, 'themes/Katalog_umkm.html', context)


# =========================================================================
# 4. DATA DESA & TRANSPARANSI
# =========================================================================

def data_statistik(request):
    stat_terbaru = StatistikPenduduk.objects.order_by('-tahun', '-semester').first()
    data_dusun = Dusun.objects.all()
    pekerjaan = StatistikPekerjaan.objects.all().order_by('-jumlah')
    agama = StatistikAgama.objects.all().order_by('-jumlah_penganut')

    dusun_labels = [d.nama for d in data_dusun]
    dusun_data = [d.jumlah_jiwa for d in data_dusun]
    pekerjaan_labels = [p.nama_pekerjaan for p in pekerjaan]
    pekerjaan_data = [p.jumlah for p in pekerjaan]
    agama_labels = [a.agama for a in agama]
    agama_data = [a.jumlah_penganut for a in agama]

    context = {
        'stat_terbaru': stat_terbaru,
        'data_dusun': data_dusun,
        'pekerjaan': pekerjaan,
        'agama': agama,
        'dusun_labels_json': json.dumps(dusun_labels),
        'dusun_data_json': json.dumps(dusun_data),
        'pekerjaan_labels_json': json.dumps(pekerjaan_labels),
        'pekerjaan_data_json': json.dumps(pekerjaan_data),
        'agama_labels_json': json.dumps(agama_labels),
        'agama_data_json': json.dumps(agama_data),
    }
    return render(request, 'themes/data_statistik.html', context)


def apbdes(request):
    laporan_terbaru = APBDes.objects.order_by('-tahun_anggaran', 'tahap').first()
    riwayat_laporan = APBDes.objects.all().order_by('-tahun_anggaran', 'tahap')
    context = {'laporan_terbaru': laporan_terbaru, 'riwayat_laporan': riwayat_laporan}
    return render(request, 'themes/APBDes.html', context)


# =========================================================================
# 5. AUTENTIKASI & DASHBOARD ADMIN
# =========================================================================

def proses_login(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('identity')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f'Selamat datang, {user.username}!')
            return redirect('dashboard')
        else:
            return render(request, 'themes/portal_masuk.html',
                          {'error': 'Nama pengguna atau kata sandi salah!'})

    return render(request, 'themes/portal_masuk.html')


def proses_logout(request):
    logout(request)
    messages.info(request, 'Anda telah keluar.')
    return redirect('beranda')


@login_required(login_url='portal_masuk')
def dashboard_admin(request):
    antrean_surat = PengajuanSurat.objects.all().order_by('-tanggal_pengajuan')[:5]

    total_surat = PengajuanSurat.objects.count()
    surat_menunggu = PengajuanSurat.objects.filter(status__in=['menunggu', 'diproses']).count()
    surat_selesai = PengajuanSurat.objects.filter(status='selesai').count()
    
    apbdes_terbaru = APBDes.objects.order_by('-tahun_anggaran').first()

    total_umkm = ProdukUMKM.objects.count()
    total_berita = Berita.objects.filter(status='tayang').count()
    total_pengumuman = Pengumuman.objects.count()
    
    total_pesan_baru = PesanKontak.objects.filter(sudah_dibaca=False).count()

    status_stats = PengajuanSurat.objects.values('status').annotate(total=Count('id'))

    context = {
        'antrean_surat': antrean_surat,
        'total_surat': total_surat,
        'surat_menunggu': surat_menunggu,
        'surat_selesai': surat_selesai,
        'apbdes': apbdes_terbaru,
        'total_umkm': total_umkm,
        'total_berita': total_berita,
        'total_pengumuman': total_pengumuman,
        'total_pesan_baru': total_pesan_baru,
        'status_stats': status_stats,
    }
    return render(request, 'themes/admin/dashboard.html', context)


# =========================================================================
# 6. HALAMAN KELOLA (READ)
# =========================================================================

@login_required(login_url='portal_masuk')
def kelola_layanan_surat(request):
    return render(request, 'themes/admin/kelola_layanan_surat.html',
                  {'daftar_layanan': LayananSurat.objects.all()})


@login_required(login_url='portal_masuk')
def kelola_pengumuman(request):
    return render(request, 'themes/admin/kelola_pengumuman.html',
                  {'daftar_pengumuman': Pengumuman.objects.all().order_by('-tanggal_rilis')})


@login_required(login_url='portal_masuk')
def kelola_berita(request):
    return render(request, 'themes/admin/kelola_berita.html',
                  {'daftar_berita': Berita.objects.all().order_by('-tanggal_rilis')})


@login_required(login_url='portal_masuk')
def kelola_galeri(request):
    return render(request, 'themes/admin/kelola_galeri.html',
                  {'daftar_galeri': Galeri.objects.all().order_by('-tanggal_kegiatan')})


@login_required(login_url='portal_masuk')
def kelola_apbdes(request):
    return render(request, 'themes/admin/kelola_apbdes.html',
                  {'daftar_apbdes': APBDes.objects.all().order_by('-tahun_anggaran', 'tahap')})


@login_required(login_url='portal_masuk')
def kelola_umkm(request):
    return render(request, 'themes/admin/kelola_umkm.html',
                  {'daftar_umkm': ProdukUMKM.objects.all().order_by('-is_unggulan', 'nama_produk')})


@login_required(login_url='portal_masuk')
def kelola_dusun(request):
    return render(request, 'themes/admin/kelola_dusun.html',
                  {'daftar_dusun': Dusun.objects.all().order_by('nama')})


@login_required(login_url='portal_masuk')
def kelola_statistik(request):
    stat_terbaru = StatistikPenduduk.objects.order_by('-tahun', '-semester').first()
    context = {
        'stat_terbaru': stat_terbaru,
        'data_pekerjaan': StatistikPekerjaan.objects.all(),
        'data_agama': StatistikAgama.objects.all(),
        'riwayat_statistik': StatistikPenduduk.objects.all().order_by('-tahun', '-semester'),
    }
    return render(request, 'themes/admin/kelola_statistik.html', context)


@login_required(login_url='portal_masuk')
def kelola_aparatur(request):
    return render(request, 'themes/admin/kelola_aparatur.html',
                  {'daftar_aparatur': AparaturDesa.objects.all().order_by('urutan')})


@login_required(login_url='portal_masuk')
def kelola_visi_misi(request):
    data = VisiMisi.objects.first()
    if request.method == 'POST':
        if data:
            data.visi = request.POST.get('visi')
            data.misi = request.POST.get('misi')
            data.save()
        else:
            VisiMisi.objects.create(
                visi=request.POST.get('visi'),
                misi=request.POST.get('misi')
            )
        messages.success(request, 'Visi & Misi berhasil disimpan.')
        return redirect('kelola_visi_misi')
    return render(request, 'themes/admin/kelola_visi_misi.html', {'data': data})


@login_required(login_url='portal_masuk')
def kelola_sejarah(request):
    data_sejarah = SejarahDesa.objects.first()
    if request.method == 'POST':
        fields = ['bab_1_judul', 'bab_1_isi', 'kutipan_falsafah',
                  'bab_2_judul', 'bab_2_isi', 'bab_3_judul', 'bab_3_isi']
        if data_sejarah:
            for f in fields:
                setattr(data_sejarah, f, request.POST.get(f))
            data_sejarah.save()
        else:
            SejarahDesa.objects.create(**{f: request.POST.get(f) for f in fields})
        messages.success(request, 'Sejarah berhasil disimpan.')
        return redirect('kelola_sejarah')
    return render(request, 'themes/admin/kelola_sejarah.html', {'data': data_sejarah})


@login_required(login_url='portal_masuk')
@require_POST
def hapus_sejarah(request):
    data_sejarah = SejarahDesa.objects.first()
    if data_sejarah:
        data_sejarah.delete()
        messages.success(request, 'Sejarah berhasil dihapus.')
    return redirect('kelola_sejarah')


@login_required(login_url='portal_masuk')
def kelola_peta(request):
    data_peta = PetaDesa.objects.first()
    if request.method == 'POST':
        fields = ['judul', 'deskripsi', 'link_embed_maps', 'luas_wilayah', 'jumlah_dusun', 'elevasi']
        if data_peta:
            for f in fields:
                setattr(data_peta, f, request.POST.get(f))
            data_peta.save()
        else:
            PetaDesa.objects.create(**{f: request.POST.get(f) for f in fields})
        messages.success(request, 'Data peta berhasil disimpan.')
        return redirect('kelola_peta')
    return render(request, 'themes/admin/kelola_peta.html', {'data': data_peta})


@login_required(login_url='portal_masuk')
@require_POST
def hapus_peta(request):
    data_peta = PetaDesa.objects.first()
    if data_peta:
        data_peta.delete()
        messages.success(request, 'Data peta berhasil dihapus.')
    return redirect('kelola_peta')


# =========================================================================
# 7. FUNGSI TAMBAH (CREATE)
# =========================================================================

@login_required(login_url='portal_masuk')
def tambah_layanan_surat(request):
    if request.method == 'POST':
        LayananSurat.objects.create(
            nama_layanan=request.POST.get('nama_layanan'),
            kategori=request.POST.get('kategori'),
            deskripsi=request.POST.get('deskripsi'),
            persyaratan=request.POST.get('persyaratan'),
            estimasi_waktu=request.POST.get('estimasi_waktu'),
            biaya=request.POST.get('biaya')
        )
        messages.success(request, 'Layanan surat berhasil ditambahkan.')
        return redirect('kelola_layanan_surat')
    return render(request, 'themes/admin/tambah_layanan_surat.html')


@login_required(login_url='portal_masuk')
def tambah_pengumuman(request):
    if request.method == 'POST':
        is_penting = request.POST.get('is_penting') == 'on'
        Pengumuman.objects.create(
            judul=request.POST.get('judul'),
            isi_pengumuman=request.POST.get('isi_pengumuman'),
            tanggal_rilis=request.POST.get('tanggal_rilis'),
            is_penting=is_penting,
            file_lampiran=request.FILES.get('file_lampiran'),
            gambar=request.FILES.get('gambar')
        )
        messages.success(request, 'Pengumuman berhasil ditambahkan.')
        return redirect('kelola_pengumuman')
    return render(request, 'themes/admin/tambah_pengumuman.html')


@login_required(login_url='portal_masuk')
def tambah_berita(request):
    if not Kategori.objects.exists():
        for nama in ["Pembangunan", "Kegiatan Desa", "Pengumuman", "Pemberdayaan"]:
            Kategori.objects.create(nama=nama)

    if request.method == 'POST':
        judul = request.POST.get('judul')
        slug_base = slugify(judul)
        slug = slug_base
        counter = 1
        while Berita.objects.filter(slug=slug).exists():
            slug = f"{slug_base}-{counter}"
            counter += 1

        Berita.objects.create(
            judul=judul,
            slug=slug,
            kategori_id=request.POST.get('kategori'),
            penulis=request.user,
            ringkasan=request.POST.get('ringkasan'),
            isi_berita=request.POST.get('isi_berita'),
            status=request.POST.get('status'),
            tanggal_rilis=request.POST.get('tanggal_rilis'),
            gambar=request.FILES.get('gambar')
        )
        messages.success(request, 'Berita berhasil ditambahkan.')
        return redirect('kelola_berita')
    return render(request, 'themes/admin/tambah_berita.html',
                  {'kategori_list': Kategori.objects.all()})


@login_required(login_url='portal_masuk')
def tambah_galeri(request):
    if request.method == 'POST':
        Galeri.objects.create(
            judul_kegiatan=request.POST.get('judul_kegiatan'),
            kategori=request.POST.get('kategori'),
            lokasi_dusun=request.POST.get('lokasi_dusun'),
            tanggal_kegiatan=request.POST.get('tanggal_kegiatan'),
            gambar=request.FILES.get('gambar'),
            deskripsi=request.POST.get('deskripsi')
        )
        messages.success(request, 'Galeri berhasil ditambahkan.')
        return redirect('kelola_galeri')
    return render(request, 'themes/admin/tambah_galeri.html')


@login_required(login_url='portal_masuk')
def tambah_apbdes(request):
    if request.method == 'POST':
        # 1. Simpan Induk APBDes (Menggunakan int(float()) agar aman dari input desimal/kosong)
        apbdes = APBDes.objects.create(
            tahun_anggaran=int(float(request.POST.get('tahun_anggaran') or 0)),
            tahap=request.POST.get('tahap') or '',
            pendapatan_asli=int(float(request.POST.get('pendapatan_asli') or 0)),
            pendapatan_transfer=int(float(request.POST.get('pendapatan_transfer') or 0)),
            pendapatan_lain=int(float(request.POST.get('pendapatan_lain') or 0)),
            total_pendapatan=int(float(request.POST.get('total_pendapatan') or 0)),
            realisasi_pendapatan=int(float(request.POST.get('realisasi_pendapatan') or 0)),
            total_belanja=int(float(request.POST.get('total_belanja') or 0)),
            realisasi_belanja=int(float(request.POST.get('realisasi_belanja') or 0)),
        )
        
        # 2. Simpan Rincian Belanja
        uraian_list = request.POST.getlist('uraian_belanja[]')
        anggaran_list = request.POST.getlist('anggaran_belanja[]')
        realisasi_list = request.POST.getlist('realisasi_belanja[]')
        
        for u, a, r in zip(uraian_list, anggaran_list, realisasi_list):
            if u: # Jika uraian tidak kosong
                RincianBelanja.objects.create(
                    apbdes=apbdes,
                    uraian=u,
                    anggaran=int(float(a or 0)),
                    realisasi=int(float(r or 0))
                )

        messages.success(request, 'APBDes & Rincian Belanja berhasil ditambahkan.')
        return redirect('kelola_apbdes')
    return render(request, 'themes/admin/tambah_apbdes.html')


@login_required(login_url='portal_masuk')
def tambah_umkm(request):
    if request.method == 'POST':
        is_unggulan = request.POST.get('is_unggulan') == 'on'
        ProdukUMKM.objects.create(
            nama_produk=request.POST.get('nama_produk'),
            nama_penjual=request.POST.get('nama_penjual'),
            dusun_id=request.POST.get('dusun'),
            kategori=request.POST.get('kategori'),
            harga=request.POST.get('harga'),
            satuan=request.POST.get('satuan'),
            deskripsi=request.POST.get('deskripsi'),
            kontak_whatsapp=request.POST.get('kontak_whatsapp'),
            gambar_produk=request.FILES.get('gambar_produk'),
            is_unggulan=is_unggulan
        )
        messages.success(request, 'UMKM berhasil ditambahkan.')
        return redirect('kelola_umkm')
    return render(request, 'themes/admin/tambah_umkm.html',
                  {'daftar_dusun': Dusun.objects.all()})


@login_required(login_url='portal_masuk')
def tambah_dusun(request):
    if request.method == 'POST':
        Dusun.objects.create(
            nama=request.POST.get('nama'),
            kepala_dusun=request.POST.get('kepala_dusun'),
            luas_ha=request.POST.get('luas_ha'),
            jumlah_kk=request.POST.get('jumlah_kk'),
            jumlah_jiwa=request.POST.get('jumlah_jiwa'),
            deskripsi=request.POST.get('deskripsi')
        )
        messages.success(request, 'Dusun berhasil ditambahkan.')
        return redirect('kelola_dusun')
    return render(request, 'themes/admin/tambah_dusun.html')


@login_required(login_url='portal_masuk')
def tambah_aparatur(request):
    if request.method == 'POST':
        AparaturDesa.objects.create(
            nama=request.POST.get('nama'),
            jabatan=request.POST.get('jabatan'),
            nipd=request.POST.get('nipd'),
            foto=request.FILES.get('foto'),
            periode=request.POST.get('periode'),
            tupoksi=request.POST.get('tupoksi'),
            kontak_wa=request.POST.get('kontak_wa'),
            meja_layanan=request.POST.get('meja_layanan'),
            kategori=request.POST.get('kategori'),
            urutan=request.POST.get('urutan', 0)
        )
        messages.success(request, 'Aparatur berhasil ditambahkan.')
        return redirect('kelola_aparatur')
    return render(request, 'themes/admin/tambah_aparatur.html')


# =========================================================================
# 8. FUNGSI EDIT/UPDATE
# =========================================================================

@login_required(login_url='portal_masuk')
def edit_berita(request, id):
    berita = get_object_or_404(Berita, id=id)
    if request.method == 'POST':
        berita.judul = request.POST.get('judul')
        berita.kategori_id = request.POST.get('kategori')
        berita.ringkasan = request.POST.get('ringkasan')
        berita.isi_berita = request.POST.get('isi_berita')
        berita.status = request.POST.get('status')
        berita.tanggal_rilis = request.POST.get('tanggal_rilis')
        if request.FILES.get('gambar'):
            berita.gambar = request.FILES.get('gambar')
        berita.save()
        messages.success(request, 'Berita berhasil diperbarui.')
        return redirect('kelola_berita')
    return render(request, 'themes/admin/edit_berita.html', {
        'berita': berita,
        'kategori_list': Kategori.objects.all()
    })


@login_required(login_url='portal_masuk')
def edit_umkm(request, id):
    umkm = get_object_or_404(ProdukUMKM, id=id)
    if request.method == 'POST':
        umkm.nama_produk = request.POST.get('nama_produk')
        umkm.nama_penjual = request.POST.get('nama_penjual')
        umkm.dusun_id = request.POST.get('dusun')
        umkm.kategori = request.POST.get('kategori')
        umkm.harga = request.POST.get('harga')
        umkm.satuan = request.POST.get('satuan')
        umkm.deskripsi = request.POST.get('deskripsi')
        umkm.kontak_whatsapp = request.POST.get('kontak_whatsapp')
        umkm.is_unggulan = request.POST.get('is_unggulan') == 'on'
        if request.FILES.get('gambar_produk'):
            umkm.gambar_produk = request.FILES.get('gambar_produk')
        umkm.save()
        messages.success(request, 'UMKM berhasil diperbarui.')
        return redirect('kelola_umkm')
    return render(request, 'themes/admin/edit_umkm.html', {
        'umkm': umkm,
        'daftar_dusun': Dusun.objects.all()
    })


@login_required(login_url='portal_masuk')
def edit_pengumuman(request, id):
    pengumuman = get_object_or_404(Pengumuman, id=id)
    if request.method == 'POST':
        pengumuman.judul = request.POST.get('judul')
        pengumuman.isi_pengumuman = request.POST.get('isi_pengumuman')
        pengumuman.tanggal_rilis = request.POST.get('tanggal_rilis')
        pengumuman.is_penting = request.POST.get('is_penting') == 'on'
        if request.FILES.get('file_lampiran'):
            pengumuman.file_lampiran = request.FILES.get('file_lampiran')
        if request.FILES.get('gambar'):
            pengumuman.gambar = request.FILES.get('gambar')
        pengumuman.save()
        messages.success(request, 'Pengumuman berhasil diperbarui.')
        return redirect('kelola_pengumuman')
    return render(request, 'themes/admin/edit_pengumuman.html', {'pengumuman': pengumuman})


@login_required(login_url='portal_masuk')
def edit_aparatur(request, id):
    aparatur = get_object_or_404(AparaturDesa, id=id)
    if request.method == 'POST':
        aparatur.nama = request.POST.get('nama')
        aparatur.jabatan = request.POST.get('jabatan')
        aparatur.nipd = request.POST.get('nipd')
        aparatur.periode = request.POST.get('periode')
        aparatur.tupoksi = request.POST.get('tupoksi')
        aparatur.kontak_wa = request.POST.get('kontak_wa')
        aparatur.meja_layanan = request.POST.get('meja_layanan')
        aparatur.kategori = request.POST.get('kategori')
        aparatur.urutan = request.POST.get('urutan', 0)
        if request.FILES.get('foto'):
            aparatur.foto = request.FILES.get('foto')
        aparatur.save()
        messages.success(request, 'Aparatur berhasil diperbarui.')
        return redirect('kelola_aparatur')
    return render(request, 'themes/admin/edit_aparatur.html', {'aparatur': aparatur})


@login_required(login_url='portal_masuk')
def edit_dusun(request, id):
    dusun = get_object_or_404(Dusun, id=id)
    if request.method == 'POST':
        dusun.nama = request.POST.get('nama')
        dusun.kepala_dusun = request.POST.get('kepala_dusun')
        dusun.luas_ha = request.POST.get('luas_ha')
        dusun.jumlah_kk = request.POST.get('jumlah_kk')
        dusun.jumlah_jiwa = request.POST.get('jumlah_jiwa')
        dusun.deskripsi = request.POST.get('deskripsi')
        dusun.save()
        messages.success(request, 'Dusun berhasil diperbarui.')
        return redirect('kelola_dusun')
    return render(request, 'themes/admin/edit_dusun.html', {'dusun': dusun})


@login_required(login_url='portal_masuk')
def edit_layanan_surat(request, id):
    layanan = get_object_or_404(LayananSurat, id=id)
    if request.method == 'POST':
        layanan.nama_layanan = request.POST.get('nama_layanan')
        layanan.kategori = request.POST.get('kategori')
        layanan.deskripsi = request.POST.get('deskripsi')
        layanan.persyaratan = request.POST.get('persyaratan')
        layanan.estimasi_waktu = request.POST.get('estimasi_waktu')
        layanan.biaya = request.POST.get('biaya')
        layanan.save()
        messages.success(request, 'Layanan surat berhasil diperbarui.')
        return redirect('kelola_layanan_surat')
    return render(request, 'themes/admin/edit_layanan_surat.html', {'layanan': layanan})


@login_required(login_url='portal_masuk')
def edit_apbdes(request, id):
    apbdes = get_object_or_404(APBDes, id=id)
    if request.method == 'POST':
        apbdes.tahun_anggaran = int(float(request.POST.get('tahun_anggaran') or 0))
        apbdes.tahap = request.POST.get('tahap') or ''
        
        # Update rincian pendapatan
        apbdes.pendapatan_asli = int(float(request.POST.get('pendapatan_asli') or 0))
        apbdes.pendapatan_transfer = int(float(request.POST.get('pendapatan_transfer') or 0))
        apbdes.pendapatan_lain = int(float(request.POST.get('pendapatan_lain') or 0))
        
        apbdes.total_pendapatan = int(float(request.POST.get('total_pendapatan') or 0))
        apbdes.realisasi_pendapatan = int(float(request.POST.get('realisasi_pendapatan') or 0))
        apbdes.total_belanja = int(float(request.POST.get('total_belanja') or 0))
        apbdes.realisasi_belanja = int(float(request.POST.get('realisasi_belanja') or 0))
        apbdes.save()

        # Hapus rincian belanja lama, ganti dengan yang baru
        apbdes.rincian_belanja.all().delete()
        
        uraian_list = request.POST.getlist('uraian_belanja[]')
        anggaran_list = request.POST.getlist('anggaran_belanja[]')
        realisasi_list = request.POST.getlist('realisasi_belanja[]')
        
        for u, a, r in zip(uraian_list, anggaran_list, realisasi_list):
            if u:
                RincianBelanja.objects.create(
                    apbdes=apbdes,
                    uraian=u,
                    anggaran=int(float(a or 0)),
                    realisasi=int(float(r or 0))
                )

        messages.success(request, 'APBDes berhasil diperbarui.')
        return redirect('kelola_apbdes')
    return render(request, 'themes/admin/edit_apbdes.html', {'apbdes': apbdes})


# =========================================================================
# 9. FUNGSI HAPUS (dengan require_POST untuk keamanan)
# =========================================================================

@login_required(login_url='portal_masuk')
@require_POST
def hapus_layanan_surat(request, id):
    get_object_or_404(LayananSurat, id=id).delete()
    messages.success(request, 'Layanan surat berhasil dihapus.')
    return redirect('kelola_layanan_surat')


@login_required(login_url='portal_masuk')
@require_POST
def hapus_pengumuman(request, id):
    get_object_or_404(Pengumuman, id=id).delete()
    messages.success(request, 'Pengumuman berhasil dihapus.')
    return redirect('kelola_pengumuman')


@login_required(login_url='portal_masuk')
@require_POST
def hapus_berita(request, id):
    get_object_or_404(Berita, id=id).delete()
    messages.success(request, 'Berita berhasil dihapus.')
    return redirect('kelola_berita')


@login_required(login_url='portal_masuk')
@require_POST
def hapus_galeri(request, id):
    get_object_or_404(Galeri, id=id).delete()
    messages.success(request, 'Galeri berhasil dihapus.')
    return redirect('kelola_galeri')


@login_required(login_url='portal_masuk')
@require_POST
def hapus_apbdes(request, id):
    get_object_or_404(APBDes, id=id).delete()
    messages.success(request, 'APBDes berhasil dihapus.')
    return redirect('kelola_apbdes')


@login_required(login_url='portal_masuk')
@require_POST
def hapus_umkm(request, id):
    get_object_or_404(ProdukUMKM, id=id).delete()
    messages.success(request, 'UMKM berhasil dihapus.')
    return redirect('kelola_umkm')


@login_required(login_url='portal_masuk')
@require_POST
def hapus_dusun(request, id):
    get_object_or_404(Dusun, id=id).delete()
    messages.success(request, 'Dusun berhasil dihapus.')
    return redirect('kelola_dusun')


@login_required(login_url='portal_masuk')
@require_POST
def hapus_aparatur(request, id):
    get_object_or_404(AparaturDesa, id=id).delete()
    messages.success(request, 'Aparatur berhasil dihapus.')
    return redirect('kelola_aparatur')


# =========================================================================
# 10. STATISTIK PENDUDUK & EKONOMI
# =========================================================================

@login_required(login_url='portal_masuk')
@require_POST
def simpan_statistik(request):
    tahun = request.POST.get('tahun')
    semester = request.POST.get('semester')

    stat, created = StatistikPenduduk.objects.update_or_create(
        tahun=tahun, semester=semester,
        defaults={
            'total_penduduk': request.POST.get('total_penduduk'),
            'laki_laki': request.POST.get('laki_laki'),
            'perempuan': request.POST.get('perempuan'),
            'total_kk': request.POST.get('total_kk'),
        }
    )

    # Update pekerjaan (tanpa hapus semua jika tidak perlu)
    StatistikPekerjaan.objects.all().delete()
    for name, jumlah in zip(
        request.POST.getlist('nama_pekerjaan[]'),
        request.POST.getlist('jumlah_pekerjaan[]')
    ):
        if name and jumlah:
            StatistikPekerjaan.objects.create(nama_pekerjaan=name, jumlah=jumlah)

    # Update agama
    StatistikAgama.objects.all().delete()
    for name, jumlah in zip(
        request.POST.getlist('nama_agama[]'),
        request.POST.getlist('jumlah_agama[]')
    ):
        if name and jumlah:
            StatistikAgama.objects.create(agama=name, jumlah_penganut=jumlah)

    messages.success(request, 'Statistik berhasil disimpan.')
    return redirect('kelola_statistik')


# =========================================================================
# 11. PENGAJUAN SURAT & LACAK TIKET (PUBLIK)
# =========================================================================

def formulir_pengajuan(request):
    if request.method == 'POST':
        # 1. Ambil jenis surat yang diketik manual oleh warga
        jenis_surat_manual = request.POST.get('jenis_surat_manual')
        
        if not jenis_surat_manual:
            messages.error(request, 'Jenis surat wajib diisi.')
            return render(request, 'themes/formulir_pengajuan.html')

        # 2. Ambil keterangan tambahan
        keterangan = request.POST.get('keterangan_tambahan') or ''

        # 3. Gabungkan jenis surat manual ke dalam keterangan tambahan
        keterangan_lengkap = f"Jenis Surat: {jenis_surat_manual}\n{('Catatan Tambahan: ' + keterangan) if keterangan else ''}"

        # 4. Buat pengajuan baru
        pengajuan = PengajuanSurat.objects.create(
            layanan=None, # Dikosongkan karena input manual
            nik_pemohon=request.POST.get('nik_pemohon'),
            nama_pemohon=request.POST.get('nama_pemohon'),
            no_whatsapp=request.POST.get('no_whatsapp'),
            dusun_asal=request.POST.get('dusun_asal'),
            keterangan_tambahan=keterangan_lengkap,
            file_ktp=request.FILES.get('file_ktp'),
            file_kk=request.FILES.get('file_kk'),
        )
        
        return redirect('sukses_pengajuan', id_tiket=pengajuan.id_tiket)

    return render(request, 'themes/formulir_pengajuan.html')


def sukses_pengajuan(request, id_tiket):
    pengajuan = get_object_or_404(PengajuanSurat, id_tiket=id_tiket)
    return render(request, 'themes/sukses_pengajuan.html', {'pengajuan': pengajuan})


def lacak_tiket(request):
    pengajuan = None
    error = None
    if request.method == 'POST':
        id_tiket = request.POST.get('id_tiket', '').strip()
        if id_tiket:
            pengajuan = PengajuanSurat.objects.filter(id_tiket__iexact=id_tiket).first()
            if not pengajuan:
                error = "Tiket dengan ID tersebut tidak ditemukan. Pastikan ID Tiket benar."
        else:
            error = "Silakan masukkan ID Tiket."

    return render(request, 'themes/lacak_tiket.html', {
        'pengajuan': pengajuan,
        'error': error
    })


# =========================================================================
# 12. KELOLA PENGAJUAN SURAT (ADMIN)
# =========================================================================

@login_required(login_url='portal_masuk')
def kelola_pengajuan_surat(request):
    daftar_pengajuan = PengajuanSurat.objects.all().order_by('-tanggal_pengajuan')

    status_filter = request.GET.get('status')
    if status_filter:
        daftar_pengajuan = daftar_pengajuan.filter(status=status_filter)

    q = request.GET.get('q')
    if q:
        daftar_pengajuan = daftar_pengajuan.filter(
            Q(id_tiket__icontains=q) |
            Q(nama_pemohon__icontains=q) |
            Q(nik_pemohon__icontains=q)
        )

    paginator = Paginator(daftar_pengajuan, 20)
    page_obj = paginator.get_page(request.GET.get('page'))

    context = {
        'daftar_pengajuan': page_obj,
        'page_obj': page_obj,
        'status_filter': status_filter,
        'q': q,
    }
    return render(request, 'themes/admin/kelola_pengajuan_surat.html', context)


@login_required(login_url='portal_masuk')
def ubah_status_pengajuan(request, id):
    pengajuan = get_object_or_404(PengajuanSurat, id=id)
    status_choices = [s[0] for s in PengajuanSurat.STATUS_CHOICES] \
        if hasattr(PengajuanSurat, 'STATUS_CHOICES') else ['menunggu', 'diproses', 'selesai', 'ditolak']

    if request.method == 'POST':
        status_baru = request.POST.get('status')
        catatan = request.POST.get('catatan_admin', '')

        if status_baru not in status_choices:
            messages.error(request, f'Status "{status_baru}" tidak valid.')
            return render(request, 'themes/admin/ubah_status_pengajuan.html', {
                'pengajuan': pengajuan,
                'status_choices': status_choices
            })

        pengajuan.status = status_baru
        if hasattr(pengajuan, 'catatan_admin') and catatan:
            pengajuan.catatan_admin = catatan
        pengajuan.save()

        # Baris messages.success DIHAPUS agar notifikasi tidak muncul
        return redirect('kelola_pengajuan_surat')

    return render(request, 'themes/admin/ubah_status_pengajuan.html', {
        'pengajuan': pengajuan,
        'status_choices': status_choices
    })


@login_required(login_url='portal_masuk')
@require_POST
def hapus_pengajuan_surat(request, id):
    pengajuan = get_object_or_404(PengajuanSurat, id=id)
    tiket = pengajuan.id_tiket
    pengajuan.delete()
    messages.success(request, f'Pengajuan tiket {tiket} berhasil dihapus.')
    return redirect('kelola_pengajuan_surat')


# =========================================================================
# 13. API ENDPOINT (Opsional - untuk AJAX)
# =========================================================================

@login_required(login_url='portal_masuk')
def api_cek_status_tiket(request, id_tiket):
    """Endpoint AJAX untuk cek status tiket tanpa reload."""
    pengajuan = PengajuanSurat.objects.filter(id_tiket__iexact=id_tiket).first()
    if not pengajuan:
        return JsonResponse({'success': False, 'message': 'Tiket tidak ditemukan'}, status=404)

    # Antisipasi jika layanan bernilai None karena input manual
    nama_layanan = pengajuan.layanan.nama_layanan if pengajuan.layanan else "Layanan Input Manual"

    return JsonResponse({
        'success': True,
        'data': {
            'id_tiket': pengajuan.id_tiket,
            'nama_pemohon': pengajuan.nama_pemohon,
            'status': pengajuan.status,
            'layanan': nama_layanan,
            'tanggal_pengajuan': pengajuan.tanggal_pengajuan.strftime('%d %B %Y'),
        }
    })


# =========================================================================
# 14. PENGADUAN, KRITIK & SARAN (PUBLIK)
# =========================================================================

def pengaduan_warga(request):
    if request.method == 'POST':
        # Tangkap data dari form
        nama = request.POST.get('nama') or 'Anonim'
        email_atau_wa = request.POST.get('email')
        subjek = request.POST.get('subjek')
        pesan = request.POST.get('pesan')

        # Simpan ke database
        PesanKontak.objects.create(
            nama=nama,
            email=email_atau_wa,
            subjek=subjek,
            pesan=pesan
        )

        messages.success(request, 'Terima kasih! Pengaduan/Kritik/Saran Anda telah berhasil dikirim dan akan segera ditindaklanjuti.')
        
        # UBAH BAGIAN INI: Agar setelah submit, warga kembali ke halaman pengumuman
        return redirect('pengumuman') 

    # Jika bukan POST, arahkan juga ke halaman pengumuman
    return redirect('pengumuman')


# =========================================================================
# 15. KELOLA KRITIK & SARAN (ADMIN)
# =========================================================================

@login_required(login_url='portal_masuk')
def kelola_kritik_saran(request):
    # Ambil semua pesan, urutkan dari yang terbaru
    daftar_pesan = PesanKontak.objects.all().order_by('-tanggal_kirim')
    
    # Filter berdasarkan status sudah dibaca atau belum
    status_filter = request.GET.get('status')
    if status_filter == 'belum':
        daftar_pesan = daftar_pesan.filter(sudah_dibaca=False)
    elif status_filter == 'sudah':
        daftar_pesan = daftar_pesan.filter(sudah_dibaca=True)
        
    # Fitur Pencarian
    q = request.GET.get('q')
    if q:
        daftar_pesan = daftar_pesan.filter(
            Q(nama__icontains=q) | 
            Q(subjek__icontains=q) | 
            Q(pesan__icontains=q)
        )

    # Pagination
    paginator = Paginator(daftar_pesan, 15)
    page_obj = paginator.get_page(request.GET.get('page'))

    context = {
        'daftar_pesan': page_obj,
        'page_obj': page_obj,
        'status_filter': status_filter,
        'q': q,
        'total_belum_dibaca': PesanKontak.objects.filter(sudah_dibaca=False).count()
    }
    return render(request, 'themes/admin/kelola_kritik_saran.html', context)


@login_required(login_url='portal_masuk')
@require_POST
def tandai_sudah_dibaca(request, id):
    pesan = get_object_or_404(PesanKontak, id=id)
    pesan.sudah_dibaca = not pesan.sudah_dibaca # Toggle status
    pesan.save()
    status = "sudah dibaca" if pesan.sudah_dibaca else "belum dibaca"
    messages.success(request, f'Pesan berhasil ditandai sebagai {status}.')
    return redirect('kelola_kritik_saran')


@login_required(login_url='portal_masuk')
@require_POST
def hapus_pesan_warga(request, id):
    pesan = get_object_or_404(PesanKontak, id=id)
    pesan.delete()
    messages.success(request, 'Pesan/Kritik warga berhasil dihapus.')
    return redirect('kelola_kritik_saran')