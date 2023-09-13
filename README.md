# Streamlit App

## Run locally

- Install requirements:

  ```shell
  pip install -r requirements.txt
  ```

- Start streamlit web-app locally by running the following command:

  ```shell
  streamlit run app.py
  ```

## Dockerize application

If you plan to run the docker container locally you have to remove the following option:

```shell
--server.enableCORS false
```

- Build the docker image

  ```shell
  docker build -t my-streamlit-app .
  ```

- Run the docker container
  ```shell
  docker run -p 8080:8080 my-streamlit-app
  ```

## Deploy to GCP using Cloud Run

For more detailed instructions check out this [tutorial](https://github.com/Daniel-Fauland/gcp-test/tree/main/cloud_run).

- Tag the docker image

  ```shell
  docker tag my-streamlit-app europe-west3-docker.pkg.dev/propane-nomad-396712/cloud-run/my-streamlit-app
  ```

- Push the tagged image to Artifact Registry

  ```shell
  docker push europe-west3-docker.pkg.dev/propane-nomad-396712/cloud-run/my-streamlit-app
  ```

- Deploy the application using gcloud

  ```shell
  gcloud run deploy my-streamlit-app \
  --image europe-west3-docker.pkg.dev/propane-nomad-396712/cloud-run/my-streamlit-app \
  --platform managed \
  --allow-unauthenticated
  ```

- You can retrieve the url at any time with this command

  ```shell
  gcloud run services describe my-streamlit-app --platform managed --region europe-west3 --format 'value(status.url)'
  ```
