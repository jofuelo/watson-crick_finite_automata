from django.contrib import admin
from django.urls import include, path
from django.contrib import admin

urlpatterns = [
    path('admin/', admin.site.urls),
    path('afwk/', include('afwk.urls'))
]
