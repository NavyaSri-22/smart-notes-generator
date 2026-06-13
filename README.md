# Smart Notes Engine

## Overview

Smart Notes Engine is an AI-powered study assistant built using Streamlit and Groq's Llama 3 models. It helps students, educators, and self-learners convert different types of learning materials into organized study notes and practice questions within seconds.

Instead of manually creating notes from lengthy documents, videos, or lectures, users can simply upload their content and let the application generate structured notes in their preferred format.

---

## What This Project Can Do

### Generate Notes from Multiple Sources

The application accepts study material from different sources, including:

* Plain text
* PDF documents
* Word (.docx) files
* Voice recordings
* YouTube videos

This flexibility allows users to learn from almost any type of educational content.

### Extract Content from YouTube Videos

Users can paste a YouTube video link, and the application automatically retrieves the video's transcript (if available) and converts it into useful study notes.

### Convert Voice into Notes

The built-in voice recording feature allows users to speak directly into the application. The recorded speech is converted into text and can then be transformed into structured notes.

### Multiple Note Formats

Users can choose how they want their notes to be presented:

* **Bullet Points** – for quick revision
* **Detailed Paragraphs** – for in-depth understanding
* **Flashcards** – for active recall and exam preparation

### Practice Question Generator

To support exam preparation, the application automatically generates practice questions based on the uploaded content. Users can select the number of questions they want, making revision more interactive and effective.

### Notebook Management

Generated notes are saved within the session, allowing users to:

* View previous notes
* Rename notebooks
* Reopen saved content
* Delete unwanted notes

This creates a simple workspace for managing study materials.

---

## How to Use the Application

### Step 1: Upload Your Study Material

Choose any of the available input options:

* Paste text directly
* Upload a PDF file
* Upload a Word document
* Record your voice
* Paste a YouTube link

### Step 2: Select Your Preferred Format

Choose how you want the generated notes to appear:

* Bullet Points
* Detailed Paragraphs
* Flashcards

You can also specify how many practice questions should be created.

### Step 3: Generate and Review

Click the **Generate Exam-Ready Notes** button.

The application will:

* Analyze your content
* Generate structured notes
* Create practice questions
* Display everything in editable sections

You can further modify the generated content based on your learning needs.

---

## Installation Guide

### Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/smart-notes-engine.git
cd smart-notes-engine
```

### Install Required Libraries

Create a `requirements.txt` file and add:

```txt
streamlit
openai
python-docx
pypdf
youtube-transcript-api
streamlit-mic-recorder
pandas
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

### Configure Your Groq API Key

Get your API key from the Groq Console.

For local development:

```python
LOCAL_GROQ_KEY = "your_api_key_here"
```

For Streamlit Cloud deployment, store it in the Secrets section:

```toml
GROQ_API_KEY = "your_api_key_here"
```

### Run the Application

```bash
streamlit run app.py
```

---

## Technologies Used

* Python
* Streamlit
* Groq API
* Llama 3 Models
* PyPDF
* Python-Docx
* Pandas
* YouTube Transcript API
* Streamlit Mic Recorder

---

## Error Handling and Reliability

The application includes several mechanisms to improve reliability:

* Automatic fallback to alternative AI models if the primary model is unavailable.
* Safe processing of transcripts and uploaded files.
* Error handling for invalid YouTube links or missing captions.
* Structured output generation to ensure notes and questions are displayed correctly.

These features help provide a smooth user experience even when unexpected issues occur.

---

## Future Improvements

Some planned enhancements include:

* Multi-language support
* PDF export for generated notes
* Dark mode interface
* Cloud notebook storage
* AI-generated mind maps
* Personalized learning recommendations

---

## Conclusion

Smart Notes Engine simplifies the note-taking process by combining artificial intelligence with an easy-to-use interface. Whether you're studying for exams, reviewing lecture materials, or learning from online videos, the platform helps you create organized notes and practice questions quickly and efficiently.
