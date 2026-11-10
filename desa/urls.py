from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    # Admin bawaan Django (bisa diakses di /admin/)
    path("admin/", admin.site.urls),

    # Semua URL publik dan dashboard diarahkan ke aplikasi BJ
    path("", include("BJ.urls")),

    # Django CMS (jika Anda masih menggunakannya)
    path("cms/", include("cms.urls")), 
]

# Media dan static files
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)