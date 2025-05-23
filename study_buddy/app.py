import logging
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file
from werkzeug.utils import secure_filename
import uuid
import tempfile
import json
from .utils.pdf_processor import extract_text_from_pdf
from .utils.gemini_client import generate_study_guide, generate_quiz
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch
from reportlab.lib import colors
from flask_session import Session
import tempfile
import os
import markdown  # Add this import

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default-secret-key-for-development")

# Configure Flask-Session
app.config['SESSION_TYPE'] = 'filesystem'  # Store sessions in the filesystem
app.config['SESSION_FILE_DIR'] = tempfile.mkdtemp()  # Temporary directory for session files
app.config['SESSION_PERMANENT'] = False  # Sessions are not permanent
app.config['SESSION_USE_SIGNER'] = True  # Sign session cookies for security

# Initialize Flask-Session
Session(app)

# Create temporary directories to store uploaded PDFs and generated content
UPLOAD_FOLDER = tempfile.mkdtemp()
OUTPUT_FOLDER = tempfile.mkdtemp()
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limit file size to 16MB

# Allowed file extensions
ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    # Check if the post request has the file part
    if 'pdf_file' not in request.files:
        flash('No file part', 'danger')
        return redirect(url_for('index'))
    
    file = request.files['pdf_file']
    
    # If user does not select file, browser also
    # submit an empty part without filename
    if file.filename == '':
        flash('No selected file', 'danger')
        return redirect(url_for('index'))
    
    if file and allowed_file(file.filename):
        # Generate a unique filename to avoid collisions
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(filepath)
        
        # Extract text from PDF
        try:
            extracted_text = extract_text_from_pdf(filepath)
            if not extracted_text:
                flash('Could not extract text from PDF. Please try another file.', 'danger')
                return redirect(url_for('index'))
            
            # Store the text and file path in session
            session['extracted_text'] = extracted_text
            session['pdf_filename'] = filename
            
            flash('PDF uploaded and processed successfully!', 'success')
            return redirect(url_for('index'))
        
        except Exception as e:
            logger.error(f"Error processing PDF: {str(e)}")
            flash(f'Error processing PDF: {str(e)}', 'danger')
            return redirect(url_for('index'))
    else:
        flash('Invalid file type. Please upload a PDF file.', 'danger')
        return redirect(url_for('index'))

@app.route('/generate_study_guide', methods=['POST'])
def create_study_guide():
    extracted_text = session.get('extracted_text')
    
    if not extracted_text:
        flash('No PDF text found. Please upload a PDF first.', 'danger')
        return redirect(url_for('index'))
    
    try:
        # Generate study guide using Gemini API
        study_guide_markdown = generate_study_guide(extracted_text)
        
        # Generate a unique ID for this study guide
        study_guide_id = str(uuid.uuid4())
        
        # Save the study guide to a file instead of the session
        study_guide_file = os.path.join(app.config['OUTPUT_FOLDER'], f"{study_guide_id}_study_guide.md")
        with open(study_guide_file, 'w', encoding='utf-8') as f:  # Specify UTF-8 encoding
            f.write(study_guide_markdown)
        
        # Convert Markdown to HTML with the tables extension
        study_guide_html = markdown.markdown(study_guide_markdown, extensions=['tables'])
        
        # Store only the ID in the session
        session['study_guide_id'] = study_guide_id
        
        # Pass the rendered HTML to the template
        return render_template('study_guide.html', study_guide=study_guide_html, pdf_filename=session.get('pdf_filename'))
    
    except Exception as e:
        logger.error(f"Error generating study guide: {str(e)}")
        flash(f'Error generating study guide: {str(e)}', 'danger')
        return redirect(url_for('index'))

@app.route('/generate_quiz', methods=['POST'])
def create_quiz():
    extracted_text = session.get('extracted_text')
    
    if not extracted_text:
        flash('No PDF text found. Please upload a PDF first.', 'danger')
        return redirect(url_for('index'))
    
    try:
        # Get number of questions from form
        num_questions = int(request.form.get('num_questions', 5))
        
        # Generate quiz using Gemini API
        quiz = generate_quiz(extracted_text, num_questions)
        
        # Parse the JSON string into a Python object
        quiz_data = json.loads(quiz)
        
        # Convert quiz JSON into Markdown format
        markdown_content = ""
        for i, question in enumerate(quiz_data, 1):
            markdown_content += f"### Question {i}: {question['question']}\n"
            for j, option in enumerate(question['options'], 1):
                markdown_content += f"- {option}\n"
            markdown_content += f"**Answer:** {question['answer']}\n\n"
        
        # Convert Markdown to HTML with the tables extension
        html_content = markdown.markdown(markdown_content, extensions=['tables'])
        
        return render_template('quiz.html', quiz_html=html_content, pdf_filename=session.get('pdf_filename'))
    
    except Exception as e:
        logger.error(f"Error generating quiz: {str(e)}")
        flash(f'Error generating quiz: {str(e)}', 'danger')
        return redirect(url_for('index'))

@app.route('/download_study_guide')
def download_study_guide():
    study_guide_id = session.get('study_guide_id')
    
    if not study_guide_id:
        flash('No study guide found. Please generate a study guide first.', 'danger')
        return redirect(url_for('index'))
    
    # Get the study guide file path
    study_guide_file = os.path.join(app.config['OUTPUT_FOLDER'], f"{study_guide_id}_study_guide.md")
    
    # Check if the file exists
    if not os.path.exists(study_guide_file):
        flash('Study guide file not found. Please generate a new study guide.', 'danger')
        return redirect(url_for('index'))
    
    # Read the original study guide
    with open(study_guide_file, 'r', encoding='utf-8') as source:
        study_guide_markdown = source.read()
    
    # Convert Markdown to HTML with the tables extension
    study_guide_html = markdown.markdown(study_guide_markdown, extensions=['tables'])
    
    # Create a PDF file
    pdf_filename = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf').name
    
    # Set up the PDF document
    doc = SimpleDocTemplate(
        pdf_filename,
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )
    
    # Define styles
    styles = getSampleStyleSheet()
    title_style = styles["Heading1"]
    title_style.alignment = 1  # Center alignment
    
    normal_style = styles["Normal"]
    normal_style.fontName = "Helvetica"
    normal_style.fontSize = 11
    normal_style.leading = 14
    
    bullet_style = ParagraphStyle(
        name="Bullet",
        fontName="Helvetica",
        fontSize=11,
        leading=14,
        leftIndent=20,
        bulletFontName="Helvetica",
        bulletFontSize=11,
        bulletIndent=10
    )
    
    # Create the content for the PDF
    story = []
    
    # Add title
    title = f"Study Guide for {session.get('pdf_filename', 'Uploaded PDF')}"
    story.append(Paragraph(title, title_style))
    story.append(Spacer(1, 0.25 * inch))
    
    # Add the rendered HTML content
    from bs4 import BeautifulSoup
    from reportlab.platypus import Table, TableStyle
    from reportlab.lib import colors

    soup = BeautifulSoup(study_guide_html, 'html.parser')
    
    for element in soup.find_all(['h1', 'h2', 'h3', 'p', 'ul', 'li', 'code', 'table', 'tr', 'th', 'td']):
        if element.name in ['h1', 'h2', 'h3']:
            style = ParagraphStyle(
                name=element.name,
                fontName="Helvetica-Bold",
                fontSize=14 if element.name == 'h1' else 12,
                leading=16,
                spaceAfter=10
            )
            story.append(Paragraph(element.get_text(), style))
        elif element.name == 'p':
            story.append(Paragraph(element.get_text(), normal_style))
        elif element.name == 'ul':
            for li in element.find_all('li'):
                story.append(Paragraph(f"- {li.get_text()}", normal_style))
        elif element.name == 'code':
            code_style = ParagraphStyle(
                name="Code",
                fontName="Courier",
                fontSize=10,
                leading=12,
                backColor="#f0f0f0",
                leftIndent=10
            )
            story.append(Paragraph(element.get_text(), code_style))
        elif element.name == 'table':
            # Handle tables
            table_data = []
            for row in element.find_all('tr'):
                table_row = [cell.get_text() for cell in row.find_all(['th', 'td'])]
                table_data.append(table_row)
            
            # Create a table with gridlines
            table = Table(table_data)
            table.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), 1, colors.black),  # Add gridlines
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),  # Header background
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Center align all cells
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # Vertically align all cells
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Bold font for header
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),  # Regular font for body
                ('FONTSIZE', (0, 0), (-1, -1), 10),  # Font size
            ]))
            story.append(table)
        story.append(Spacer(1, 0.1 * inch))
    
    # Build the PDF
    doc.build(story)
    
    return send_file(pdf_filename, as_attachment=True, download_name=f"study_guide_{session.get('pdf_filename', 'document').replace('.pdf', '')}.pdf")

@app.route('/download_quiz')
def download_quiz():
    quiz_id = session.get('quiz_id')
    
    if not quiz_id:
        flash('No quiz found. Please generate a quiz first.', 'danger')
        return redirect(url_for('index'))
    
    # Get the quiz file path
    quiz_file = os.path.join(app.config['OUTPUT_FOLDER'], f"{quiz_id}_quiz.json")
    
    # Check if the file exists
    if not os.path.exists(quiz_file):
        flash('Quiz file not found. Please generate a new quiz.', 'danger')
        return redirect(url_for('index'))
    
    # Read the quiz JSON
    with open(quiz_file, 'r') as source:
        quiz_json = source.read()
    
    # Parse the JSON 
    quiz_data = json.loads(quiz_json)
    
    # Create a PDF file
    pdf_filename = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf').name
    
    # Set up the PDF document
    doc = SimpleDocTemplate(
        pdf_filename,
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )
    
    # Define styles
    styles = getSampleStyleSheet()
    title_style = styles["Heading1"]
    title_style.alignment = 1  # Center alignment
    
    normal_style = styles["Normal"]
    normal_style.fontName = "Helvetica"
    normal_style.fontSize = 11
    normal_style.leading = 14
    
    question_style = ParagraphStyle(
        name="Question",
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        spaceAfter=6,
        textColor=colors.darkblue
    )
    
    option_style = ParagraphStyle(
        name="Option",
        fontName="Helvetica",
        fontSize=11,
        leading=14,
        leftIndent=20
    )
    
    answer_style = ParagraphStyle(
        name="Answer",
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        leftIndent=10,
        textColor=colors.darkgreen
    )
    
    # Create the content for the PDF
    story = []
    
    # Add title
    title = f"Quiz for {session.get('pdf_filename', 'Uploaded PDF')}"
    story.append(Paragraph(title, title_style))
    story.append(Spacer(1, 0.25 * inch))
    
    # Format the quiz questions
    for i, question in enumerate(quiz_data, 1):
        # Add the question
        question_text = f"Question {i}: {question['question']}"
        story.append(Paragraph(question_text, question_style))
        story.append(Spacer(1, 0.1 * inch))
        
        # Add the options
        for j, option in enumerate(question['options'], 1):
            option_text = f"{j}. {option}"
            story.append(Paragraph(option_text, option_style))
        
        # Add the answer
        answer_text = f"Answer: {question['answer']}"
        story.append(Spacer(1, 0.1 * inch))
        story.append(Paragraph(answer_text, answer_style))
        story.append(Spacer(1, 0.25 * inch))
    
    # Build the PDF
    doc.build(story)
    
    return send_file(pdf_filename, as_attachment=True, download_name=f"quiz_{session.get('pdf_filename', 'document').replace('.pdf', '')}.pdf")

@app.route('/clear')
def clear_session():
    # Clean up any files associated with this session
    if session.get('study_guide_id'):
        study_guide_file = os.path.join(app.config['OUTPUT_FOLDER'], f"{session.get('study_guide_id')}_study_guide.txt")
        if os.path.exists(study_guide_file):
            try:
                os.remove(study_guide_file)
            except:
                logger.warning(f"Could not remove study guide file: {study_guide_file}")
    
    if session.get('quiz_id'):
        quiz_file = os.path.join(app.config['OUTPUT_FOLDER'], f"{session.get('quiz_id')}_quiz.json")
        if os.path.exists(quiz_file):
            try:
                os.remove(quiz_file)
            except:
                logger.warning(f"Could not remove quiz file: {quiz_file}")
    
    # Clear the session
    session.clear()
    flash('Session cleared. You can upload a new PDF.', 'info')
    return redirect(url_for('index'))

# Error handlers
@app.errorhandler(413)
def request_entity_too_large(error):
    flash('File too large! Maximum size is 16MB.', 'danger')
    return redirect(url_for('index')), 413

@app.errorhandler(500)
def internal_server_error(error):
    flash('An unexpected error occurred. Please try again.', 'danger')
    return redirect(url_for('index')), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))  # Use Railway's PORT or default to 8080
    app.run(host="0.0.0.0", port=port)