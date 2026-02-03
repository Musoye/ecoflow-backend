# Cloud Run Performance Optimizations

## Issues Identified

### 1. **500 Errors - Root Causes**
- Database connection pool exhaustion (only 1 worker, 8 threads)
- Gemini API rate limiting under concurrent load  
- File handling issues (PIL.Image without file pointer reset)
- No retry logic for external API calls
- Missing timeouts on HTTP requests

### 2. **429 Errors (Too Many Requests)**
- No rate limiting on sensor endpoints
- Multiple concurrent requests to same zone
- External API overwhelm

### 3. **401 Errors**
- Authentication required for `/alerts/?status=OPEN`
- Missing JWT token in requests

## Optimizations Implemented

### Database Layer

**PostgreSQL Configuration:**
```bash
# Increased max connections
max_connections = 100  # Up from default 15
```

**Django Settings:**
```python
DATABASES = {
    'default': {
        'CONN_MAX_AGE': 60,  # Persistent connections for 60 seconds
        'CONN_HEALTH_CHECKS': True,  # Auto-reconnect on stale connections
        'OPTIONS': {
            'connect_timeout': 10,
            'options': '-c statement_timeout=30000',  # 30 second query timeout
        },
    }
}
```

### Application Layer

**Gunicorn Configuration:**
- **Workers**: 2 (up from 1) - Better CPU utilization
- **Threads**: 4 per worker (down from 8) - Better memory management
- **Worker Class**: `gthread` - Optimized for I/O-bound tasks
- **Worker Temp Dir**: `/dev/shm` - In-memory tmp for faster performance
- **Max Requests**: 1000 with 100 jitter - Prevents memory leaks

**Configuration:**
```bash
gunicorn --bind 0.0.0.0:$PORT \
    --workers 2 \
    --threads 4 \
    --worker-class gthread \
    --worker-tmp-dir /dev/shm \
    --timeout 300 \
    --max-requests 1000 \
    --max-requests-jitter 100
```

### Code Optimizations

**1. Rate Limiting (sensor_detect endpoint):**
```python
# Max 1 request per 2 seconds per zone
rate_limit_key = f"sensor_detect_zone_{zone_id}"
if cache.get(rate_limit_key):
    return Response({"error": "Rate limit exceeded"}, status=429)
cache.set(rate_limit_key, True, 2)
```

**2. Timeout Handling:**
```python
# External API calls with timeout
crowd_resp = requests.post(CROWD_PREDICT_URL, files=files, timeout=30)

# Specific error handling
except requests.Timeout:
    return Response({"error": "Crowd API timeout"}, status=504)
except requests.ConnectionError:
    return Response({"error": "Cannot connect to Crowd API"}, status=503)
```

**3. Retry Logic for Gemini API:**
```python
max_retries = 2
for attempt in range(max_retries):
    try:
        gemini_response = model.generate_content([prompt, img])
        break
    except Exception as retry_error:
        if attempt == max_retries - 1:
            raise
        time.sleep(1)  # Wait before retry
```

**4. File Handling Fix:**
```python
# Reset file pointer before reading
image_file.seek(0)
img = PIL.Image.open(image_file)
```

## Cloud Run Configuration

**Recommended Deployment Settings:**
```bash
gcloud run deploy ecoflow-backend \
    --image gcr.io/PROJECT_ID/ecoflow-backend \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --add-cloudsql-instances PROJECT_ID:us-central1:ecoflow-db \
    --concurrency 80 \
    --cpu 2 \
    --memory 1Gi \
    --min-instances 1 \
    --max-instances 10 \
    --timeout 300 \
    --set-env-vars "USE_CLOUD_SQL=True,..." \
    --set-secrets "DJANGO_SECRET_KEY=django-secret:latest,..."
```

### Key Parameters:
- **Concurrency**: 80 requests per instance (2 workers × 4 threads × 10 safety margin)
- **CPU**: 2 vCPU for better performance
- **Memory**: 1Gi to handle image processing
- **Min Instances**: 1 to avoid cold starts
- **Max Instances**: 10 for autoscaling under load

## Performance Metrics

### Before Optimization:
- Workers: 1
- Threads: 8
- Max Connections: 15
- Error Rate: ~40% (500 errors)
- No rate limiting
- No retry logic

### After Optimization:
- Workers: 2
- Threads: 4 per worker
- Max Connections: 100
- Connection Pooling: 60s
- Rate Limiting: 2s per zone
- Retry Logic: 2 attempts
- Timeout Handling: 30s

### Expected Improvements:
- **Throughput**: 2-3x increase
- **Error Rate**: <5% under normal load
- **Latency**: 20-30% reduction
- **Database Efficiency**: 80% reduction in connection overhead

## Monitoring Commands

**Check Cloud Run Logs:**
```bash
gcloud run services logs read ecoflow-backend --region=us-central1 --limit=100
```

**Monitor Database Connections:**
```bash
gcloud sql operations list --instance=ecoflow-db --limit=20
```

**View Service Metrics:**
```bash
gcloud run services describe ecoflow-backend --region=us-central1
```

## Troubleshooting

### High 500 Error Rate
1. Check database connections: `SELECT count(*) FROM pg_stat_activity;`
2. Verify Cloud SQL is not restarting
3. Check Gemini API quotas
4. Review Cloud Run logs for specific errors

### High 429 Error Rate
- Normal behavior under heavy load
- Indicates rate limiting is working
- Client should implement exponential backoff

### Memory Issues
```bash
# Increase memory allocation
gcloud run services update ecoflow-backend \
    --region=us-central1 \
    --memory 2Gi
```

### CPU Bottlenecks
```bash
# Increase CPU allocation
gcloud run services update ecoflow-backend \
    --region=us-central1 \
    --cpu 4
```

## Next Steps

1. **Enable Caching**: Implement Redis for session/query caching
2. **CDN Integration**: Use Cloud CDN for static assets
3. **Async Processing**: Move heavy image processing to Cloud Tasks
4. **Load Testing**: Use `locust` or `artillery` to test limits
5. **APM Integration**: Add Cloud Trace for detailed performance monitoring

## Cost Optimization

**Current Configuration Cost (Estimated):**
- Cloud Run: ~$15-30/month (depending on traffic)
- Cloud SQL (db-f1-micro): ~$9/month
- Total: ~$25-40/month

**To Reduce Costs:**
- Use `--min-instances 0` if occasional cold starts are acceptable
- Implement caching to reduce database queries
- Optimize image sizes before processing
- Use Cloud Storage for image caching
