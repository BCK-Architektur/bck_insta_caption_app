from django.db import models


class InstaPost(models.Model):
    images = models.JSONField(default=list, blank=True, null=True)  # ✅ Make it optional
    caption = models.CharField(max_length=500, blank=True, null=True)

    def __str__(self):
        return f"Post {self.id}"

class InstaPostImage(models.Model):
    post = models.ForeignKey(InstaPost, on_delete=models.CASCADE, related_name="post_images")
    image = models.ImageField(upload_to="insta_images/")

    def __str__(self):
        return f"Image for Post {self.post.id}"
