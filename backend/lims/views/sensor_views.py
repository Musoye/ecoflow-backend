import requests
import google.generativeai as genai
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db.models import Avg, Sum
from ..models import Zone, Alert, CarbonLog
import PIL.Image

# Endpoint for the initial Crowd Prediction
CROWD_PREDICT_URL = "https://ecoflow-detector-490388308724.us-central1.run.app/predict"

# Configure Gemini
genai.configure(api_key=settings.GEMINI_API_KEY)

@api_view(['POST'])
@permission_classes([AllowAny])
def sensor_detect(request):
    """
    1. Uploads image to Crowd API -> Gets 'sahi_count'.
    2. Checks Overcrowding.
    3. If Safe -> Sends image DIRECTLY to Google Gemini API to get 'gemini_count'.
    4. Calculates Carbon Saved = sahi_count / gemini_count.
    """
    
    # 1. Validation
    zone_id = request.data.get('zone_id')
    camera_id = request.data.get('camera_id')
    image_file = request.FILES.get('file')

    if not zone_id or not image_file:
        return Response({"error": "Missing 'zone_id' or 'file'"}, status=400)

    zone = get_object_or_404(Zone, pk=zone_id)
    capacity = zone.capacity

    # ---------------------------------------------------------
    # STEP 1: Call Crowd Prediction API (SAHI)
    # ---------------------------------------------------------
    try:
        # Send file to your external Sahi service
        files = {'file': (image_file.name, image_file, image_file.content_type)}
        crowd_resp = requests.post(CROWD_PREDICT_URL, files=files)
        
        if crowd_resp.status_code != 200:
            return Response({"error": "Crowd Service failed", "details": crowd_resp.text}, status=502)
        
        crowd_data = crowd_resp.json()
        sahi_count = int(crowd_data.get('sahi_count', 0))

    except Exception as e:
        return Response({"error": "Connection Error (Crowd API)", "details": str(e)}, status=503)

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
        # Create Alert
        Alert.objects.create(
            heading=f"Overcrowding in {zone.name}",
            sub_heading=f"Detected {sahi_count}/{capacity} people. (Cam: {camera_id})",
            status=Alert.Status.OPEN
        )
        response_data["status"] = "DANGER"
        response_data["alert_created"] = True
        response_data["carbon_message"] = "Skipped Gemini calculation due to overcrowding."
        
    else:
        # ---------------------------------------------------------
        # STEP 3: Call Google Gemini API Directly
        # ---------------------------------------------------------
        try:
            # Prepare image for Gemini (Load from memory)
            img = PIL.Image.open(image_file)

            # Initialize Model (Gemini 1.5 Flash is fast and cheap for vision)
            model = genai.GenerativeModel('gemini-1.5-flash')

            # Prompt Logic
            prompt = (
                f"Count the number of people in this image. "
                f"The room capacity is {capacity}. "
                f"Return ONLY the integer number of people you see. Do not add text."
            )

            # Call Gemini
            gemini_response = model.generate_content([prompt, img])
            gemini_text = gemini_response.text.strip()
            
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

            # Save to Database
            CarbonLog.objects.create(zone=zone, saved_amount=final_ratio)

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
    """ Retrieves Carbon Saving statistics """
    zone_id = request.query_params.get('zone_id')

    if zone_id:
        logs = CarbonLog.objects.filter(zone_id=zone_id).order_by('-timestamp')
    else:
        logs = CarbonLog.objects.all().order_by('-timestamp')

    stats = logs.aggregate(
        total_saved=Sum('saved_amount'),
        avg_saved=Avg('saved_amount')
    )

    recent_logs = [
        {
            "zone": log.zone.name,
            "saved": log.saved_amount,
            "date": log.timestamp.strftime("%Y-%m-%d %H:%M")
        } 
        for log in logs[:10]
    ]

    return Response({
        "summary": {
            "total_saved_all_time": round(stats['total_saved'] or 0, 2),
            "average_per_detection": round(stats['avg_saved'] or 0, 2)
        },
        "recent_history": recent_logs
    })