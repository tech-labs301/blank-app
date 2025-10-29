import streamlit as st
import json
import time
import os
from openai import OpenAI

from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="Media Recommender",
    page_icon="",
    layout="wide"
)

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

#t
system_prompt = " Give recoomendations based on the user preferences"


#create session
if "history" not in st.session_state:
    st.session_state.history = []  # List of recommendations 

if "feedback" not in st.session_state:
    st.session_state.feedback = []

if "chat" not in st.session_state: 
    st.session_state.chat = [{"role": "system", "content": system_prompt}]  

st.title("Media reccomendation!")
st.caption(
    "Hello, this is a media reccomendation, so put in the topics you want and ai will help you choose out what you wanted"
)

col1, col2 = st.columns(2)

with col1: 
    media_type = st.selectbox("Media type", ["Movies", "Games", "TV show", "Book"])
    length = st.selectbox("length", ["Short", "Medium", "Long"])
    genres = st.multiselect("Genres", ["Action", "Comedy", "Drama", "Horror", "Mystery", "Science fiction", "Thriller", "Western","RPG", "Strategy", "Indie", "Other"],
    max_selections = 3 
    )
    

with col2:
    topic = st.text_input("Specific topic", placeholder="baseball, goverment, health, arts, technology, weather, hobbies, travel, etc." )
    similar_items = st.text_input("Similar Items (Optional)" )
    people = st.text_input("People (Optional)")


st.markdown("**Content preferences**")  
c1, c2, c3, c4 = st.columns(4) 
content_flags = []


def get_recs(prefs):
    
    sys = """
    You are a reccomendation engine and your goal is to provide a good media reccomendation for the user based on there prefernces 
    Make sure all of the content is Family-friendly
    Give the response in this format (JSON): 
{
   title:  "..."
   type:  "..."
   rating:  "..."
   genre:  "..."
   lenght: "..."
   why: "2-4 sentences"
   

}

    """

    user_prompt = f"""
    Please reccomend 1 item of {prefs[media_type]} based on 

    Preferred Genre: {prefs[genres]}
    Preferred topic/characters: {prefs[topic]}
    Preferred similar Items: {prefs[similar_items]}
    Preferred people: {prefs[people]}
    Preferred length: {prefs[length]}
    Preferred content flags: {prefs[content_flags]}
    Preferred number of items: {prefs[content_flags]}
    # Preferred avoid titles: {prefs[avoid_titles]}



    """

    if not client:
        return None
        # API CALL 
    try:
        response = client.chat.completions.create( 
            model= "gpt-3.5-turbo-0125",
            messages=[
                {"role": "system", "content": sys},
                {"role": "user", "content": user_prompt}
                
                
                ]
        )
     
     # RETURN THE RESPONSE  
        r =  response.choices[0].message.content
        rec = json.loads(r)
        for k in ["title", "rating", "type", "genre", "length", "why"]:
            if k  not in rec:
                raise ValueError(f"Missing Key {k}")

        return rec
    except Exception as e:
        st.error(f"ai error")

if st.button("show recommendations", type="primary", disabled= not api_key ):
   
 #media_type, genres, topic, similiar_items, people, length , content_flags, avoid_titles, 
    prefs  = { 
        "media_type": media_type,
        "genres": genres,
        "topic": topic,
        "similar_items": similar_items,
        "people": people,
        "length": length,
        "content_flags": content_flags,
    
    }

    with st.spinner("Finding Recommendation"):
        item = get_recs(prefs)
    if item:
        st.session_state.history.append({"prefs": prefs, "item": item})

#----DISPLAY----
st.markdown("---")
st.subheader("Reccomendation")
if st.session_state.history:
    last = st.session_state.history[-1]["item"]
    #TODO show title using markdown 
    st.markdown(f"### {last['title']}")
    #TODO show info using st.caption - type, genre, rating, length
    st.caption(f" {last['type']} - {last['genre']} - {last[rating]} - {last['length']}")
    #TODO show why using write 
    st.write(f" {last['why']}")

    b1, b2, b3 = st.columns([1,1,6]) 
    with b1:
        if st.button("Like"):
            st.session_state.feedback.append({
                #last elemenets title type genre thumb : up
                "title": last["title"],
                "type": last["type"],
                "genre": last["genre"],
                "thumb": "up"

            })
            st.toast("Saved as Liked")
        if st.button("Dislike"):
            st.session_state.feedback.append({
                #last elemenets title type genre thumb : up
                "title": last["title"],
                "type": last["type"],
                "genre": last["genre"],
                "thumb": "down"

            })
            st.toast("Saved as Disliked")

        with b3:
            pass
else:
    st.info("Fill out the form and click Show Reccomendation")

#---Recommend Another 
st.markdown("---")

if st.session_state.history and st.button("Recommend Another"):
    last_prefs = st.session_state.history[-1]["prefs"].copy()
    last_prefs["avoid_titles"] = [f["title"] for f in st.session_state.feedback if f["thumb"] == "down"]
    with st.spinner("Finding Another..."):
        item = get_recs(last_prefs)
    if item:
       st.session_state.history.append({"prefs": last_prefs, "item": item})

    
