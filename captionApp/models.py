from django.db import models
import cloudinary
import cloudinary.models

class InstaPost(models.Model):
    caption = models.CharField(max_length=500, blank=True, null=True)

    def __str__(self):
        return f"Post {self.id}"

class InstaPostImage(models.Model):
    post = models.ForeignKey(InstaPost, on_delete=models.CASCADE, related_name="post_images")
    image = cloudinary.models.CloudinaryField('image')

    def __str__(self):
        return f"Image for Post {self.post.id}"
