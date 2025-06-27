
import streamlit as st
from io import StringIO
from dotenv import load_dotenv

import os
from io import BytesIO
from PIL import Image
from google import genai
from google.genai import types



st.set_page_config(page_title='AI StyleFrame', 
                    page_icon = "images/gemini_avatar.png",
                    initial_sidebar_state = 'auto',
                    layout='wide')


@st.cache_data
def initialize_model():
    load_dotenv()
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    os.environ["GEMINI_API_KEY"] = GEMINI_API_KEY
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])

background_color = "#252740"

avatars = {
    "assistant" : "images/gemini_avatar.png",
    "user": "images/user_avatar.png"
}

st.markdown("<h2 style='text-align: center; color: #428ED7;'>AI StyleFrame</h2>", unsafe_allow_html=True)

face_col, side_col, top_col, back_col = st.columns(4)

with face_col:
    box_color = "#428ED7"
    st.markdown(
        f"""
        <div style="background-color:{box_color};padding-left:20px;border-radius:5px">
            <h1 style="color:#f1f9ff;text-align:left;font-size:20px">Front</h1>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("""---""", unsafe_allow_html=True)   

with side_col:
    box_color = "#428ED7"
    st.markdown(
        f"""
        <div style="background-color:{box_color};padding-left:20px;border-radius:5px">
            <h1 style="color:#f1f9ff;text-align:left;font-size:20px">Side</h1>
        </div>
        """,
        unsafe_allow_html=True,
    )  
    st.markdown("""---""", unsafe_allow_html=True)

with top_col:
    box_color = "#428ED7"
    st.markdown(
        f"""
        <div style="background-color:{box_color};padding-left:20px;border-radius:5px">
            <h1 style="color:#f1f9ff;text-align:left;font-size:20px">Top</h1>
        </div>
        """,
        unsafe_allow_html=True,
    )  
    st.markdown("""---""", unsafe_allow_html=True)

with back_col:
    box_color = "#428ED7"
    st.markdown(
        f"""
        <div style="background-color:{box_color};padding-left:20px;border-radius:5px">
            <h1 style="color:#f1f9ff;text-align:left;font-size:20px">Back</h1>
        </div>
        """,
        unsafe_allow_html=True,
    )  
    st.markdown("""---""", unsafe_allow_html=True)

with st.sidebar:
    st.image("images/gemini_avatar.png")


gender_options = ["girl", "boy", "man", "woman"]
background_options = ["studio", "city", "nature"]
item_color_options = ["unchanged from original", "black", "darkblue", "blue", "green", "red", "grey"]
options = {
    "gender": gender_options[0],
    "background": background_options[0],
    "color": item_color_options[0]
}

with st.sidebar:
    gender = st.selectbox("Select person type", options=gender_options, index=0)
    background = st.selectbox("Select background", options=background_options, index=0)
    item_color = st.selectbox("Select item color", options=item_color_options, index=0)
    uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

    options = {
        "gender": gender,
        "background": background,
        "color": item_color
    }

    print(options)

    if uploaded_file:
        image_bytes =Image.open(uploaded_file)
        if "image" not in st.session_state:
            st.session_state.image = image_bytes
        st.image(image_bytes, caption="Uploaded Image", use_column_width=True)




def run_query(input_text, options):
    """
    Run query. The model is initialized and then queried.
    Args:
        input_text (str): we are just passing to the model the user prompt
    Returns:
        response.text (str): the text of the response
    """
    try:
        load_dotenv()
        GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
        os.environ["GEMINI_API_KEY"] = GEMINI_API_KEY
        client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
        system_prompt = f"""
            You are an expert styling assistant that will generate assets.
            In the following the content of the initial image is called 'the item'

            #INSTRUCTIONS
            Generate an image according to the instructions:
            Modify the initial image to display a '{options['gender']}' wearing the item.
            The item is modified to be of the following color: '{options['color']}'.
            The image will have a background as following: '{options['background']}'

            # DETAILS
            If the background is 'studio', a simple, neutral background color will be displayed.
            If the background is 'city', a city street background adapted to the item will be displayed.
            If the background is 'nature', a natural outdoor setup adapted to the item will be displayed as a background.

            If the instructions require to show full body, show entire body, from the feet to the top of the head.
            If the instructions require to show top only, show only the upper torso and full head.


            #OUTPUT
            A generated image and a short text. The short text is describing the item, as modified (e.g. the color) from 
            the instructions.
        """

        print(system_prompt)

        contents = ([system_prompt,input_text], st.session_state.image)
        
        response = client.models.generate_content(
            model="gemini-2.0-flash-exp-image-generation",
            contents=contents,
            config=types.GenerateContentConfig(
            response_modalities=['Text', 'Image']
            )
        )

        if response:
            return response
        
        else:
            return "Error"

    except Exception as ex:
        print(f"Exception: {ex}")
        return f"Exception: {ex}"
    

def unpack_response(prompt, options=options):
    response = run_query(prompt, options=options)
    placeholder = st.empty()
    full_response = ""
    generated_image = None

    try:
        for part in response.candidates[0].content.parts:
            if part.text is not None:
                for item in part.text:
                    full_response += item
            elif part.inline_data is not None:
                generated_image = Image.open(BytesIO((part.inline_data.data)))
    except Exception as ex:
        full_response = f"ERROR: {full_response}"
        generated_image = st.session_state.image

    return full_response, placeholder, generated_image


if st.sidebar.button("Generate") and uploaded_file:
    prompt = "Show person full body front side"
    with st.spinner("Thinking..."):

        full_response, placeholder, first_generated_image = unpack_response(prompt, options=options)
        if first_generated_image:
            with face_col:
                st.image(first_generated_image)
    
    # replace session_state.image to keep the same person in the next images
    st.session_state.image = first_generated_image
    with st.spinner("Thinking..."):
        prompt = "Show person full body from one side. Keep the same person and clothes, do not change clothes color  or clothes pattern, and keep the same background"
        full_response, placeholder, generated_image = unpack_response(prompt, options=options)
        if generated_image:
            with side_col:
                st.image(generated_image)


    with st.spinner("Thinking..."):
        prompt = "Show person top body (torso & head) from front. Keep the same person and clothes, do not change clothes color or clothes pattern, and keep the same background"
        full_response, placeholder, generated_image = unpack_response(prompt, options=options)
        if generated_image:
            with top_col:
                st.image(generated_image)

    with st.spinner("Thinking..."):
        prompt = "Show person full body from back. Keep the same person and clothes, do not change clothes color  or clothes pattern, and keep the same background"
        full_response, placeholder, generated_image = unpack_response(prompt, options=options)
        if generated_image:
            with back_col:
                st.image(generated_image)
