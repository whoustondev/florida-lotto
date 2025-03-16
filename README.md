I am using google cloud at the moment. Some useful commands for dev

- Run the app 
gunicorn --bind :5000 --workers 1 --threads 8 --timeout 0 app:app

- Deploy the app
gcloud run deploy --source .

- Build image
docker build -t proj-fla-lotto .

- Access the app on the web
https://proj-fla-lotto-188715981166.us-east1.run.app
