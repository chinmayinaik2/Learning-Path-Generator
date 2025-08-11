import streamlit as st
import google.generativeai as genai
import os
import json
from dotenv import load_dotenv
import database as db # Import our database module

# --- Initial Setup ---
load_dotenv()
st.set_page_config(page_title="AI Learning Path Generator", page_icon="🚀", layout="wide")

# Initialize the database (creates tables if they don't exist)
db.init_user_db()

# Configure Gemini API
# This block attempts to configure the API and will show an error if the key is missing
try:
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
except (KeyError, TypeError):
    st.error("API Key not found. Please add your GEMINI_API_KEY to your Streamlit secrets.")
    model = None

# Initialize session state for login status
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'username' not in st.session_state:
    st.session_state['username'] = ''

# --- HELPER FUNCTIONS ---

def generate_prompt(topic, time_period, skill_level):
    """Creates a detailed, structured prompt for the AI model."""
    return f"""
        You are an expert instructional designer. Your task is to create a personalized, day-by-day learning path.

        **Topic:** "{topic}"
        **Total Time Frame:** "{time_period}"
        **Current Skill Level:** "{skill_level}"

        Generate a detailed plan that is broken down into a daily schedule based on the total time frame provided.
        The output must be a clean JSON object and nothing else.
        The top-level JSON object must have a single key "dailyPlan".
        The value of "dailyPlan" should be an array of day objects.
        Each day object in the array must contain two keys:
        1. "day" (number): The day number in the schedule.
        2. "tasks" (array): A list of task objects for that day.

        Each task object in the "tasks" array must have the following three keys:
        - "title" (string): A concise, descriptive title for the task.
        - "description" (string): A one or two-sentence explanation of what to do for this task.
        - "exampleLink" (string): A single, high-quality, real URL to a helpful resource for this task.

        Ensure the entire learning path realistically fits within the user's specified time frame.
    """

def safe_json_loads(json_string):
    """
    Safely loads a JSON string, even if it's embedded in other text
    or wrapped in markdown code fences.
    """
    try:
        # Find the start and end of the JSON object
        start_index = json_string.find('{')
        end_index = json_string.rfind('}') + 1

        if start_index == -1 or end_index == 0:
            return None # No JSON object found

        # Extract the potential JSON string
        json_part = json_string[start_index:end_index]
        return json.loads(json_part)
    except (json.JSONDecodeError, TypeError):
        return None # Failed to parse

# --- AUTHENTICATION & MAIN APP LOGIC ---

# If user is not logged in, show the login/signup page
if not st.session_state['logged_in']:
    st.title("Welcome to the AI Learning Path Generator 🚀")
    choice = st.selectbox("Login / Signup", ["Login", "Signup"])

    if choice == "Login":
        st.subheader("Login")
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
        st.subheader("Create a New Account")
        with st.form("signup_form"):
            new_username = st.text_input("Choose a Username")
            new_password = st.text_input("Choose a Password", type="password")
            submitted = st.form_submit_button("Signup")
            if submitted:
                if db.add_user(new_username, new_password):
                    st.success("Account created! Please proceed to the Login tab.")
                else:
                    st.error("Username already exists.")

# If user IS logged in, show the main application
else:
    st.sidebar.title(f"Welcome, {st.session_state['username']}!")
    if st.sidebar.button("Logout"):
        st.session_state['logged_in'] = False
        st.session_state['username'] = ''
        st.rerun()

    st.title("Generate a New Learning Path")

    with st.form("path_form"):
        topic_input = st.text_input("What do you want to learn?", placeholder="e.g., ReactJS from scratch")
        time_input = st.text_input("How much time do you have?", placeholder="e.g., 10 days, 2 weeks")
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
                    st.success("Your path has been generated and saved!")
                    st.rerun()

                except Exception as e:
                    st.error(f"An error occurred during path generation: {e}")

    st.markdown("---")
    st.header("Your Saved Learning Paths")
    saved_paths = db.get_user_paths(st.session_state['username'])

    if not saved_paths:
        st.write("You haven't generated any paths yet. Use the form above to create one!")
    else:
        for path_id, topic, path_data in saved_paths:
            with st.expander(f"Path for: {topic}"):
                parsed_path = safe_json_loads(path_data)
                
                if parsed_path:
                    daily_plan = parsed_path.get("dailyPlan", [])
                    for day_data in daily_plan:
                        st.subheader(f"🗓️ Day {day_data['day']}", divider="rainbow")
                        for task in day_data['tasks']:
                            st.markdown(f"**{task['title']}**")
                            st.write(task['description'])
                            link = task.get('exampleLink', '')
                            if link:
                                st.markdown(f"🔗 [{link}]({link})")
                            st.divider()
                else:
                    st.error("Could not parse or display this path. The saved data might be corrupted.")

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
