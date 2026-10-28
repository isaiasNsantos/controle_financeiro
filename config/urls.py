from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView # <-- NOVO IMPORT
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('financas/', include('financas.urls')),
    
    # Rotas de Autenticação
    path('contas/login/', auth_views.LoginView.as_view(template_name='financas/login.html'), name='login'),
    path('contas/logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # Redirecionar a raiz (http://127.0.0.1:8000/) para o Dashboard
    path('', RedirectView.as_view(url='/financas/', permanent=False)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)