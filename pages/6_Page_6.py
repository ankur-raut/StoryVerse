import base64
import os

import pyttsx3
import streamlit as st
import streamlit.components.v1 as components
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Image, Paragraph, PageBreak, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.units import inch

st.title('Page 5')


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


def get_binary_file_downloader_html(file_path, file_label='File'):
    with open(file_path, 'rb') as f:
        data = f.read()
    b64 = base64.b64encode(data).decode('utf-8')
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="{os.path.basename(file_path)}">{file_label}</a>'
    return href


def create_pdf(text_list, image_list):
    doc = SimpleDocTemplate("pages/output.pdf", pagesize=letter, topMargin=1.5 * inch)

    styles = getSampleStyleSheet()
    text_style = ParagraphStyle(
        "Text",
        parent=styles["Normal"],
        fontName="Courier",
        fontSize=18,
        alignment=TA_JUSTIFY,
        spaceAfter=15,  # Increased space after each paragraph
        spaceBefore=15,
        spaceWithin=0.2,
        textColor="black",
        leftIndent=0,
        rightIndent=0,
        leading=22
    )

    flowables = []

    for i in range(min(len(text_list), len(image_list)) - 1):
        flowables.append(Spacer(1, 0.7 * inch))  # Add some space between text and image

        image = Image(image_list[i], width=7 * inch, height=5 * inch)
        image.hAlign = "CENTER"
        flowables.append(image)

        flowables.append(Spacer(1, 0.5 * inch))  # Add some space between text and image
        text = Paragraph(text_list[i], text_style)
        flowables.append(text)

        flowables.append(PageBreak())

    doc.build(flowables)
    st.write("Done")


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

colnav1, colnav2 = st.columns(2)
colnav1.markdown('<a href="/Page_4" target="_self"> <- Previous </a>', unsafe_allow_html=True)
colnav2.markdown('<a href="/main" target="_self"> Main => </a>', unsafe_allow_html=True)

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
            <center><img src="{imgs_list[4]}" alt="Image 1" width="512" height="512">
            <p style="padding-left: 20px; padding-right: 20px;">{scenes_list[4]}</p></center>
        &nbsp
        </div>
    </body>
    </html>
    """,
    height=600,
)

col2, col3, col4, col5 = st.columns(4)

# with col2:
#     if st.button("Sound"):
#         speaker(scenes_list[4])

# with col3:
#     if st.button("Full audio"):
#         for i in range(0, len(scenes_list)):
#             speaker(scenes_list[i])

with col4:
    if st.button("Create PDF"):
        create_pdf(scenes_list, imgs_list)

with col5:
    if st.button("Download PDF"):
        if os.path.exists("pages/output.pdf"):
            st.markdown(get_binary_file_downloader_html("pages/output.pdf", "PDF File"), unsafe_allow_html=True)
        else:
            st.write("File does not exist")
