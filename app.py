import streamlit as st
import numpy as np
import pandas as pd
import cv2
import openai
import wikipediaapi
import pdfplumber
import pytesseract
from pdf2image import convert_from_bytes


def get_wikipedia_content(url):
    if "de.wikipedia.org" in url:
        country_flag = "de"
    else:
        country_flag = "en"
    wiki = wikipediaapi.Wikipedia(
        "Api-User-Agent", country_flag
    ) 
    page_name = url.split("/")[-1]  # Extract the page name from the URL
    page = wiki.page(page_name)

    if page.exists():
        return page.text
    else:
        return "Page not found."


def ask_gpt(kwargs):
    print("Inside GPT func")
    simplify = ""
    if kwargs["simplify"] == "yes":
        simplify = ". Explain it in a way so that a child can understand it. "
    if kwargs["language"] == "German":
        prompt = f"Translate the following text to german while also giving a {kwargs['length']} summary of the translation{simplify}Only return the summarized translation:\n{kwargs['prompt']}"
    if kwargs["language"] == "English":
        prompt = f"Give a {kwargs['length']} summary of the following text{simplify}:\n{kwargs['prompt']}"
    openai.api_key = api_key

    prompt = prompt.strip()
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k", messages=[{"role": "user", "content": prompt}]
    )
    return completion


def read_pdf(file):
    pdf_lang = st.radio("Choose the language of your pdf document", ["German", "English"])
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
            handle_button_click(content)


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
            # transfer image of pdf_file into array
            img = np.asarray(page)
            # transfer into grayscale
            cv2_img = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
            st.image(cv2_img)
            thresh = cv2.threshold(cv2_img, 150, 255, cv2.THRESH_BINARY_INV)[1]
            result = cv2.GaussianBlur(thresh, (5,5), 0)
            result = 255 - result
            content += pytesseract.image_to_string(result, lang=lang, config='--psm 6')
    return content


def handle_button_click(input):
    if len(input) > 3:
        result = ask_gpt(
            {
                "prompt": input,
                "length": length,
                "simplify": simplify,
                "language": language,
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
        st.markdown("---")
    st.session_state.prompt = ""


def handle_wiki_click():
    url = prompt
    content = get_wikipedia_content(url)
    if len(content) > 10:
        handle_button_click(content)

def user_options():
    length = st.select_slider(
        "Choose the length of the summary",
        options=["Very short", "short", "detailed", "very detailed"],
        value=("short"),
    )
    simplify = st.radio(
        "Simplify the output to make it more accessible for children",
        options=("No", "Yes"),
    )
    language = st.radio("Select Output language", options=("German", "English"))
    return length, simplify, language


st.set_page_config(page_title="GPT-Summarizer")
st.markdown(
    """
<style>
.css-h5rgaw.ea3mdgi1
{
    visibility: hidden;
}
.css-cio0dv.ea3mdgi1
{
    visibility: hidden;
}         
</style>
""",
    unsafe_allow_html=True,
)

input_placeholder = st.empty()
api_key = input_placeholder.text_input("Set your OpenAI API key:")
if api_key:
    input_placeholder.empty()
    st.title("Summarize and translate your texts using GPT 3.5")

    mode = st.selectbox(
        "Choose your preferred way of input", options=("Manual input", "Wikipedia URL", "PDF Upload")
    )

    if mode == "Manual input":
        length, simplify, language = user_options()
        prompt = st.text_area("Enter any text to summarize", value="", height=150)
        if st.button("Start"):
            handle_button_click(prompt)
    elif mode == "Wikipedia URL":
        length, simplify, language = user_options()
        prompt = st.text_input("Enter any wikipedia URL", value="")
        if st.button("Start"):
            handle_wiki_click()
    elif mode == "PDF Upload":
        file = st.file_uploader("Upload a PDF file", type="pdf", accept_multiple_files=False)
        length, simplify, language = user_options()
        if file:
            read_pdf(file)
            
