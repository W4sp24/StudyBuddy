
---

# PDF Study Buddy

PDF Study Buddy is a Flask-based web application designed to assist users in transforming PDF documents into structured study materials. The application processes uploaded PDFs to extract text and utilizes the Gemini AI API to generate comprehensive study guides and quizzes based on the document content. Generated materials are available for download in PDF format.

---

## Features

* **PDF Upload:** Provides a user interface for securely uploading PDF files for processing.
* **Text Extraction:** Processes uploaded PDF documents to extract textual content, which serves as the basis for AI analysis.
* **AI-Powered Study Guide Generation:** Integrates with the Gemini AI API to analyze extracted text and generate a detailed study guide, including summaries, key concepts, and important facts.
* **AI-Powered Quiz Generation:** Utilizes the Gemini AI API to create multiple-choice quizzes based on the content and key points identified in the processed PDF.
* **Content Download:** Allows users to download the generated study guide and quiz documents in PDF format.

---
Okay, here is the directory structure for your StudyBuddy project formatted clearly, suitable for your README.md or other documentation.

## Project Structure as of 21/4/2025
StudyBuddy/
├── app.py                   # Main Flask application entry point
├── utils/                     # Directory for utility functions
│   ├── pdf_processor.py     # Handles extraction of text content from PDFs
│   └── gemini_client.py     # Manages communication and requests with the Gemini AI API
├── templates/                 # Directory for HTML templates
│   ├── base.html            # Base template for common structure (header, footer, etc.)
│   ├── index.html           # Template for the application's home or upload page
│   ├── study_guide.html     # Template for displaying the generated study guide
│   └── quiz.html            # Template for displaying the generated quiz
├── static/                    # Directory for static assets (CSS, JS, images)
│   ├── css/                 # Subdirectory for CSS stylesheets
│   └── js/                  # Subdirectory for JavaScript files
├── .env                       # File to store environment variables (e.g., API keys, configuration)
├── requirements.txt           # Lists the project's Python dependencies
└── README.md                  # Project documentation file (this file)


---

## Installation

### Prerequisites
- Python 3.8 or higher
- Pip (Python package manager)

### Steps
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-username/pdf-study-buddy.git
   cd pdf-study-buddy

2. Install Dependencies: Install the required Python packages: pip install -r requirements.txt
3. Set Up Environment Variables: Create a .env file in the root directory and add your Gemini API key: GEMINI_API_KEY=your-gemini-api-key   
4. Run the Application: Start the Flask development server: python [app.py](http://_vscodecontentref_/3)
5 .Access the Application: Open your browser and navigate to: http://127.0.0.1:5000

   

