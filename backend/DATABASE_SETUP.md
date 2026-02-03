# Cloud SQL PostgreSQL Setup - Complete ✅

## Database Information
- **Instance Name**: ecoflow-db
- **Database**: ecoflow_prod
- **User**: ecoflow_user
- **Region**: us-central1
- **Public IP**: 136.119.237.102
- **Connection Name**: qwiklabs-gcp-03-266c2fb0e304:us-central1:ecoflow-db

## Local Development

### Environment Variables (.env)
```env
USE_CLOUD_SQL=True
DB_NAME=ecoflow_prod
DB_USER=ecoflow_user
DB_PASSWORD=EcoflowAIPWD
DB_HOST=136.119.237.102
DB_PORT=5432
```

### Run Locally
```bash
# Activate virtual environment
source .venv/bin/activate

# Run migrations
python manage.py migrate

# Start server
python manage.py runserver
```

## Production Deployment (Cloud Run)

### Secrets Created
- ✅ django-secret
- ✅ db-password
- ✅ gemini-api-key
- ✅ email-user
- ✅ email-password

### Deploy Command
```bash
./deploy.sh
```

### Manual Deployment
```bash
# Build and push image
gcloud builds submit --tag gcr.io/qwiklabs-gcp-03-266c2fb0e304/ecoflow-backend

# Deploy to Cloud Run
gcloud run deploy ecoflow-backend \
    --image gcr.io/qwiklabs-gcp-03-266c2fb0e304/ecoflow-backend \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --add-cloudsql-instances qwiklabs-gcp-03-266c2fb0e304:us-central1:ecoflow-db \
    --set-env-vars "USE_CLOUD_SQL=True" \
    --set-env-vars "DB_NAME=ecoflow_prod" \
    --set-env-vars "DB_USER=ecoflow_user" \
    --set-env-vars "DB_HOST=/cloudsql/qwiklabs-gcp-03-266c2fb0e304:us-central1:ecoflow-db" \
    --set-env-vars "DB_PORT=5432" \
    --set-secrets "DJANGO_SECRET_KEY=django-secret:latest" \
    --set-secrets "DB_PASSWORD=db-password:latest" \
    --set-secrets "GEMINI_API_KEY=gemini-api-key:latest" \
    --set-secrets "EMAIL_HOST_USER=email-user:latest" \
    --set-secrets "EMAIL_HOST_PASSWORD=email-password:latest"
```

## Database Management

### Connect to Database
```bash
# Via gcloud
gcloud sql connect ecoflow-db --user=ecoflow_user --database=ecoflow_prod

# Via psql (if installed)
psql "host=136.119.237.102 dbname=ecoflow_prod user=ecoflow_user password=EcoflowAIPWD"
```

### Backup Database
```bash
# Create backup
gcloud sql backups create --instance=ecoflow-db

# List backups
gcloud sql backups list --instance=ecoflow-db

# Restore from backup
gcloud sql backups restore BACKUP_ID --backup-instance=ecoflow-db
```

### View Logs
```bash
# Cloud SQL logs
gcloud sql operations list --instance=ecoflow-db

# Cloud Run logs
gcloud run services logs read ecoflow-backend --region=us-central1
```

## Important Notes

1. **SQLite vs PostgreSQL**: The app automatically switches based on `USE_CLOUD_SQL` environment variable
2. **Authorized Networks**: Your current IP (87.101.253.150) is authorized. Add new IPs with:
   ```bash
   gcloud sql instances patch ecoflow-db --authorized-networks=NEW_IP_ADDRESS
   ```
3. **Secret Updates**: To update a secret:
   ```bash
   echo -n 'new-value' | gcloud secrets versions add SECRET_NAME --data-file=-
   ```

## Troubleshooting

### Connection Issues
- Verify Cloud SQL is running: `gcloud sql instances describe ecoflow-db`
- Check authorized networks: `gcloud sql instances describe ecoflow-db --format="value(settings.ipConfiguration.authorizedNetworks)"`

### Permission Issues
- Ensure service account has roles:
  - `roles/cloudsql.client`
  - `roles/secretmanager.secretAccessor`

### Migration Issues
```bash
# Check current migrations
python manage.py showmigrations

# Create new migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate
```
