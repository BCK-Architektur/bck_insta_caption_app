from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("uncaptioned/", views.get_uncaptioned_posts, name="uncaptioned"),
    path("generate/<int:post_id>/", views.generate_captions, name="generate_captions"),
    path("save/<int:post_id>/", views.save_caption, name="save_caption"),
]
