import streamlit as st
import google.generativeai as genai
import os
import json


# Load environment variables from .env file


# --- Page Configuration ---
st.set_page_config(
    page_title="AI Learning Path Generator",
    page_icon="🚀",
    layout="wide",
)

# --- Google Gemini Configuration ---
try:
    genai.configure(api_key="AIzaSyBhXPPxYGc7OzhUV060IsYHBApcWoEF1aY")
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
except Exception as e:
    st.error(f"Error configuring the AI model: {e}")
    st.error("Please make sure your GEMINI_API_KEY is set correctly in the .env file.")
    model = None

# --- Prompt Engineering Function ---
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

# --- App UI and Logic ---
st.title("AI Day-by-Day Learning Path Generator 🚀")
st.write("Enter what you want to learn, your time commitment, and your current skill level to get a customized learning plan.")

with st.form("path_form"):
    topic_input = st.text_input("What do you want to learn?", placeholder="e.g., ReactJS from scratch")
    time_input = st.text_input("How much time do you have?", placeholder="e.g., 10 days, 2 weeks, 1 month")
    skill_level_input = st.selectbox(
        "What is your current skill level?",
        ("Beginner", "Intermediate", "Advanced")
    )
    submitted = st.form_submit_button("Generate My Daily Plan")

if submitted:
    if not model:
        st.stop()
        
    if not topic_input or not time_input:
        st.warning("Please fill in all the fields before generating a path.")
    else:
        with st.spinner(f"Crafting your day-by-day plan for '{topic_input}'... This might take a moment."):
            try:
                # 1. Create the prompt
                prompt = generate_prompt(topic_input, time_input, skill_level_input)

                # 2. Call the AI model
                response = model.generate_content(prompt)
                
                # 3. Clean and parse the response
                response_text = response.text.replace('```json', '').replace('```', '').strip()
                parsed_response = json.loads(response_text)
                daily_plan = parsed_response.get("dailyPlan", [])

                # 4. Display the path
                if daily_plan:
                    st.success("Your personalized learning path is ready!")
                    st.info("💡 **Disclaimer:** The links are AI-generated. Please verify the content, as they may occasionally be outdated or incorrect.")

                    for day_data in daily_plan:
                        st.subheader(f"🗓️ Day {day_data['day']}", anchor=False, divider="rainbow")
                        
                        for task in day_data['tasks']:
                            st.markdown(f"**{task['title']}**")
                            st.write(task['description'])
                            link = task.get('exampleLink', '')
                            if link:
                                st.markdown(f"🔗 [{link}]({link})")
                            st.divider()
                else:
                    st.error("The AI couldn't generate a path for this topic. Please try rephrasing your request.")

            except json.JSONDecodeError:
                st.error("There was an issue decoding the AI's response. It might not be valid JSON. Please try again.")
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")