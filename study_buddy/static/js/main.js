document.addEventListener('DOMContentLoaded', function() {
    // Show spinner when processing actions are initiated
    const processingActions = document.querySelectorAll('.processing-action');
    const spinner = document.getElementById('processing-spinner');
    const uploadForm = document.getElementById('upload-form');
    
    if (processingActions) {
        processingActions.forEach(button => {
            button.addEventListener('click', function() {
                spinner.classList.remove('d-none');
                // If this is the upload button, validate file first
                if (this.id === 'upload-button' && uploadForm) {
                    const fileInput = document.getElementById('pdf-file');
                    if (!fileInput || !fileInput.files || fileInput.files.length === 0) {
                        spinner.classList.add('d-none');
                        showAlert('Please select a PDF file first.', 'danger');
                        return false;
                    }
                    
                    const file = fileInput.files[0];
                    if (file.type !== 'application/pdf') {
                        spinner.classList.add('d-none');
                        showAlert('Please select a valid PDF file.', 'danger');
                        return false;
                    }
                    
                    if (file.size > 16 * 1024 * 1024) { // 16MB
                        spinner.classList.add('d-none');
                        showAlert('File size exceeds the maximum limit of 16MB.', 'danger');
                        return false;
                    }
                }
            });
        });
    }
    
    // File input change handler
    const fileInput = document.getElementById('pdf-file');
    const fileNameDisplay = document.getElementById('file-name-display');
    
    if (fileInput && fileNameDisplay) {
        fileInput.addEventListener('change', function() {
            if (this.files && this.files.length > 0) {
                fileNameDisplay.innerHTML = `<i class="fas fa-file-pdf me-2"></i>${this.files[0].name}`;
                fileNameDisplay.classList.remove('text-muted');
                fileNameDisplay.classList.add('text-success');
            } else {
                fileNameDisplay.innerHTML = 'No file selected';
                fileNameDisplay.classList.add('text-muted');
                fileNameDisplay.classList.remove('text-success');
            }
        });
    }
    
    // Drag and drop functionality
    const dropZone = document.querySelector('.upload-zone');
    if (dropZone && fileInput) {
        // Prevent default drag behaviors
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, preventDefaults, false);
            document.body.addEventListener(eventName, preventDefaults, false);
        });
        
        // Highlight drop zone when item is dragged over it
        ['dragenter', 'dragover'].forEach(eventName => {
            dropZone.addEventListener(eventName, highlight, false);
        });
        
        // Remove highlight when item is dragged out or dropped
        ['dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, unhighlight, false);
        });
        
        // Handle dropped files
        dropZone.addEventListener('drop', handleDrop, false);
        
        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }
        
        function highlight() {
            dropZone.classList.add('upload-zone-highlight');
        }
        
        function unhighlight() {
            dropZone.classList.remove('upload-zone-highlight');
        }
        
        function handleDrop(e) {
            const dt = e.dataTransfer;
            const files = dt.files;
            
            if (files.length > 0) {
                // Update file input with dropped file
                fileInput.files = files;
                
                // Trigger change event
                const event = new Event('change');
                fileInput.dispatchEvent(event);
                
                // Validate file type and size
                const file = files[0];
                
                if (file.type !== 'application/pdf') {
                    showAlert('Please select a valid PDF file.', 'danger');
                    return;
                }
                
                if (file.size > 16 * 1024 * 1024) { // 16MB
                    showAlert('File size exceeds the maximum limit of 16MB.', 'danger');
                    return;
                }
                
                // File name is already updated by the change event we triggered
                
                showAlert('File ready for upload! Click the "Upload & Process PDF" button to continue.', 'success');
            }
        }
    }
    
    // Quiz form validation
    const quizForm = document.getElementById('quiz-form');
    if (quizForm) {
        quizForm.addEventListener('submit', function(event) {
            const numQuestions = document.getElementById('num-questions');
            if (numQuestions) {
                const value = parseInt(numQuestions.value);
                if (isNaN(value) || value < 1 || value > 20) {
                    event.preventDefault();
                    showAlert('Please enter a number between 1 and 20.', 'danger');
                    return false;
                }
            }
            spinner.classList.remove('d-none');
        });
    }
    
    // Handle quiz submission
    const quizSubmitBtn = document.getElementById('quiz-submit');
    const checkAnswersBtn = document.getElementById('check-answers');
    
    if (checkAnswersBtn) {
        checkAnswersBtn.addEventListener('click', function() {
            const quizForm = document.getElementById('quiz-questions-form');
            const questions = quizForm.querySelectorAll('.quiz-question');
            let score = 0;
            
            questions.forEach((question, index) => {
                const selectedOption = question.querySelector('input[type="radio"]:checked');
                const correctAnswer = question.getAttribute('data-answer');
                const feedbackElement = question.querySelector('.question-feedback');
                
                if (selectedOption) {
                    const selectedValue = selectedOption.value;
                    if (selectedValue === correctAnswer) {
                        score++;
                        feedbackElement.textContent = 'Correct!';
                        feedbackElement.className = 'question-feedback text-success mt-2';
                    } else {
                        feedbackElement.textContent = `Incorrect. The correct answer is: ${correctAnswer}`;
                        feedbackElement.className = 'question-feedback text-danger mt-2';
                    }
                } else {
                    feedbackElement.textContent = `Not answered. The correct answer is: ${correctAnswer}`;
                    feedbackElement.className = 'question-feedback text-warning mt-2';
                }
                feedbackElement.classList.remove('d-none');
            });
            
            const scoreDisplay = document.getElementById('quiz-score');
            scoreDisplay.textContent = `Your score: ${score}/${questions.length}`;
            scoreDisplay.classList.remove('d-none');
            
            this.classList.add('d-none');
            document.getElementById('quiz-retry').classList.remove('d-none');
        });
    }
    
    // Function to show bootstrap alerts
    function showAlert(message, type) {
        const alertPlaceholder = document.getElementById('alert-placeholder');
        if (alertPlaceholder) {
            const wrapper = document.createElement('div');
            wrapper.innerHTML = `
                <div class="alert alert-${type} alert-dismissible fade show" role="alert">
                    ${message}
                    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                </div>
            `;
            alertPlaceholder.appendChild(wrapper);
            
            // Auto dismiss after 5 seconds
            setTimeout(() => {
                const alert = wrapper.querySelector('.alert');
                if (alert) {
                    alert.classList.remove('show');
                    setTimeout(() => wrapper.remove(), 150);
                }
            }, 5000);
        }
    }
});
