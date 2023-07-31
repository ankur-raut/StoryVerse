import streamlit as st
import streamlit.components.v1 as components
import pyttsx3
#import voices as voices

st.title('Page 2')


def read_file(file_path):
    with open(file_path, 'r') as file:
        response = file.read()
        return response


def splitter(response):
    scenes = (response.split('^')[0])
    imgs = (response.split('^')[1])

    scenes_list = (scenes.split(';'))
    imgs_list = (imgs.split(';'))
    return scenes_list, imgs_list


def speaker(text):
    engine = pyttsx3.init()
    engine.setProperty('rate', 135)
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[1].id)
    engine.say(text)
    try:
        engine.runAndWait()
        engine.stop()
    except:
        st.write("Wait")



scenes_list, imgs_list = splitter(read_file('pages/file.txt'))

# Create three columns using st.columns()
col1, col2 = st.columns(2)
# Add content to the columns
col1.markdown('<a href="/main" target="_self"> <- Previous</a>', unsafe_allow_html=True)
col2.markdown('<a href="/Page_3" target="_self"> Next -> </a>', unsafe_allow_html=True)

components.html(
    f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Image and Text Example</title>
    </head>
    <body>
        <div style="background-color: white;">
        &nbsp
            <center><img src="{imgs_list[0]}" alt="Image 1" width="512" height="512">
            <p style="padding-left: 20px; padding-right: 20px;">{scenes_list[0]}</p></center>
        &nbsp
        </div>
    </body>
    </html>
    """,
    height=600,
)

# if st.button("Sound"):
#     speaker(scenes_list[0])


