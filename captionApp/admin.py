from django.contrib import admin
from django.utils.html import format_html
from .models import InstaPost, InstaPostImage

class InstaPostImageInline(admin.TabularInline):  
    """Allows adding multiple images inline in the InstaPost admin page."""
    model = InstaPostImage
    extra = 1  # Number of empty image fields to show by default
    fields = ("image", "preview")

    readonly_fields = ("preview",)

    def preview(self, obj):
        """Shows image preview in the admin panel."""
        if obj.image:
            return format_html('<img src="{}" style="width:100px; height:auto;"/>', obj.image.url)
        return ""

class InstaPostAdmin(admin.ModelAdmin):
    """Custom admin for InstaPost."""
    list_display = ("id", "caption", "image_preview")
    inlines = [InstaPostImageInline]

    def image_preview(self, obj):
        """Display first image preview in the list view."""
        first_image = obj.post_images.first()
        if first_image:
            return format_html('<img src="{}" style="width:100px; height:auto;"/>', first_image.image.url)
        return "No Image"

    image_preview.short_description = "Preview"

admin.site.register(InstaPost, InstaPostAdmin)
admin.site.register(InstaPostImage)  # Register the Image model
