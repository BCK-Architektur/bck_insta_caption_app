import openai
import os
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import InstaPost
import json

# Load API key from environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai.api_key = OPENAI_API_KEY

def index(request):
    """Renders the main UI for the caption app."""
    return render(request, 'captionApp/index.html')

def get_uncaptioned_posts(request):
    """Fetches all Instagram posts without captions."""
    posts = InstaPost.objects.filter(caption__isnull=True)  # Fetch posts without captions
    data = [{"id": post.id, "images": post.images} for post in posts]
    return JsonResponse({"posts": data})

def generate_captions(request, post_id):
    """Uses OpenAI to generate captions for a given InstaPost."""
    post = get_object_or_404(InstaPost, id=post_id)

    # Construct prompt for OpenAI
    prompt = f"Generate four engaging Instagram captions for these images: {post.images}. Keep them catchy, fun, and engaging for social media."

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",  # Use the latest GPT model
            messages=[
                {"role": "system", "content": "You are an AI that generates creative Instagram captions."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=100
        )

        # Extract captions from response
        captions = response["choices"][0]["message"]["content"].split("\n")

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"captions": captions})

@csrf_exempt
def save_caption(request, post_id):
    """Saves the selected caption for an Instagram post."""
    if request.method == "POST":
        post = get_object_or_404(InstaPost, id=post_id)
        data = json.loads(request.body)
        selected_caption = data.get("caption")

        if not selected_caption:
            return JsonResponse({"error": "No caption provided"}, status=400)

        post.caption = selected_caption
        post.save()

        return JsonResponse({"message": "Caption saved successfully", "caption": post.caption})
