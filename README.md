
-----

# 🎓 Conversational RAG AI Tutor

This project is a fully functional AI tutor application that leverages a Retrieval-Augmented Generation (RAG) pipeline to answer questions based on a provided PDF document. The application features a conversational interface with voice input, text-to-speech output, and an animated emoji mascot that changes expression based on the AI's state.

The application is built with a **FastAPI backend** for the AI logic and a **Streamlit frontend** for the user interface.

## ✨ Features

  * **RAG Pipeline:** The AI's knowledge is sourced directly from a PDF document (`python Machine Learning .pdf`).
  * **Conversational Memory:** The AI remembers the context of the conversation for follow-up questions.
  * **Voice-to-Text Input:** Users can speak their questions directly into the application.
  * **Text-to-Speech Output:** The AI's answers are spoken aloud automatically.
  * **Interactive Frontend:** A user-friendly chat interface built with Streamlit.
  * **Dynamic Mascot:** An emoji mascot changes to reflect the AI's current state (thinking, explaining, etc.).
  * **Containerized:** A `Dockerfile` is included for easy setup and deployment.

## 🏛️ Architecture

The application consists of two main components running in a single container:

1.  **FastAPI Backend (`main.py`):**

      * Handles the RAG pipeline using **LangChain**.
      * Loads a PDF, splits it into chunks, and creates vector embeddings using **Google Gemini Embeddings**.
      * Stores embeddings in a **ChromaDB** vector store.
      * Uses **Google Gemini 1.5 Flash** to generate responses based on user queries and retrieved context.
      * Manages conversational history for each user session.
      * Exposes a `/chat` endpoint for the frontend to communicate with.

2.  **Streamlit Frontend (`frontend.py`):**

      * Provides the web-based user interface.
      * Captures user audio via the microphone using `speech_recognition`.
      * Allows users to edit the transcribed text before sending it.
      * Sends user queries to the FastAPI backend.
      * Displays the chat history and the AI's response.
      * Converts the AI's text response to audio using `gTTS` (Google Text-to-Speech).

## 🚀 Getting Started

You can run this application in two ways: directly on your local machine or using Docker.

### Prerequisites

  * **Python 3.9+**
  * **Docker** (for the Docker-based setup)
  * A **Google API Key** with the "Generative Language API" enabled. You can get one from the [Google AI Studio](https://aistudio.google.com/app/apikey).

-----

## 🔧 Method 1: Local Setup (Without Docker)

Follow these steps to run the application directly on your machine.

### 1\. Clone the Repository

```bash
git clone <your-repository-url>
cd <your-repository-name>
```

### 2\. Set Up a Virtual Environment

It's recommended to use a virtual environment to manage dependencies.

```bash
# Create a virtual environment
python -m venv venv

# Activate it
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

### 3\. Install Dependencies

Install all the required Python packages from the `requirements.txt` file.

```bash
pip install -r requirements.txt
```

### 4\. Configure Environment Variables

Create a file named `.env` in the root directory of the project. This file will store your Google API key.

```plaintext
# .env file
GOOGLE_API_KEY="YOUR_GOOGLE_API_KEY_HERE"
```

Replace `YOUR_GOOGLE_API_KEY_HERE` with your actual key.

### 5\. Add Your Knowledge Source

Place the PDF file you want the AI to learn from in the root directory. The backend code is currently configured to look for a file named `python Machine Learning .pdf`.

```
/
|-- main.py
|-- frontend.py
|-- requirements.txt
|-- .env
|-- python Machine Learning .pdf  <-- PLACE YOUR PDF HERE
|-- ... (other files)
```

### 6\. Run the Application

You need to run the backend and frontend servers in two separate terminal windows.

**Terminal 1: Start the FastAPI Backend**

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

The backend is now running at `http://localhost:8000`.

**Terminal 2: Start the Streamlit Frontend**

```bash
streamlit run frontend.py
```

The application will open in your browser, usually at `http://localhost:8501`.

-----

## 🐳 Method 2: Running with Docker (Recommended)

This method simplifies the setup by running the entire application within a single Docker container.

### 1\. Clone the Repository & Prepare Files

Clone the repository and ensure your `.env` file and PDF document are in the root directory, as described in steps 1, 4, and 5 of the local setup. The Docker build process needs these files.

```
/
|-- Dockerfile
|-- main.py
|-- frontend.py
|-- requirements.txt
|-- .env                         <-- CREATE THIS FILE
|-- python Machine Learning .pdf   <-- ADD YOUR PDF HERE
|-- ...
```

### 2\. Build the Docker Image

From the root directory of the project, run the following command to build the Docker image.

```bash
docker build -t ai-tutor .
```

### 3\. Run the Docker Container

Once the image is built, run it. This command will start the container, mapping the necessary ports from the container to your local machine.

```bash
docker run -p 8000:8000 -p 8501:8501 ai-tutor
```

  * `-p 8000:8000` maps the FastAPI backend port.
  * `-p 8501:8501` maps the Streamlit frontend port.

### 4\. Access the Application

Open your web browser and navigate to:

**`http://localhost:8501`**

You can now interact with your AI tutor\!