import streamlit as st
import google.generativeai as genai
import os
import json
from dotenv import load_dotenv
import database as db
import pandas as pd # Still needed for the admin dashboard dataframe

# --- Initial Setup ---
load_dotenv()
st.set_page_config(page_title="AI Learning Path Generator", page_icon="🚀", layout="wide")
db.init_user_db()

# Configure Gemini API
try:
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
except (KeyError, TypeError):
    st.error("API Key not found. Please add your GEMINI_API_KEY to your Streamlit secrets.")
    model = None

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'username' not in st.session_state:
    st.session_state['username'] = ''
if 'admin_access' not in st.session_state:
    st.session_state['admin_access'] = False

# --- HELPER FUNCTIONS ---
def generate_prompt(topic, time_period, skill_level):
    """Creates a detailed, structured prompt for the AI model."""
    return f"""
        You are an expert instructional designer. Your task is to create a personalized, day-by-day learning path.
        **Topic:** "{topic}"
        **Total Time Frame:** "{time_period}"
        **Current Skill Level:** "{skill_level}"
        Generate a detailed plan that is broken down into a daily schedule. The output must be a clean JSON object and nothing else.
        The top-level JSON object must have a single key "dailyPlan". The value should be an array of day objects.
        Each day object must contain two keys: "day" (number) and "tasks" (an array).
        Each task object must have: "title" (string), "description" (string), and "exampleLink" (a real, high-quality URL).
    """

def safe_json_loads(json_string):
    """Safely loads a JSON string, handling potential errors and surrounding text."""
    try:
        start_index = json_string.find('{')
        end_index = json_string.rfind('}') + 1
        if start_index == -1 or end_index == 0: return None
        json_part = json_string[start_index:end_index]
        return json.loads(json_part)
    except (json.JSONDecodeError, TypeError):
        return None

# --- AUTHENTICATION & MAIN APP LOGIC ---
if not st.session_state['logged_in']:
    st.title("Welcome to the AI Learning Path Generator 🚀")
    choice = st.selectbox("Login / Signup", ["Login", "Signup"])
    if choice == "Login":
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")
            if submitted:
                if db.check_user(username, password):
                    st.session_state['logged_in'] = True
                    st.session_state['username'] = username
                    st.rerun()
                else:
                    st.error("Incorrect username or password.")
    else: # Signup
        with st.form("signup_form"):
            new_username = st.text_input("Choose a Username")
            new_password = st.text_input("Choose a Password", type="password")
            submitted = st.form_submit_button("Signup")
            if submitted:
                if db.add_user(new_username, new_password):
                    st.success("Account created! Please proceed to the Login tab.")
                else:
                    st.error("Username already exists.")
else:
    # --- SIDEBAR ---
    st.sidebar.title(f"Welcome, {st.session_state['username']}!")
    if st.sidebar.button("Logout"):
        st.session_state.clear()
        st.rerun()

    st.sidebar.markdown("---")
    with st.sidebar.expander("👑 Admin Dashboard"):
        admin_password = st.text_input("Enter Admin Password", type="password", key="admin_pass")
        if st.button("Access Dashboard"):
            if admin_password == os.environ.get("ADMIN_PASSWORD", ""):
                st.session_state['admin_access'] = True
            else:
                st.warning("Incorrect password.")
                st.session_state['admin_access'] = False

    # --- MAIN PAGE ---
    st.title("Generate a New Learning Path")
    with st.form("path_form"):
        topic_input = st.text_input("What do you want to learn?", placeholder="e.g., Python for Data Science")
        time_input = st.text_input("How much time do you have?", placeholder="e.g., 10 days")
        skill_level_input = st.selectbox("What is your current skill level?", ("Beginner", "Intermediate", "Advanced"))
        submitted = st.form_submit_button("Generate & Save Plan")

    if submitted and model:
        if not topic_input or not time_input:
            st.warning("Please fill in all the fields.")
        else:
            with st.spinner(f"Crafting your plan for '{topic_input}'..."):
                try:
                    prompt = generate_prompt(topic_input, time_input, skill_level_input)
                    response = model.generate_content(prompt)
                    db.save_path(st.session_state['username'], topic_input, response.text)
                    st.success("Your new path has been generated and saved!")
                    st.rerun()
                except Exception as e:
                    st.error(f"An error occurred during path generation: {e}")

    # --- DISPLAY SAVED PATHS & ADMIN VIEW ---
    st.markdown("---")
    if st.session_state.get('admin_access', False):
        st.header("👑 Admin View: All User Feedback")
        feedback_data = db.get_all_feedback_with_details()
        if feedback_data:
            df = pd.DataFrame(feedback_data, columns=['Username', 'Topic', 'Rating (1=👍, -1=👎)'])
            st.dataframe(df, use_container_width=True)
        else:
            st.write("No feedback has been submitted yet.")
    
    st.header("Your Saved Learning Paths")
    saved_paths = db.get_user_paths(st.session_state['username'])
    if not saved_paths:
        st.write("You haven't generated any paths yet.")
    else:
        for path_id, topic, path_data in saved_paths:
            with st.expander(f"Path for: {topic}"):
                parsed_path = safe_json_loads(path_data)
                if parsed_path:
                    daily_plan = parsed_path.get("dailyPlan", [])
                    for day_data in daily_plan:
                        st.subheader(f"🗓️ Day {day_data['day']}", divider="rainbow")
                        for task in daily_plan[0]['tasks']:
                            st.markdown(f"**{task['title']}**")
                            st.write(task['description'])
                            link = task.get('exampleLink', '')
                            if link: st.markdown(f"🔗 [{link}]({link})")
                            st.divider()
                else:
                    st.error("Could not parse or display this path.")
                
                # Feedback Section
                st.markdown("**Was this path helpful?**")
                cols = st.columns(2)
                with cols[0]:
                    if st.button("👍 Helpful", key=f"up_{path_id}", use_container_width=True):
                        db.add_feedback(path_id, st.session_state['username'], 1)
                        st.rerun()
                with cols[1]:
                    if st.button("👎 Not Helpful", key=f"down_{path_id}", use_container_width=True):
                        db.add_feedback(path_id, st.session_state['username'], -1)
                        st.rerun()
                
                current_feedback = db.get_feedback(path_id, st.session_state['username'])
                if current_feedback is not None:
                    feedback_text = "Helpful" if current_feedback == 1 else "Not Helpful"
                    st.info(f"You rated this path as: **{feedback_text}**")
