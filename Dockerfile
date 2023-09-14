FROM python:3.11
ENV PYTHONUNBUFFERED True

ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./

EXPOSE 8080

RUN pip install -r requirements.txt

#Install tesseract & ocrmypdf
RUN apt-get update -qqy && apt-get install -qqy \
        tesseract-ocr \
        libtesseract-dev \
        poppler-utils
        

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

CMD streamlit run --server.port=8080 app.py