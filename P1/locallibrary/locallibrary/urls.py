"""
URL configuration for locallibrary project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.conf import settings
from django.views.generic import RedirectView
from django.urls import include
from django.contrib import admin
from django.urls import path

urlpatterns = [
    path('admin/', admin.site.urls),
]


# Use include() to add paths from the catalog application

# Redirige cualquier URL que comience con
#   catalog/ a otro archivo: catalog/urls.py,
# donde se definirán las rutas específicas de la aplicación.
urlpatterns += [
    path('catalog/', include('catalog.urls')),
]


# Add URL maps to redirect the base URL to our application

# Queremos que cuando un usuario visite http://127.0.0.1:8000/, sea redirigido
# automáticamente a http://127.0.0.1:8000/catalog/. Para esto, usamos
# RedirectView.
urlpatterns += [
    path('', RedirectView.as_view(url='catalog/', permanent=True)),
]


# Use static() to add URL mapping to serve static files during development
# (only)

# Indica a Django dónde encontrar los
#   archivos estáticos (definidos en settings.py).
# Solo funciona en el entorno de desarrollo.
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


# Add Django site authentication urls (for login, logout, password management)
urlpatterns += [
    path('accounts/', include('django.contrib.auth.urls')),
]
