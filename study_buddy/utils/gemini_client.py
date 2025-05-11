import os
import json
import google.generativeai as genai
import logging
from dotenv import load_dotenv  # Add this import

# Load environment variables from .env file
load_dotenv()  # Add this line

logger = logging.getLogger(__name__)

# Initialize the Gemini API
API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    logger.warning("GEMINI_API_KEY not found in environment variables")

genai.configure(api_key=API_KEY)

def get_gemini_model():
    """
    Get the Gemini model for text generation
    
    Returns:
        Model: Gemini model instance
    """
    try:
        # Use the Gemini model for text generation
        model = genai.GenerativeModel('gemini-2.0-flash')
        return model
    except Exception as e:
        logger.error(f"Error initializing Gemini model: {str(e)}")
        raise Exception(f"Failed to initialize Gemini model: {str(e)}")

def generate_study_guide(text):
    """
    Generate a study guide from the given text using Gemini API
    
    Args:
        text (str): Text extracted from the PDF
        
    Returns:
        str: Generated study guide in Markdown format
    """
    try:
        model = get_gemini_model()
        
        # Truncate text if too long (Gemini has input token limits)
        if len(text) > 30000:  # Approximate limit to stay within Gemini's token count
            text = text[:30000]
            logger.warning("Text truncated to fit within Gemini's token limit")
        
        prompt = f"""
        Goal: Design and generate a comprehensive study reviewer on a specified topic.
        
        Topic/Content{text}
        
        Target Audience Level: Beginner/Student/College Level

        Content Requirements:

        - Define Key Terms: Clearly define all essential terms and concepts related to the topic. Define the terms exactly as they are used in the text.
        - Provide Examples: Include short, relevant examples to illustrate concepts.
        - Explain Core Principles: Detail the fundamental ideas and mechanisms of the topic.
        - Include Comparisons/Contrasts (if applicable): Use tables or bullet points to compare related concepts.
        - Code/Syntax Examples (if applicable): Provide code snippets or syntax examples using proper formatting and highlighting if the topic involves programming or specific syntax.
        - Real-World Applications (if applicable): Briefly mention how the topic is used in practice.
        - Compile a Glossary: Create a dedicated section at the very end listing key terms and their definitions.

        Formatting Guidelines:

        - Use Clear Headings: Structure the reviewer with main headings and subheadings (e.g., using Markdown #, ##, ###).
        - Use Bullet Points: Ensure liberal use of bullet points (-) for lists, facts, definitions, and key points within sections.
        -Use Tables: Create tables for comparisons or structured information when appropriate, using standard Markdown syntax for proper rendering.
        - Format Code: Use code blocks (```language) for any code examples.
        - Use LaTeX (Optional): Use LaTeX formatting ($...$ or $$...$$) ONLY for mathematical or scientific notation where appropriate, NOT for regular text.

        Style & Tone:

        - Concise: Be direct and to the point, avoiding unnecessary jargon unless defined.
        - Educational: Focus on explaining concepts clearly for the specified audience level.
        - Friendly & Academic: Maintain a helpful yet formal and knowledgeable tone.
        - Structured: Organize the information logically, like a study guide.

        Output Format:

        - Provide the output cleanly formatted in Markdown for easy rendering into HTML.
        - Make sure every component is properly rendered in Markdown.
        - Avoid conversational filler at the beginning or end; go straight into the reviewer content.

        Request: Generate the comprehensive reviewer based on the topic, level, content, formatting, and style guidelines provided above.
        """
        
        response = model.generate_content(prompt)
        study_guide = response.text  # Gemini outputs Markdown-like content
        
        return study_guide
    
    except Exception as e:
        logger.error(f"Error generating study guide: {str(e)}")
        raise Exception(f"Failed to generate study guide: {str(e)}")

def generate_quiz(text, num_questions=5):
    """
    Generate a quiz from the given text using Gemini API
    
    Args:
        text (str): Text extracted from the PDF
        num_questions (int): Number of questions to generate
        
    Returns:
        str: Generated quiz in JSON format
    """
    try:
        model = get_gemini_model()
        
        # Truncate text if too long (Gemini has input token limits)
        if len(text) > 30000:  # Approximate limit to stay within Gemini's token count
            text = text[:30000]
            logger.warning("Text truncated to fit within Gemini's token limit")
        
        prompt = f"""
        Create a multiple-choice quiz with {num_questions} questions based on the following content:
        
        {text}
        
        Return the quiz in the following JSON format:
        [
            {{
                "question": "Question text here",
                "options": ["Option A", "Option B", "Option C", "Option D"],
                "answer": "The correct option (verbatim text of the answer)"
            }},
            // more questions...
        ]
        
        Make sure questions test key concepts and important information from the content.
        Ensure each question has 4 options and exactly one correct answer.
        The questions should vary in difficulty level.
        """
        
        response = model.generate_content(prompt)
        quiz_text = response.text
        
        # Extract the JSON from the response
        # Sometimes the model includes markdown code blocks or other text
        if "```json" in quiz_text:
            quiz_text = quiz_text.split("```json")[1].split("```")[0].strip()
        elif "```" in quiz_text:
            quiz_text = quiz_text.split("```")[1].split("```")[0].strip()
        
        # Validate JSON format
        try:
            quiz_data = json.loads(quiz_text)
            # Ensure it's a valid quiz format
            for question in quiz_data:
                if not all(key in question for key in ["question", "options", "answer"]):
                    raise ValueError("Invalid quiz format")
            return quiz_text
        except json.JSONDecodeError:
            logger.error("Failed to parse JSON from Gemini response")
            raise Exception("Failed to generate a valid quiz. Please try again.")
    
    except Exception as e:
        logger.error(f"Error generating quiz: {str(e)}")
        raise Exception(f"Failed to generate quiz: {str(e)}")