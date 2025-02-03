from django.urls import path
from . import views
from .views import upload_image,generate_pdf
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='home'),
    path('create-room/', views.create_room, name='create_room'),
    path('<str:room_name>/', views.room, name='room'),
    
    path('generate_pdf/<int:chatroom_id>/', generate_pdf, name='generate_pdf'),
   
    path('upload_image/', upload_image, name='upload_image'),
    
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)