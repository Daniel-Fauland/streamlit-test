import streamlit as st
import openai
import wikipediaapi


def get_wikipedia_content(url, country_flag):
    wiki = wikipediaapi.Wikipedia(
        "Api-User-Agent", country_flag
    )  # Set the language of the Wikipedia you want to access (in this case, "en" for English)
    page_name = url.split("/")[-1]  # Extract the page name from the URL
    page = wiki.page(page_name)

    if page.exists():
        return page.text
    else:
        return "Page not found."


def askGPT(kwargs):
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


def handle_button_click(input):
    if len(input) > 5:
        result = askGPT(
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
        output_tokens = st.text(f"Tokens used for completing the task: {result_tokens}")
        output_price = st.text(f"Cost for completing the task: {round(cost, 4)}$")
        output_msg = st.text_area("GPT result", value=result_msg, height=350)
        st.markdown("---")


def handle_wiki_click():
    url = wiki_prompt
    if "de.wikipedia.org" in url:
        country_flag = "de"
    else:
        country_flag = "en"
    content = get_wikipedia_content(url, country_flag)
    if len(content) > 10:
        handle_button_click(content)


st.set_page_config(page_title="GPT-Summarizer")
input_placeholder = st.empty()
api_key = input_placeholder.text_input("Set your OpenAI API key:")
if api_key:
    input_placeholder.empty()
    st.title("Summarize and translate your texts using GPT 3.5")

    st.markdown(
        """
    <style>
    .css-h5rgaw.ea3mdgi1
    {
        visibility: hidden;
    }         
    </style>
    """,
        unsafe_allow_html=True,
    )

    mode = st.selectbox(
        "Choose your preferred way of input", options=("Manual input", "Wikipedia URL")
    )

    if mode == "Manual input":
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
        prompt = st.text_area("Enter any text to summarize", value="", height=150)
        start_btn = st.button("Start", on_click=handle_button_click(prompt))
    elif mode == "Wikipedia URL":
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
        wiki_prompt = st.text_input("Enter any wikipedia URL", value="")
        start_btn = st.button("Start", on_click=handle_wiki_click)
