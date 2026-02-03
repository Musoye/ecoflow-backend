#!/bin/bash
# Deploy to Cloud Run with Cloud SQL connection

# Set your variables
PROJECT_ID="qwiklabs-gcp-03-266c2fb0e304"
REGION="us-central1"
SERVICE_NAME="ecoflow-backend"
DB_INSTANCE="ecoflow-db"
CONNECTION_NAME="$PROJECT_ID:$REGION:$DB_INSTANCE"

# Build and push image
gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME

# Deploy to Cloud Run with Cloud SQL connection
gcloud run deploy $SERVICE_NAME \
    --image gcr.io/$PROJECT_ID/$SERVICE_NAME \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --add-cloudsql-instances $CONNECTION_NAME \
    --set-env-vars "USE_CLOUD_SQL=True" \
    --set-env-vars "DB_NAME=ecoflow_prod" \
    --set-env-vars "DB_USER=ecoflow_user" \
    --set-env-vars "DB_HOST=/cloudsql/$CONNECTION_NAME" \
    --set-env-vars "DB_PORT=5432" \
    --set-secrets "DJANGO_SECRET_KEY=django-secret:latest" \
    --set-secrets "DB_PASSWORD=db-password:latest" \
    --set-secrets "GEMINI_API_KEY=gemini-api-key:latest" \
    --set-secrets "EMAIL_HOST_USER=email-user:latest" \
    --set-secrets "EMAIL_HOST_PASSWORD=email-password:latest"

echo "Deployment complete!"
echo "Make sure you've created the secrets in Secret Manager first:"
echo "  gcloud secrets create django-secret --data-file=-"
echo "  gcloud secrets create db-password --data-file=-"
echo "  gcloud secrets create gemini-api-key --data-file=-"
echo "  gcloud secrets create email-user --data-file=-"
echo "  gcloud secrets create email-password --data-file=-"
