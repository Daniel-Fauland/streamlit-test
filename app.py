import streamlit as st
import time
import backend


def user_options_summarize(mode):
    length = st.select_slider(
        "Choose the length of the summary",
        options=["Very short", "short", "detailed", "very detailed"],
        value=("short"),
    )
    simplify = st.radio(
        "Simplify the output to make it more accessible for children",
        options=("No", "Yes"),
    )
    if mode == "PDF Upload":
        inp_language = st.radio("Select Input language", options=("German", "English"))
    else:
        inp_language = ""
    language = ""
    return length, simplify, inp_language, language


def user_options_translate(mode):
    length = ""
    simplify = ""
    if mode == "PDF Upload":
        inp_language = st.radio("Select Input language", options=("German", "English"))
    else:
        inp_language = ""
    language = st.radio("Select Output language", options=("German", "English"))
    return length, simplify, inp_language, language


def user_options_summarize_translate(mode):
    length = st.select_slider(
        "Choose the length of the summary",
        options=["Very short", "short", "detailed", "very detailed"],
        value=("short"),
    )
    simplify = st.radio(
        "Simplify the output to make it more accessible for children",
        options=("No", "Yes"),
    )
    if mode == "PDF Upload":
        inp_language = st.radio("Select Input language", options=("German", "English"))
    else:
        inp_language = ""
    language = st.radio("Select Output language", options=("German", "English"))
    return length, simplify, inp_language, language


def mode_options(user_option):
        if user_option == "summarize":
            length, simplify, inp_language, language = user_options_summarize(mode)
        elif user_option == "translate":
            length, simplify, inp_language, language = user_options_translate(mode)
        elif user_option == "summarize_translate":
            length, simplify, inp_language, language = user_options_summarize_translate(mode)
        if mode == "Manual input":
            prompt = st.text_area("Enter any text to summarize", value="", height=150)
            if st.button("Start"):
                start_time = time.time()
                backend.handle_button_click(feature, api_key, start_time, prompt, length, simplify, language, inp_language)
        elif mode == "Wikipedia URL":
            prompt = st.text_input("Enter any wikipedia URL", value="")
            if st.button("Start"):
                start_time = time.time()
                backend.handle_wiki_click(feature, api_key, start_time, prompt, length, simplify, language, inp_language)
        elif mode == "PDF Upload":
            file = st.file_uploader("Upload a PDF file", type="pdf", accept_multiple_files=False)
            if file:
                start_time = time.time()
                backend.read_pdf(feature, api_key, start_time, file, length, simplify, language, inp_language)


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

    feature = st.selectbox(
        "Choose your preferred feature", options=("Summarize only", "Translate only", "Summarize & Translate")
    )

    mode = st.selectbox(
        "Choose your preferred way of input", options=("Manual input", "Wikipedia URL", "PDF Upload")
    )

    if feature == "Summarize only":
        mode_options("summarize")
    elif feature == "Translate only":
        mode_options("translate")
    elif feature == "Summarize & Translate":
        mode_options("summarize_translate")
