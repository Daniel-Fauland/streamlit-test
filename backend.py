import streamlit as st
import langid
import time
import numpy as np
import pandas as pd
import cv2
import openai
import wikipediaapi
import pdfplumber
import pytesseract
from pdf2image import convert_from_bytes


def measure_response_time(start_time, text):
    now = time.time()
    diff = now - start_time
    text = f"Duration for {text}: {diff:.2f}"
    return text


def detect_language(text):
    lang, _ = langid.classify(text)
    if lang == "de":
        inp_language = "German"
    else:
        inp_language = "English"
    print(f"Detected language: {inp_language}")
    return inp_language


def get_wikipedia_content(url):
    if "de.wikipedia.org" in url:
        country_flag = "de"
        inp_language = "German"
    else:
        country_flag = "en"
        inp_language = "English"
    wiki = wikipediaapi.Wikipedia(
        "Api-User-Agent", country_flag
    ) 
    page_name = url.split("/")[-1]  # Extract the page name from the URL
    page = wiki.page(page_name)

    if page.exists():
        return page.text, inp_language
    else:
        return "Page not found.", inp_language


def ask_gpt(api_key, kwargs):
    openai.api_key = api_key
    simplify = ". "
    if kwargs["simplify"] == "yes":
        simplify = ". Explain it in a way so that a child can understand it. "

    feature = kwargs["feature"]
    if feature == "Summarize only":
        if kwargs["inp_language"] == "German":
            prompt = f"Give a {kwargs['length']} summary of the following text in german{simplify}:\n{kwargs['prompt']}"
        if kwargs["inp_language"] == "English":
            prompt = f"Give a {kwargs['length']} summary of the following text{simplify}:\n{kwargs['prompt']}"

    elif feature == "Translate only":
        if kwargs["inp_language"] == "German":
            prompt = f"Translate the following text to english and only return the translation:\n{kwargs['prompt']}"
        if kwargs["inp_language"] == "English":
            prompt = f"Translate the following text to german and only return the translation:\n{kwargs['prompt']}" 

    else: 
        if kwargs["inp_language"] == "German":
            if kwargs["language"] == "German":
                prompt = f"Give a {kwargs['length']} summary of the following text in german{simplify}:\n{kwargs['prompt']}"
            if kwargs["language"] == "English":
                prompt = f"Translate the following text to english while also giving a {kwargs['length']} summary of the translation{simplify}Only return the summarized translation:\n{kwargs['prompt']}"
        if kwargs["inp_language"] == "English":
            if kwargs["language"] == "German":
                prompt = f"Translate the following text to german while also giving a {kwargs['length']} summary of the translation{simplify}Only return the summarized translation:\n{kwargs['prompt']}"
            if kwargs["language"] == "English":
                prompt = f"Give a {kwargs['length']} summary of the following text{simplify}:\n{kwargs['prompt']}"


    prompt = prompt.strip()
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k", messages=[{"role": "user", "content": prompt}]
    )
    return completion


def read_pdf(feature, api_key, start_time, file, length, simplify, language, inp_language):
    pdf_lang = inp_language
    with pdfplumber.open(file) as pdf:
        page_count = len(pdf.pages)
        if page_count == 1:
            st.write(f"There is 1 page in your pdf document")
        elif page_count > 1:
            st.write(f"There are {len(pdf.pages)} pages in your pdf document")
        else:
            st.write(f"No pages found in your pdf document. Please check your uploaded file!")
            return None
        
        pdf_start_page = st.number_input(f"Choose your start page between 1 and {page_count}", 1, page_count, value=1)
        if pdf_start_page:
            pdf_end_page = st.number_input(f"Choose your end page between {pdf_start_page} and {page_count}", pdf_start_page, page_count, value=pdf_start_page)
        if st.button("Start"):
            content = extract_pdf_text(pdf, int(pdf_start_page), int(pdf_end_page), file, pdf_lang)
            handle_button_click(feature, api_key, start_time, content, length, simplify, language, inp_language)


def extract_pdf_text(pdf, start, end, file, pdf_lang):
    content = ""
    for i in range(len(pdf.pages)):
            if i+1 >= start and i+1 <= end:
                page = pdf.pages[i]
                content += page.extract_text()
                content += "\n\n" 
    if len(content) < 10:
        st.write("There is no selectable text in the pdf document. Switching to OCR mode...")
        content = ocr_text_from_file(file, start, end, pdf_lang)
        return content
    else:
        return content
    

def ocr_text_from_file(file, start, end, lang="deu"):
    if lang == "English":
        lang = "eng"
    else: 
        lang = "deu"
    content = ""
    file = file.getvalue()
    pdf = convert_from_bytes(file)
    for (i,page) in enumerate(pdf):
        if i+1 >= start and i+1 <= end:
            now = time.time()
            # transfer image of pdf_file into array
            img = np.asarray(page)
            # transfer into grayscale
            cv2_img = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
            st.image(cv2_img, width=250)
            thresh = cv2.threshold(cv2_img, 150, 255, cv2.THRESH_BINARY_INV)[1]
            result = cv2.GaussianBlur(thresh, (5,5), 0)
            result = 255 - result
            st.text(measure_response_time(now, f"reading CV2 image {i+1}/{len(pdf)}"))
            now = time.time()
            content += pytesseract.image_to_string(result, lang=lang, config='--psm 6')
            st.text(measure_response_time(now, f"OCR image {i+1}/{len(pdf)}"))
    return content

def handle_button_click(feature, api_key, start_time, input, length, simplify, language, inp_language):
    if len(input) > 3:
        if inp_language == "":
            inp_language = detect_language(input)
        now = time.time()
        result = ask_gpt(api_key,
            {
                "prompt": input,
                "length": length,
                "simplify": simplify,
                "language": language,
                "inp_language": inp_language,
                "feature": feature
            }
        )
        st.markdown("---")
        result_msg = result.choices[0].message.content
        result_prompt_tokens = result.usage.prompt_tokens
        result_output_tokens = result.usage.completion_tokens
        result_tokens = result_prompt_tokens + result_output_tokens
        cost = (result_prompt_tokens / 1000) * 0.003 + (
            result_output_tokens / 1000
        ) * 0.004
        output_msg = st.text_area("GPT result", value=result_msg, height=350)
        output_tokens = st.text(f"Tokens used for completing the task: {result_tokens}")
        output_price = st.text(f"Cost for completing the task: {round(cost, 4)}$")
        api_duration = st.text(measure_response_time(now, "GPT API call"))
        full_duration = st.text(measure_response_time(start_time, "entire response"))
        st.markdown("---")
    st.session_state.prompt = ""


def handle_wiki_click(feature, api_key, start_time, input, length, simplify, language, inp_language):
    content, inp_language = get_wikipedia_content(input)

    if len(content) > 10:
        handle_button_click(feature, api_key, start_time, content, length, simplify, language, inp_language)
