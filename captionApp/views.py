import os
import json
import cloudinary.uploader
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv
from openai import OpenAI
from .models import InstaPost, InstaPostImage

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("Missing OpenAI API Key! Please set OPENAI_API_KEY in your .env file.")

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)


def index(request):
    """Renders the main UI for the caption app."""
    return render(request, 'captionApp/index.html')


def get_uncaptioned_posts(request):
    """Fetches all Instagram posts without captions."""
    posts = InstaPost.objects.filter(caption__isnull=True)  # Fetch posts without captions
    data = [{"id": post.id, "images": [img.image.url for img in post.post_images.all()]} for post in posts]
    return JsonResponse({"success": True, "posts": data})


def upload_image_to_cloudinary(image_file):
    """Uploads image to Cloudinary and returns the URL"""
    result = cloudinary.uploader.upload(image_file)
    return result.get("secure_url")  # Return the secure image URL


@csrf_exempt
def upload_images(request):
    """Handles multiple image uploads, saves them to Cloudinary, and associates them with a post."""
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Only POST method allowed."}, status=405)

    if 'images' not in request.FILES:
        return JsonResponse({"success": False, "error": "No images uploaded."}, status=400)

    post = InstaPost.objects.create()  # Create a new post first
    uploaded_urls = []

    for image_file in request.FILES.getlist('images'):
        image_url = upload_image_to_cloudinary(image_file)
        InstaPostImage.objects.create(post=post, image=image_url)  # Save image record
        uploaded_urls.append(image_url)

    return JsonResponse({"success": True, "urls": uploaded_urls, "post_id": post.id})


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from openai import OpenAI
from .models import InstaPost

client = OpenAI()

@csrf_exempt
def generate_captions(request, post_id):
    """Generates Instagram captions based on color, texture, and material, avoiding professional terms."""
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Only POST method allowed."}, status=405)

    post = get_object_or_404(InstaPost, id=post_id)

    if not post.post_images.exists():
        return JsonResponse({"success": False, "error": "No images found for this post."}, status=400)

    messages = [
        {"role": "system", "content": (
            "You specialize in crafting quirky, straight-to-the-point Instagram captions for architectural images. "
            "Avoid professional architectural terminology, bombastic words, and any terms related to 'elegance'. "
            "Use engaging, relatable language that reflects the image's color, texture, and material. "
            "Captions should be short, catchy, and visually inspired. DO NOT USE EMOJIS! "
            "If multiple images are sent, they belong to the same project.")}
    ]

    for img in post.post_images.all():
        messages.append({
            "role": "user",
            "content": f"Describe the color, texture, and material of this image: {img.image.url}"
        })
    
    messages.append({"role": "user", "content": "Now, generate 4-5 short, catchy captions for this image based on its color, texture, and material. "
                                                    "No professional or design-related terms. No exaggerated words. No words related to 'elegance'. "
                                                    "**No exaggerated or overly fancy words.**"
                                                    "*No professional or design-related terms.**"
                                                    "Ignore any lines that specify image format, typeface, or logos."
                                                    "Captions should be fun, catchy, and true to the image. "
                                                    })
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            max_tokens=1000
        )

        captions = response.choices[0].message.content.strip().split("\n")
        captions = [cap.strip() for cap in captions if cap.strip()]  # Clean up any empty lines

        return JsonResponse({"success": True, "captions": captions})

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@csrf_exempt
def save_caption(request, post_id):
    """Saves the selected caption and deletes the temporary images from Cloudinary."""
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Only POST method allowed."}, status=405)

    post = get_object_or_404(InstaPost, id=post_id)
    data = json.loads(request.body)
    selected_caption = data.get("caption")

    if not selected_caption:
        return JsonResponse({"success": False, "error": "No caption provided"}, status=400)

    # Save caption
    post.caption = selected_caption
    post.save()

    # Delete all images from Cloudinary
    for image in post.post_images.all():
        cloudinary.uploader.destroy(image.image.public_id)  # Delete from Cloudinary
        image.delete()  # Remove from database

    return JsonResponse({"success": True, "message": "Caption saved, images deleted", "caption": post.caption})


@csrf_exempt
def chat_with_openai(request):
    """Handles OpenAI chat requests and returns a generated caption."""
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Only POST method allowed."}, status=405)

    try:
        data = json.loads(request.body)
        user_prompt = data.get("prompt", "").strip()

        if not user_prompt:
            return JsonResponse({"success": False, "error": "No prompt provided."}, status=400)

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": user_prompt}]
        )

        caption = response.choices[0].message.content.strip()

        return JsonResponse({"success": True, "caption": caption}, status=200)

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)
