import streamlit as st
import google.generativeai as genai
import os
import json
from dotenv import load_dotenv
import database as db
import pandas as pd
import re
import plotly.graph_objects as go

# --- Initial Setup ---
load_dotenv()
st.set_page_config(page_title="Learning Path Generator", page_icon="🚀", layout="wide")
db.init_user_db()

# Configure Gemini API
try:
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
except (KeyError, TypeError):
    st.error("API Key not found. Please add your GEMINI_API_KEY to your Streamlit secrets.")
    model = None

# Initialize session state to prevent KeyErrors
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'username' not in st.session_state:
    st.session_state['username'] = ''
if 'admin_access' not in st.session_state:
    st.session_state['admin_access'] = False
if 'reset_stage' not in st.session_state:
    st.session_state['reset_stage'] = None

# --- HELPER FUNCTIONS ---
def is_password_strong(password):
    """Checks password strength: 8+ chars, 1+ number, 1+ special character."""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if not re.search(r"\d", password):
        return False, "Password must contain at least one number."
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "Password must contain at least one special character."
    return True, ""

def generate_prompt(topic, time_period, skill_level):
    """Creates a detailed, structured prompt for the AI model."""
    return f"""
        You are an expert instructional designer. Your task is to create a personalized, day-by-day learning path.
        **Topic:** "{topic}"
        **Total Time Frame:** "{time_period}"
        **Current Skill Level:** "{skill_level}"
        
        Generate a detailed plan that is broken down into a daily schedule. 
        It is critically important that the output be a clean JSON object and nothing else. Do not include any introductory text, apologies, or explanations.
        
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
    choice = st.selectbox("Login / Signup / Reset", ["Login", "Signup", "Forgot Password"])

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
    
    elif choice == "Signup":
        with st.form("signup_form"):
            new_username = st.text_input("Choose a Username")
            new_password = st.text_input("Choose a Password", type="password")
            st.info("Passwords must be 8+ characters and contain a number and a special character.")
            secret_question = st.selectbox("Choose a Security Question", 
                                           ["What was your first pet's name?", 
                                            "What city were you born in?", 
                                            "What is your favorite book?"])
            secret_answer = st.text_input("Your Answer (case-insensitive)")
            submitted = st.form_submit_button("Signup")
            if submitted:
                if db.user_exists(new_username):
                    st.error("Username already exists. Please choose another one.")
                else:
                    is_strong, message = is_password_strong(new_password)
                    if not is_strong:
                        st.error(message)
                    elif not secret_answer:
                        st.error("Please provide an answer to your secret question.")
                    else:
                        db.add_user(new_username, new_password, secret_question, secret_answer)
                        st.success("Account created successfully! Please proceed to the Login tab.")
    
    elif choice == "Forgot Password":
        st.subheader("Password Reset")
        if st.session_state.reset_stage is None:
            st.session_state.reset_stage = 1

        if st.session_state.reset_stage == 1:
            username_to_reset = st.text_input("Enter your username to begin")
            if st.button("Next"):
                question = db.get_secret_question(username_to_reset)
                if question:
                    st.session_state.username_to_reset = username_to_reset
                    st.session_state.secret_question = question
                    st.session_state.reset_stage = 2
                    st.rerun()
                else:
                    st.error("Username not found.")
        
        if st.session_state.reset_stage == 2:
            st.write(f"Security Question: **{st.session_state.secret_question}**")
            answer = st.text_input("Your Secret Answer", key="secret_answer_reset")
            if st.button("Verify Answer"):
                if db.check_secret_answer(st.session_state.username_to_reset, answer):
                    st.session_state.reset_stage = 3
                    st.rerun()
                else:
                    st.error("Incorrect answer.")

        if st.session_state.reset_stage == 3:
            st.write("Verification successful! Please set a new password.")
            new_password = st.text_input("New Password", type="password", key="new_pass")
            if st.button("Reset Password"):
                is_strong, message = is_password_strong(new_password)
                if not is_strong:
                    st.error(message)
                else:
                    db.reset_password(st.session_state.username_to_reset, new_password)
                    st.success("Password has been reset successfully! Please log in.")
                    for key in list(st.session_state.keys()):
                        if key.startswith('reset_') or key == 'username_to_reset' or key == 'secret_question':
                            del st.session_state[key]
                    st.rerun()

else: # Main application for logged-in users
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
            parsed_path = safe_json_loads(path_data)
            
            if parsed_path:
                with st.expander(f"Path for: {topic}"):
                    daily_plan = parsed_path.get("dailyPlan", [])
                    task_statuses = db.get_task_statuses_for_path(st.session_state['username'], path_id)
                    all_tasks = [f"day{day.get('day', 0)}-{task.get('title', '')}" for day in daily_plan for task in day.get('tasks', [])]
                    
                    if all_tasks:
                        completed_count = sum(task_statuses.get(task_id, 0) for task_id in all_tasks)
                        total_tasks = len(all_tasks)
                        progress_percent = (completed_count / total_tasks) * 100 if total_tasks > 0 else 0
                        
                        fig = go.Figure(go.Indicator(
                            mode = "gauge+number", value = completed_count,
                            domain = {'x': [0, 1], 'y': [0, 1]},
                            title = {'text': f"Tasks Completed"},
                            gauge = {'axis': {'range': [None, total_tasks]}, 'bar': {'color': "#28a745"},
                                     'steps' : [{'range': [0, total_tasks], 'color': "lightgray"}]}
                        ))
                        fig.update_layout(height=250, margin=dict(l=20, r=20, t=40, b=20))
                        st.plotly_chart(fig, use_container_width=True)
                        st.markdown("---")

                    for day_data in daily_plan:
                        st.subheader(f"🗓️ Day {day_data['day']}", divider="rainbow")
                        for task in day_data.get('tasks', []):
                            task_identifier = f"day{day_data.get('day', 0)}-{task.get('title', '')}"
                            is_completed = bool(task_statuses.get(task_identifier, 0))
                            st.checkbox(label=f"**{task.get('title', 'No Title')}**", value=is_completed, key=f"task_{path_id}_{task_identifier}",
                                        on_change=db.update_task_status, args=(st.session_state['username'], path_id, task_identifier, not is_completed))
                            st.write(task.get('description', 'No Description'))
                            link = task.get('exampleLink', '')
                            if link: st.markdown(f"🔗 [{link}]({link})")
                            st.divider()
                
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
            
            else: # This block runs if parsing fails, avoiding nested expanders
                st.error(f"Could not parse or display the path for: **{topic}**")
                with st.expander("Click to see the raw data that failed to parse"):
                    st.code(path_data)
