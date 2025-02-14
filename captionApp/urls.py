from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("uncaptioned/", views.get_uncaptioned_posts, name="uncaptioned"),
    path("generate/<int:post_id>/", views.generate_captions, name="generate_captions"),
    path("save/<int:post_id>/", views.save_caption, name="save_caption"),
    
    # OpenAI API endpoints
    path("api/openai/chat/", views.chat_with_openai, name="chat_with_openai"),
    path("api/openai/generate-caption/", views.generate_instagram_caption, name="generate_instagram_caption"),
]

# Serve media files in development mode
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
