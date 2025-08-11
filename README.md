

# AI Personalized Learning Path Generator 🚀

[](https://www.python.org/) [](https://streamlit.io) [](https://ai.google.dev/)

An interactive web application that generates personalized, day-by-day learning schedules for any skill based on user-defined goals, time frames, and skill levels.

## Live Demo

**https://learning-path-generator-fc3shfpeonrlsk3fwety7y.streamlit.app/**

<img width="1867" height="692" alt="image" src="https://github.com/user-attachments/assets/a0ed105d-da7b-40cc-b58a-261381d572eb" />
<img width="1774" height="843" alt="image" src="https://github.com/user-attachments/assets/f29b3f97-63d9-4ba9-9320-d38721a1b7aa" />


## The Problem

Learning a new skill is often overwhelming due to the vast amount of information available. It's difficult to know where to start, what to learn next, or how to structure your studies over a specific period. This tool solves that problem by providing a clear, actionable, day-by-day plan.

## Features

  * **🤖 AI-Powered:** Leverages the **Google Gemini API** to generate high-quality, relevant learning content.
  * **🗓️ Daily Breakdown:** Structures the learning path into a clear, day-by-day schedule based on the user's total time commitment.
  * **🔗 Resource Links:** Includes direct, clickable links to relevant tutorials, articles, and documentation for each learning task.
  * **🎯 Fully Customizable:** Tailors the plan based on the topic, time frame, and the user's self-assessed skill level (Beginner, Intermediate, Advanced).
  * **🌐 Interactive Web UI:** Built with **Streamlit** for a simple, intuitive, and responsive user experience.

-----

## Technology Stack

  * **Backend & Frontend:** [Python](https://www.python.org/), [Streamlit](https://streamlit.io/)
  * **AI Model:** [Google Gemini API](https://ai.google.dev/)
  * **Data Handling:** JSON
  * **Dependencies:** `google-generativeai`, `python-dotenv`

## Setup and Local Installation

Follow these steps to run the project on your local machine.

### 1\. Prerequisites

  * Python 3.9 or higher
  * A Google Gemini API Key. You can get one for free from [Google AI Studio](https://aistudio.google.com).

### 2\. Clone the Repository

```bash
git clone https://github.com/your-username/your-repository-name.git
cd your-repository-name
```

### 3\. Create a Virtual Environment

It's a good practice to create a virtual environment to manage dependencies.

```bash
# For macOS/Linux
python3 -m venv venv
source venv/bin/activate

# For Windows
python -m venv venv
.\venv\Scripts\activate
```

### 4\. Install Dependencies

Create a `requirements.txt` file with the following content:

```txt
streamlit
google-generativeai
python-dotenv
```

Then, install the packages from this file:

```bash
pip install -r requirements.txt
```

### 5\. Set Up Environment Variables

Create a file named `.env` in the root of your project directory and add your API key:

```
GEMINI_API_KEY="YOUR_API_KEY_HERE"
```

### 6\. Run the Application

```bash
streamlit run app.py
```

Open your web browser and navigate to `http://localhost:8501`.

-----

## How It Works

1.  **User Input:** The Streamlit interface collects the user's desired topic, time frame, and skill level.
2.  **Prompt Engineering:** The application constructs a detailed, structured prompt, instructing the Gemini LLM to act as an expert instructional designer and return a response in a specific nested JSON format.
3.  **API Call:** The prompt is sent to the Gemini API.
4.  **JSON Parsing:** The AI's response is received, cleaned of any extraneous text, and parsed from a JSON string into a Python dictionary.
5.  **Dynamic Display:** The application iterates through the structured data with nested loops to dynamically render the day-by-day plan with tasks and links on the user interface.

-----

## Future Improvements

  * [ ] **Progress Tracking:** Add checkboxes for each task to allow users to mark them as complete.
  * [ ] **User Feedback:** Implement a thumbs-up/down system to rate the quality of generated paths.
  * [ ] **Export Functionality:** Allow users to download their learning path as a PDF or Markdown file.
  * [ ] **Caching:** Implement a caching mechanism to store results for common queries, reducing API costs and improving response time.

-----

## License

This project is licensed under the MIT License - see the [LICENSE](https://www.google.com/search?q=LICENSE) file for details.
