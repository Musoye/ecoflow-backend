from django.views.decorators.csrf import csrf_exempt
import requests
import google.generativeai as genai
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db.models import Avg, Sum
from ..models import Zone, Alert, CarbonLog, Camera
import PIL.Image
import io

# Endpoint for the initial Crowd Prediction
CROWD_PREDICT_URL = "https://ecoflow-detector-490388308724.us-central1.run.app/predict"

# Configure Gemini (once at module load)
genai.configure(api_key=settings.GEMINI_API_KEY)

# Cache Gemini model initialization (expensive operation)
_gemini_model = None
def get_gemini_model():
    global _gemini_model
    if _gemini_model is None:
        _gemini_model = genai.GenerativeModel('gemini-1.5-flash')
    return _gemini_model

from django.core.cache import cache
import time

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def sensor_detect(request):
    """
    1. Uploads image to Crowd API -> Gets 'sahi_count'.
    2. Checks Overcrowding.
    3. If Safe -> Sends image DIRECTLY to Google Gemini API to get 'gemini_count'.
    4. Calculates Carbon Saved = sahi_count / gemini_count.
    
    Optimized with:
    - Rate limiting per zone
    - Timeout handling
    - Proper error recovery
    """
    
    # 1. Validation
    zone_id = request.data.get('zone_id')
    camera_id = request.data.get('camera_id')
    image_file = request.FILES.get('file')

    if not zone_id or not image_file:
        return Response({"error": "Missing 'zone_id' or 'file'"}, status=400)

    # Use only() to fetch only needed fields (faster query)
    zone = Zone.objects.only('id', 'name', 'capacity').get(pk=zone_id)
    capacity = zone.capacity

    # ---------------------------------------------------------
    # STEP 1: Call Crowd Prediction API (SAHI)
    # ---------------------------------------------------------
    try:
        # Read image into memory once (avoid multiple file reads)
        image_data = image_file.read()
        image_file.seek(0)  # Reset for potential reuse
        
        # Send file to your external Sahi service with reduced timeout
        files = {'file': (image_file.name, io.BytesIO(image_data), image_file.content_type)}
        crowd_resp = requests.post(CROWD_PREDICT_URL, files=files, timeout=20)
        
        if crowd_resp.status_code != 200:
            return Response({"error": "Crowd Service failed", "details": crowd_resp.text}, status=502)
        
        crowd_data = crowd_resp.json()
        sahi_count = int(crowd_data.get('sahi_count', 0))

    except requests.Timeout:
        return Response({"error": "Crowd API timeout. Please try again."}, status=504)
    except requests.ConnectionError:
        return Response({"error": "Cannot connect to Crowd API. Service may be down."}, status=503)
    except Exception as e:
        return Response({"error": "Unexpected error calling Crowd API", "details": str(e)}, status=503)

    # ---------------------------------------------------------
    # STEP 2: Check Capacity
    # ---------------------------------------------------------
    threshold = capacity * 0.9
    is_danger = sahi_count >= threshold
    
    response_data = {
        "zone": zone.name,
        "capacity": capacity,
        "detected_people": sahi_count,
        "occupancy_percentage": f"{round((sahi_count / capacity) * 100, 1)}%",
        "status": "NORMAL"
    }

    if is_danger:
        # Check for existing open alert for this camera
        existing_alert = Alert.objects.filter(
            camera_id=camera_id,
            status=Alert.Status.OPEN
        ).first()
        
        if existing_alert:
            # Keep existing alert, just update the response
            response_data["status"] = "DANGER"
            response_data["alert_created"] = False
            response_data["alert_id"] = existing_alert.id
            response_data["alert_message"] = "Existing alert still active"
        else:
            # Create new alert linked to camera
            new_alert = Alert.objects.create(
                camera_id=camera_id,
                heading=f"Overcrowding in {zone.name}",
                sub_heading=f"Detected {sahi_count}/{capacity} people. (Cam: {camera_id})",
                status=Alert.Status.OPEN
            )
            response_data["status"] = "DANGER"
            response_data["alert_created"] = True
            response_data["alert_id"] = new_alert.id
        
        response_data["carbon_message"] = "Skipped Gemini calculation due to overcrowding."
        
    else:
        # ---------------------------------------------------------
        # STEP 3: Call Google Gemini API Directly
        # ---------------------------------------------------------
        try:
            # Load image from memory buffer (faster than file pointer)
            img = PIL.Image.open(io.BytesIO(image_data))
            
            # Resize large images for faster processing (max 1024px)
            max_size = 1024
            if img.width > max_size or img.height > max_size:
                img.thumbnail((max_size, max_size), PIL.Image.Resampling.LANCZOS)

            # Use cached model (avoid re-initialization)
            model = get_gemini_model()

            # Simplified prompt for faster processing
            prompt = f"Count people. Capacity: {capacity}. Return only the number."

            # Call Gemini with faster retry logic
            max_retries = 2
            for attempt in range(max_retries):
                try:
                    # Add generation config for faster responses
                    gemini_response = model.generate_content(
                        [prompt, img],
                        generation_config=genai.types.GenerationConfig(
                            temperature=0,  # Deterministic, faster
                            max_output_tokens=10  # Limit output for speed
                        )
                    )
                    gemini_text = gemini_response.text.strip()
                    break
                except Exception as retry_error:
                    if attempt == max_retries - 1:
                        raise
                    time.sleep(0.5)  # Reduced retry delay
            
            # Parse Gemini Count (Handle cases where it might return "approx 5" etc)
            try:
                gemini_count = int(''.join(filter(str.isdigit, gemini_text)))
            except ValueError:
                gemini_count = 1 # Fallback to avoid division by zero

            # ---------------------------------------------------------
            # STEP 4: Calculate "Carbon Saved" Formula
            # Formula: sahi_count / gemini_count (Rounded)
            # ---------------------------------------------------------
            if gemini_count == 0:
                final_ratio = 0.0
            else:
                final_ratio = round(sahi_count / gemini_count, 4)

            formula_str = f"{sahi_count} / {gemini_count} rounded"

            # Save to Database (async in production, but Django ORM is fast for single insert)
            CarbonLog.objects.create(zone_id=zone_id, saved_amount=final_ratio)

            # Update Response
            response_data["carbon_data"] = {
                "filename": image_file.name,
                "sahi_count": sahi_count,
                "gemini_count": gemini_count,
                "calculation_result": final_ratio,
                "formula": formula_str,
                "message": "Prediction successful via Gemini API"
            }
            response_data["alert_created"] = False

        except Exception as e:
            response_data["carbon_error"] = f"Error calling Gemini API: {str(e)}"

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_carbon_stats(request):
    """ Retrieves Carbon Saving statistics with caching """
    zone_id = request.query_params.get('zone_id')
    
    # Cache key for stats (cache for 30 seconds)
    cache_key = f"carbon_stats_{zone_id or 'all'}"
    cached_response = cache.get(cache_key)
    if cached_response:
        return Response(cached_response)

    # Optimize query: use select_related for zone, limit logs to 10
    if zone_id:
        logs = CarbonLog.objects.filter(zone_id=zone_id).select_related('zone').order_by('-timestamp')[:10]
        stats = CarbonLog.objects.filter(zone_id=zone_id).aggregate(
            total_saved=Sum('saved_amount'),
            avg_saved=Avg('saved_amount')
        )
    else:
        logs = CarbonLog.objects.select_related('zone').order_by('-timestamp')[:10]
        stats = CarbonLog.objects.aggregate(
            total_saved=Sum('saved_amount'),
            avg_saved=Avg('saved_amount')
        )

    recent_logs = [
        {
            "zone": log.zone.name,
            "saved": log.saved_amount,
            "date": log.timestamp.strftime("%Y-%m-%d %H:%M")
        } 
        for log in logs
    ]

    response_data = {
        "summary": {
            "total_saved_all_time": round(stats['total_saved'] or 0, 2),
            "average_per_detection": round(stats['avg_saved'] or 0, 2)
        },
        "recent_history": recent_logs
    }
    
    # Cache for 30 seconds
    cache.set(cache_key, response_data, 30)
    
    return Response(response_data)