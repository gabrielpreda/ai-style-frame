#!/bin/bash

# Purpose: To deploy the App to Cloud Run.

# Google Cloud Project (replace with your actual project ID)
PROJECT=<YOUR_PROJECT_ID>

# Google Cloud Region (replace with your actuall region: where the Gemini model is allowed)
LOCATION=<your_region>

# Depolying app from source code
sudo ~/google-cloud-sdk/bin/gcloud run deploy simple-app --source . --region=$LOCATION --project=$PROJECT --allow-unauthenticated