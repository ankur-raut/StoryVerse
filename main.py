import streamlit as st
from langchain import OpenAI, Cohere, PromptTemplate
import openai
import json
import os
import replicate
from langchain.prompts import (
    PromptTemplate,
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field, validator
from typing import List

def story_generator(moral, element, outline, characters, choice):
    if choice == 'OpenAI':
        os.environ["OPENAI_API_KEY"] = api_key
        model_name = "gpt-3.5-turbo-16k"
        temperature = 0.0
        model = OpenAI(model_name=model_name, temperature=temperature)
        actor_query = f"""
        moral : {moral}
        element : {element}
        outline : {outline}
        characters : {characters}

        Go through above list. you are an expert kids story writer. Write a short kids story
        for ages 4-6 teaching given moral using given elements. The entire story should be divided into 4
        short scenes and less than 100 words in each scene. 

        The story should follow story outline if given. Strictly use character names if given or create yourself if not mentioned and create scenes for the story. Now, create
        prompts for each scene but do not include any character names but refer to the kind of animal explicitly.
        Make prompts in such a way that can be used for image generation prompts. Also create a negetive prompt for image generation.
        Negetive prompt should Specify things to not see in the output. The negetive prompt should be just
        maximum 4-5 words and only state what not to include in the image.
        Negetive prompt should strictly not start with : 'Do not include'

        Refer to follow below example and generate similar

            "title": string,
            "scenes":
            {{ "Scene 1" : string,
                "Prompt1": string,
                "NegetivePrompt1 : string ;}}

                {{"Scene 2": string,
                "Prompt2": string,
                "NegetivePrompt2 : string;}}
        """

    else:
        model = Cohere(cohere_api_key=api_key,max_tokens=2096)
        actor_query = f"""
        moral : {moral}
        element : {element}
        outline : {outline}
        characters : {characters}

        Go through above list. you are an expert kids story writer. Write a short kids story
        for ages 4-6 teaching given moral using given elements. The entire story should be divided into 4
        short scenes and less than 100 words in each scene. 

        The story should follow story outline if given. Strictly use character names if given or create yourself if not mentioned and create scenes for the story. Now, create
        prompts for each scene but do not include any character names but refer to the kind of animal explicitly.
        Make prompts in such a way that can be used for image generation prompts. 

        Refer to follow below example and generate similar

            "title": string,
            "scenes":
            {{ "Scene 1" : string,
                "Prompt1": string;}}

                {{"Scene 2": string,
                "Prompt2": string;}}
        """
    # Here's another example, but with a compound typed field.
    class Actor(BaseModel):
        title: str = Field(description="Title of the story")
        scenes: List[dict] = Field(description="Scene and the corresponding prompt")

    parser = PydanticOutputParser(pydantic_object=Actor)

    prompt = PromptTemplate(
        template="Answer the user query.\n{format_instructions}\n{query}\n",
        input_variables=["query"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    _input = prompt.format_prompt(query=actor_query)

    output = model(_input.to_string())
    out = parser.parse(output)
    return out


def image_generator(response, imagestyle, replicate_api_key,llm_name):
    temp = ""
    # data = json.loads(response)
    prompts = []
    negPrompt = []

    prompts.append(response.title)
    negPrompt.append(response.title)

    # Iterate over the scenes in the JSON
    for scene_dict in response.scenes:
        for key, value in scene_dict.items():
            if key.startswith("Prompt"):
                prompts.append(value)
    
    for scene_dict in response.scenes:
        for key, value in scene_dict.items():
            if key.startswith("NegetivePrompt"):
                negPrompt.append(value)

    # for key, value in data['scenes'].items():
    #     if key.startswith("Prompt"):
    #         prompts.append(value)

    if imagestyle == 'kids':
        imgprefix = 'Beautiful digital matte pastel paint'
        imgsuffix = 'greg rutkowski artstation 2.5d animated movie, sharp focus' #remove artists
    elif imagestyle == 'cartoon':
        imgprefix = 'Beautiful digital matte pastel paint'
        imgsuffix = 'Sylvain Sarrailh artstation 2.5d animated movie, sharp focus'
    elif imagestyle == 'disney':
        imgprefix = 'Beautiful digital water color style'
        imgsuffix = 'Craig Elliott artstation 2.5d animated movie, sharp focus'

    os.environ["REPLICATE_API_TOKEN"] = replicate_api_key

    if(llm_name=='OpenAI'):    
        for prompt,neg in zip(prompts,negPrompt):
            book_url = replicate.run(
                "stability-ai/stable-diffusion:27b93a2413e7f36cd83da926f3656280b2931564ff050bf9575f1fdf9bcd7478",
                input={"prompt": imgprefix + ' ' + prompt + ' ' + imgsuffix,"negative_prompt":neg}
            )
            temp = temp + book_url[0] + ";"
    else:
        for prompt in prompts:
            book_url = replicate.run(
                "stability-ai/stable-diffusion:27b93a2413e7f36cd83da926f3656280b2931564ff050bf9575f1fdf9bcd7478",
                input={"prompt": imgprefix + ' ' + prompt + ' ' + imgsuffix}
            )
            temp = temp + book_url[0] + ";"

    return temp


def extract_scenes(response):

    temp_str = ""
    # # Parse the JSON data
    # data = json.loads(response)
    temp_str = temp_str + response.title + ";"

    # Iterate over the scenes in the JSON
    for scene_dict in response.scenes:
        for key, value in scene_dict.items():
            if key.startswith("Scene"):
                temp_str = temp_str + value + ";"

    return temp_str
    # Return the list of scenes

def append_to_file(file_path, scenes_list, image_urls):
    try:
        with open(file_path, 'w') as file:
            file.write(str(scenes_list) + '^' + image_urls + '^')
        print("Parameters appended to the file successfully.")
    except IOError:
        print("An error occurred while appending parameters to the file.")

# Page title
st.set_page_config(page_title='Story Book Generator')
st.title('Story Book Generator')

#image_urls = "https://replicate.delivery/pbxt/st4eNRepb6kqhkBSwKJxE6aUFfbi4PoD8J0depCdgq5a0nxEB/out-0.png;https://replicate.delivery/pbxt/dXdC4abH4vZiANvtMrU5hSuW2t3R7RNyr62MR5QL1bVTfMmIA/out-0.png;https://replicate.delivery/pbxt/DfrZthFfc0lQIktpn2pp4YIqzl8zcLQH6tN8TpD23JVT9ZMRA/out-0.png;https://replicate.delivery/pbxt/IHIEsgWcEI4ICtxCDoqqrFf1c4G8tMSRjfv3oXXUBPMZ9ZMRA/out-0.png;"

with st.form('story_form', clear_on_submit=False):
    # Story
    story_outline = st.text_area('Enter story Outline (If any)', '', height=10)
    character_names = st.text_area('Enter story character and its names (If any)', '', height=10)

    with st.sidebar:
        moral_opt = st.selectbox(
            'What should be the morals?',
            ('Greed', 'honesty', 'friendship', 'patience'))

        element_opt = st.selectbox(
            'What should the element used for teaching?',
            ('humans', 'animals', 'reptiles', 'birds', 'fruits', 'vegetables'))

        imagestyle_opt = st.selectbox(
            'Select Image Style: ',
            ('cartoon', 'kids', 'disney'))

        llm_name = st.radio('Select LLM type: ', ('OpenAI', 'Cohere'))
        api_key = st.text_input('LLM API Key', type='password')

        replicate_api_key = st.text_input('Replicate API Key', type='password')

        submitted = st.form_submit_button('Submit')
if (submitted and api_key.startswith('4a')) or (submitted and api_key.startswith('sk-')):
    with st.spinner('Calculating...'):

        response = story_generator(moral_opt, element_opt, story_outline, character_names, llm_name)
        
        # response = """{
        # "title": "The Greedy Reptiles",
        # "scenes": {
        #     "Scene 1": "In a dense jungle, there were two reptiles, John and Henry. John was a clever chameleon, and Henry was a sly snake. They both loved basking in the warm sun and slithering through the tall grass.",
        #     "Prompt1": "two reptiles in a jungle, one changing colors and the other slithering through the grass",
        #     "Scene 2": "One day, John and Henry stumbled upon a shiny golden treasure hidden under a tree. Their eyes sparkled with greed as they imagined all the riches they could have.",
        #     "Prompt2": "two reptiles finding a shiny golden treasure under a tree",
        #     "Scene 3": "Unable to agree on how to divide the treasure, John and Henry decided to have a race. The winner would take it all. They slithered and sprinted, but in the end, both reptiles collapsed from exhaustion.",
        #     "Prompt3": "two reptiles racing towards the treasure, both collapsing from exhaustion",
        #     "Scene 4": "As the sun set, the jungle animals found the lifeless bodies of John and Henry. They realized that greed had cost the reptiles their lives. From that day on, the animals vowed to share and help each other.",
        #     "Prompt4": "jungle animals finding the lifeless bodies of two reptiles, learning the lesson of greed"
        # }
        # }"""
        
        # print("Story : " + response)
        print(response)
        scenes_list = extract_scenes(response)
        # print("scenes list : " + scenes_list)
        image_urls = image_generator(response, imagestyle_opt, replicate_api_key,llm_name)
        print("\n\n\nurls:")
        print(image_urls)
        append_to_file('pages/file.txt', scenes_list, image_urls)
        st.markdown('<a href="/Page_2" target="_self">Go to Book -></a>', unsafe_allow_html=True)
        del api_key

# requirements.txt
# data (pdfs)
# files
# utilitites
# modules

