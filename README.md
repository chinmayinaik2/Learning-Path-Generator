
# AI-Powered Personalized Learning Platform 🚀

[](https://www.python.org/) [](https://streamlit.io) [](https://www.sqlite.org/index.html) [](https://ai.google.dev/)

A full-stack web application that generates personalized, day-by-day learning plans with secure user accounts, interactive progress tracking, and an admin dashboard.

-----

## Live Demo

** https://learning-path-generator-fc3shfpeonrlsk3fwety7y.streamlit.app/ **

-----

*The user dashboard displaying saved learning paths with progress charts.*

-----

## \#\# Features

This application has evolved from a simple generator into a feature-rich learning platform:

  * **🤖 AI-Powered Path Generation:** Integrates the **Google Gemini API** to generate high-quality, day-by-day learning plans for any topic.
  * **🔐 Secure User Authentication:**
      * Full user registration and login system.
      * Passwords securely hashed using **bcrypt**.
      * Password strength validation (length, numbers, special characters).
      * A multi-step "Forgot Password" flow using a secret question.
  * **🗃️ Database Integration:** Uses **SQLite** to persistently store all user data, saved learning paths, task progress, and user feedback.
  * **📊 Interactive Progress Tracking:**
      * Users can mark individual tasks as complete using interactive checkboxes.
      * Progress is saved instantly and visualized with dynamic **Plotly** gauge charts for each learning plan.
  * **🗓️ Extensible Long-Term Plans:** Intelligently generates long-term plans (e.g., 90+ days) in manageable 7-day chunks, which users can extend on demand.
  * **👍 User Feedback System:** Allows users to rate each generated path as helpful or not helpful.
  * **👑 Admin Dashboard:** A password-protected admin view to see all user feedback in one place.

-----

## \#\# Technology Stack

  * **Core Framework:** [Python](https://www.python.org/), [Streamlit](https://streamlit.io/)
  * **Database:** [SQLite](https://www.sqlite.org/index.html)
  * **AI Model:** [Google Gemini API](https://ai.google.dev/)
  * **Key Libraries:**
      * `bcrypt` for password hashing
      * `pandas` for data display in the admin dashboard
      * `plotly` for data visualization and progress charts

-----

## \#\# Setup and Local Installation

Follow these steps to run the project on your local machine.

### \#\#\# 1. Prerequisites

  * Python 3.9 or higher
  * A Google Gemini API Key from [Google AI Studio](https://aistudio.google.com).

### \#\#\# 2. Clone the Repository

```bash
git clone https://github.com/your-username/your-repository-name.git
cd your-repository-name
```

### \#\#\# 3. Create a Virtual Environment

```bash
# For macOS/Linux
python3 -m venv venv
source venv/bin/activate

# For Windows
python -m venv venv
.\venv\Scripts\activate
```

### \#\#\# 4. Install Dependencies

Ensure your `requirements.txt` file contains the following, then run the install command.

**`requirements.txt`:**

```txt
streamlit
google-generativeai
python-dotenv
bcrypt
pandas
plotly
```

**Installation Command:**

```bash
pip install -r requirements.txt
```

### \#\#\# 5. Set Up Environment Variables

Create a file named `.env` in the root of your project directory and add your secret keys:

```
GEMINI_API_KEY="YOUR_API_KEY_HERE"
ADMIN_PASSWORD="YOUR_CHOSEN_ADMIN_PASSWORD"
```

