from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from api.utils import short_link_redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('s/<str:short_id>/', short_link_redirect, name='short-link-redirect'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
