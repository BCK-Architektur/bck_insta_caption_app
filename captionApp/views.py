import os
import json
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv
from openai import OpenAI
from .models import InstaPost

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
    data = [{"id": post.id, "images": post.images} for post in posts]
    return JsonResponse({"success": True, "posts": data})


@csrf_exempt
def generate_captions(request, post_id):
    """Generates Instagram captions using OpenAI for a given InstaPost."""
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Only POST method allowed."}, status=405)

    post = get_object_or_404(InstaPost, id=post_id)
    prompt = f"Generate four engaging Instagram captions for these images: {post.images}. Keep them catchy, fun, and engaging for social media."

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "system", "content": "You are an AI that generates creative Instagram captions."},
                      {"role": "user", "content": prompt}],
            max_tokens=100
        )

        captions = response.choices[0].message.content.split("\n")

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)

    return JsonResponse({"success": True, "captions": captions})


@csrf_exempt
def save_caption(request, post_id):
    """Saves the selected caption for an Instagram post."""
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Only POST method allowed."}, status=405)

    post = get_object_or_404(InstaPost, id=post_id)
    data = json.loads(request.body)
    selected_caption = data.get("caption")

    if not selected_caption:
        return JsonResponse({"success": False, "error": "No caption provided"}, status=400)

    post.caption = selected_caption
    post.save()

    return JsonResponse({"success": True, "message": "Caption saved successfully", "caption": post.caption})


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


@csrf_exempt
def generate_instagram_caption(request):
    """Generates an Instagram caption based on a user-provided description."""
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Only POST method allowed."}, status=405)

    try:
        data = json.loads(request.body)
        image_description = data.get("description", "").strip()

        if not image_description:
            return JsonResponse({"success": False, "error": "No description provided."}, status=400)

        prompt = f"Generate an Instagram caption for a post about: {image_description}"
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )

        caption = response.choices[0].message.content.strip()

        return JsonResponse({"success": True, "caption": caption}, status=200)

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)
