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

- **Note:** This app uses "tesseract" for OCR. You need to [install the executable](https://tesseract-ocr.github.io/tessdoc/Installation.html) as well as the python package in order to run it successfully.

- **Note:** In order to convert a PDF to an image with "image2pdf" before sending it to tesseract you also need to [install poppler](https://pdf2image.readthedocs.io/en/latest/installation.html) which can not be installed with pip

## Dockerize application

- Build the docker image

  x86:

  ```shell
  docker build -t my-streamlit-app .
  ```

  Apple silicon:

  ```shell
  docker build --platform linux/amd64 -t my-streamlit-app .
  ```

- Run the docker container (optional)

  ```shell
  docker run -p 8080:8080 my-streamlit-app
  ```

  **Note:** If you want to run the docker container locally on an Apple silicon Mac you should not specify the platform to built it natively for ARM to massively increase the performance of the application

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
  --allow-unauthenticated \
  --memory=8Gi \
  --cpu=4
  ```

- You can retrieve the url at any time with this command

  ```shell
  gcloud run services describe my-streamlit-app --platform managed --region europe-west3 --format 'value(status.url)'
  ```
