from django.contrib import admin
from django.utils.html import format_html
from .models import InstaPost, InstaPostImage
from .forms import InstaPostImageForm

class InstaPostImageInline(admin.TabularInline):  
    """Allows adding multiple images inline in the InstaPost admin page."""
    model = InstaPostImage
    form = InstaPostImageForm  # ✅ Use the custom form
    extra = 1  
    fields = ("image", "preview")
    readonly_fields = ("preview",)

    def preview(self, obj):
        """Shows image previews in the inline section."""
        if obj.image:
            return format_html('<img src="{}" style="width:100px; height:auto; margin:5px;"/>', obj.image.url)
        return ""

class InstaPostAdmin(admin.ModelAdmin):
    """Custom admin for InstaPost."""
    list_display = ("id", "caption", "image_preview")
    inlines = [InstaPostImageInline]

    def save_model(self, request, obj, form, change):
        """Automatically update the images field based on uploaded images."""
        super().save_model(request, obj, form, change)
        obj.images = [img.image.url for img in obj.post_images.all()]  # ✅ Store all image URLs in JSONField
        obj.save()

    def image_preview(self, obj):
        """Display all images in the admin list view as thumbnails."""
        images = obj.post_images.all()
        if images:
            return format_html("".join([f'<img src="{img.image.url}" style="width:100px; height:auto; margin:5px;"/>' for img in images]))
        return "No Image"

    image_preview.allow_tags = True
    image_preview.short_description = "Preview"

admin.site.register(InstaPost, InstaPostAdmin)


