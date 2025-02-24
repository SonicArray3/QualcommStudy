import sys
import fitz  # PyMuPDF
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QFileDialog, QTextEdit

class StudyToolApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("AI-Powered ADHD Study Tool")
        self.setGeometry(100, 100, 600, 400)  # Set window size

        # Create buttons for features
        self.upload_button = QPushButton('Upload Textbook')
        self.flashcards_button = QPushButton('Generate AI Flashcards')
        self.summarize_button = QPushButton('Summarize Content')
        self.quiz_button = QPushButton('Make a Quick Quiz')

        # Create a text area to display extracted text
        self.text_display = QTextEdit(self)
        self.text_display.setReadOnly(True)  # Make text area read-only

        # Connect buttons to functions
        self.upload_button.clicked.connect(self.upload_textbook)
        self.flashcards_button.clicked.connect(self.generate_flashcards)
        self.summarize_button.clicked.connect(self.summarize_content)
        self.quiz_button.clicked.connect(self.make_quiz)

        # Layout to arrange widgets
        layout = QVBoxLayout()
        layout.addWidget(self.upload_button)
        layout.addWidget(self.flashcards_button)
        layout.addWidget(self.summarize_button)
        layout.addWidget(self.quiz_button)
        layout.addWidget(self.text_display)  # Add text area to layout

        # Set layout and display window
        self.setLayout(layout)

    # Function to handle textbook upload
    def upload_textbook(self):
        file, _ = QFileDialog.getOpenFileName(self, "Open Textbook", "", "PDF Files (*.pdf);;Text Files (*.txt)")
        if file:
            print(f"Textbook uploaded: {file}")
            text = self.extract_text_from_pdf(file)
            self.text_display.setText(text)  # Display the extracted text

    # Function to extract text from PDF using PyMuPDF
    def extract_text_from_pdf(self, pdf_file):
        doc = fitz.open(pdf_file)  # Open the PDF file
        text = ""
        for page_num in range(doc.page_count):  # Loop through each page
            page = doc.load_page(page_num)  # Get the page
            text += page.get_text()  # Extract text from the page
        return text

    # Placeholder functions for AI features (to be implemented later)
    def generate_flashcards(self):
        print("Generate AI Flashcards")
        # Add AI model code here

    def summarize_content(self):
        print("Summarize Content")
        # Add summarization model code here

    def make_quiz(self):
        print("Make a Quick Quiz")
        # Add quiz model code here

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = StudyToolApp()
    window.show()
    sys.exit(app.exec())
