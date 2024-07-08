

from django.contrib import admin
from django.urls import path, include, re_path
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('base.urls')),
    path('store/', include('store.urls')),
    path('management/', include('management.urls')),
    path('api/password_reset/', include('django_rest_passwordreset.urls', namespace='password_reset')),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
