''' 
Llama 3.2 3B model ONLY USED FOR SUMMARY IN DEMONSTRATION. Large test files meant we often exceeded token limits and had exceedingly long wait times. 
Functions to generate AI flashcards and quizzes are present but unused.
'''
import os
import qai_hub as hub
import numpy as np
import torch
import torchvision
import sys
import pymupdf as pdf  # PyMuPDF
import random
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QFileDialog, QTextEdit, QHBoxLayout, QLabel, QRadioButton, QButtonGroup, QPushButton, QMessageBox, QListWidget
from PyQt6.QtCore import Qt
from transformers import AutoTokenizer, AutoModelForCausalLM

token = "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"
model_name = "meta-llama/Llama-3.2-3B"

tokenizer = AutoTokenizer.from_pretrained(model_name, token=token, trust_remote_code = True)
model = AutoModelForCausalLM.from_pretrained(model_name, token=token, trust_remote_code = True)
if tokenizer.pad_token is None:
    tokenizer.add_special_tokens({'pad_token': '[PAD]'})
    model.resize_token_embeddings(len(tokenizer))
class StudyToolApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("AI-Powered ADHD Study Tool")
        self.setGeometry(100, 100, 600, 400)  # Set window size

        # Create buttons for features
        # quiz, flashcards, summarize features only appear after you upload a text
        self.upload_button = QPushButton('Upload Textbook')
        self.flashcards_button = QPushButton('Generate AI Flashcards')
        self.flashcards_button.setEnabled(False)
        self.summarize_button = QPushButton('Summarize Content')
        self.summarize_button.setEnabled(False)  # Disable button for now
        self.quiz_button = QPushButton('Make a Quick Quiz')
        self.quiz_button.setEnabled(False)

        # Create a text area to display extracted text
        self.text_display = QTextEdit(self)
        self.text_display.setReadOnly(True)  # Make text area read-only

        # Connect buttons to functions
        self.upload_button.clicked.connect(self.upload_textbook)
        self.flashcards_button.clicked.connect(self.run_flashcards)
        self.summarize_button.clicked.connect(self.summarize_text)
        self.quiz_button.clicked.connect(self.run_quiz)

        # Layout to arrange widgets
        layout = QVBoxLayout()
        layout.addWidget(self.upload_button)
        layout.addWidget(self.flashcards_button)
        layout.addWidget(self.summarize_button)
        layout.addWidget(self.quiz_button)
        layout.addWidget(self.text_display)  # Add text area to layout

        # Set layout and display window
        self.setLayout(layout)
     # Function to extract text from PDF using PyMuPDF
    def extract_text_from_pdf(self, pdf_file):
        doc = pdf.open(pdf_file)  # Open the PDF file
        text = ""
        for page_num in range(doc.page_count):  # Loop through each page
            page = doc.load_page(page_num)  # Get the page
            text += page.get_text()  # Extract text from the page
        return text 
    # Function to handle textbook upload
    def upload_textbook(self):
        global file
        file, _ = QFileDialog.getOpenFileName(self, "Open Textbook", "", "PDF Files (*.pdf);;Text Files (*.txt)")
        if file:
            print(f"Textbook uploaded: {file}")
            text = self.extract_text_from_pdf(file)
            self.text_display.setText(text)  # Display the extracted text
            self.quiz_button.setEnabled(True)
            self.summarize_button.setEnabled(True)
            self.flashcards_button.setEnabled(True)
    # Placeholder functions for AI features (to be implemented later)
    def generate_important_terms(self):
        if not file:  # Ensure a file was uploaded
           self.text_display.setText("No file uploaded.")
           return
         
    
        self.text = self.extract_text_from_pdf(file)  # Extract text 

        if not self.text.strip():  # Handle empty text
             self.text_display.setText("No text extracted from the file.")
             return
        self.text = self.extract_text_from_pdf(file)
        max_length = 4096
        self.count = int(input("Please enter the amount of flashcards you would like."))
        prompt = f"Create a list of {self.count} important terms in {self.text[:500]} and their definitions as a python dictionary. Dictionary:"
        inputs = tokenizer(prompt, return_tensors='pt', max_length = max_length, padding = "max_length", truncation = True)
        outputs = model.generate(**inputs, max_new_tokens = 200, do_sample = True,
                                temperature = 0.7)  #Generate dictionary of words + definition
        flashcards = tokenizer.decode(outputs[0], skip_special_tokens=True)
        return flashcards
    def run_flashcards(self):
        self.text_display.clear()
        #flashcards = self.generate_flashcards()
        self.flashcard_window = FlashcardGame()
        self.flashcard_window.show()
    def summarize_text(self): 
        if not file:  # Ensure a file was uploaded
            print("No file uploaded.")
            return
    
        self.text = self.extract_text_from_pdf(file)  # Extract text

        if not self.text.strip():  # Handle empty text
            print("No text extracted from the file.")
            return

        #    Construct a prompt for summarization
        prompt = f"Please summarize the following text:\n\n{self.text[:2000]}\n\nSummary:"  
         # Limiting input to 1000 chars to prevent exceeding model limits
        max_length = 4000
        inputs = tokenizer(prompt, return_tensors="pt", max_length = max_length, padding = "max_length", truncation = True)

        outputs = model.generate(**inputs, max_new_tokens=300, do_sample=True, temperature=0.7)

        summary = tokenizer.decode(outputs[0], skip_special_tokens=True)
        self.text_display.clear()  # Clear previous text)
        self.text_display.setText(summary) #Display Summary in the UI
    def make_quiz(self):
        if not file:  # Ensure a file was uploaded
            print("No file uploaded.")
            return
    
        self.text = self.extract_text_from_pdf(file)  # Extract text

        if not self.text.strip():  # Handle empty text
            print("No text extracted from the file.")
            return

        #    Construct a prompt for summarization
        prompt = f"Give me a 10 question quiz based on the following text:\n\n{self.text[:1000]}\n\n Quiz:"  
         # Limiting input to 1000 chars to prevent exceeding model limits
        max_length = 3000
        inputs = tokenizer(prompt, return_tensors="pt", max_length = max_length, padding = "max_length", truncation = True)

        outputs = model.generate(**inputs, max_new_tokens=300, do_sample=True, temperature=0.7)

        quiz = tokenizer.decode(outputs[0], skip_special_tokens=True)
        self.text_display.clear()  # Clear previous text)
        self.text_display.setText(quiz) #Display Quiz in the UI
    def run_quiz(self):
        self.text_display.clear()
        self.quiz_window = QuizWidget()
        self.quiz_window.show()
class FlashcardGame(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI-generated Flashcards Matching Game")
        
        # replace with AI-generated flashcards
        self.flashcards = {
            "Algorithm": "A process or set of rules to be followed in calculations or problem-solving operations.",
            "Data": "Information processed or stored by a computer.",
            "Neural Network": "A network of artificial neurons used for machine learning tasks.",
            "Python": "A high-level programming language known for its readability.",
            "Variable": "A storage location paired with an associated symbolic name."
        }
        self.init_ui()

    def init_ui(self):
        # Main vertical layout
        main_layout = QVBoxLayout()
        
        # Horizontal layout for the two list widgets
        lists_layout = QHBoxLayout()
        
        # Create list widgets for terms and definitions
        self.terms_list = QListWidget()
        self.definitions_list = QListWidget()
        # Create Flashcards: 

        # Populate the lists
        self.terms = list(self.flashcards.keys())
        self.definitions = list(self.flashcards.values())
        random.shuffle(self.definitions)  # Shuffle definitions for a challenge

        for term in self.terms:
            self.terms_list.addItem(term)
        for definition in self.definitions:
            self.definitions_list.addItem(definition)

        # Add the lists to the horizontal layout
        lists_layout.addWidget(self.terms_list)
        lists_layout.addWidget(self.definitions_list)
        
        # Create a button to check the selected match
        self.check_button = QPushButton("Check Match")
        self.check_button.clicked.connect(self.check_match)

        # Assemble the main layout
        main_layout.addLayout(lists_layout)
        main_layout.addWidget(self.check_button)
        self.setLayout(main_layout)

    def check_match(self):
        term_item = self.terms_list.currentItem()
        definition_item = self.definitions_list.currentItem()
        if term_item is None or definition_item is None:
            QMessageBox.information(self, "Selection Error", "Please select both a term and a definition.")
            return

        term = term_item.text()
        definition = definition_item.text()

        # Check if the selected definition matches the term
        if self.flashcards[term] == definition:
            QMessageBox.information(self, "Result", f"Correct! '{term}' matches the definition.")
            # Optionally remove the matched items
            self.terms_list.takeItem(self.terms_list.currentRow())
            self.definitions_list.takeItem(self.definitions_list.currentRow())
        else:
            QMessageBox.warning(self, "Result", "Incorrect match. Please try again.")
class QuizWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Quiz Widget")
        self.questions = [
            {
                "question": "What is the capital of France?",
                "options": ["Berlin", "Paris", "Madrid", "Rome"],
                "answer": "Paris"
            },
            {
                "question": "What is 2 + 2?",
                "options": ["3", "4", "5", "22"],
                "answer": "4"
            },
            {
                "question": "Which planet is known as the Red Planet?",
                "options": ["Earth", "Venus", "Mars", "Jupiter"],
                "answer": "Mars"
            }
        ]
        self.current_index = 0
        self.score = 0
        self.init_ui()

    def init_ui(self):
        # Create the main layout
        self.layout = QVBoxLayout()

        # Label to display the question
        self.question_label = QLabel("")
        self.question_label.setWordWrap(True)
        self.layout.addWidget(self.question_label)

        # Button group for multiple choice options
        self.option_group = QButtonGroup(self)
        self.option_buttons = []

        # Create radio buttons for the answer options
        for i in range(4):
            rb = QRadioButton("")
            self.option_buttons.append(rb)
            self.option_group.addButton(rb, i)
            self.layout.addWidget(rb)

        # Submit Answer Button
        self.submit_button = QPushButton("Submit Answer")
        self.submit_button.clicked.connect(self.submit_answer)
        self.layout.addWidget(self.submit_button)

        self.setLayout(self.layout)
        self.load_question()

    def load_question(self):
        if self.current_index < len(self.questions):
            question_data = self.questions[self.current_index]
            self.question_label.setText(question_data["question"])
            options = question_data["options"]
            # Ensure the radio buttons are updated with new options and unchecked
            for i, option in enumerate(options):
                self.option_buttons[i].setText(option)
                self.option_buttons[i].setChecked(False)
        else:
            self.show_result()

    def submit_answer(self):
        # Determine which radio button is selected
        selected_button = self.option_group.checkedButton()
        if selected_button is None:
            QMessageBox.warning(self, "No Selection", "Please select an option!")
            return

        selected_answer = selected_button.text()
        correct_answer = self.questions[self.current_index]["answer"]

        # Check if the answer is correct
        if selected_answer == correct_answer:
            self.score += 1
            QMessageBox.information(self, "Correct", "Your answer is correct!")
        else:
            QMessageBox.information(
                self,
                "Incorrect",
                f"Wrong answer. The correct answer is: {correct_answer}"
            )

        self.current_index += 1
        self.load_question()

    def show_result(self):
        # Show the final result in a message box
        QMessageBox.information(
            self,
            "Quiz Completed",
            f"You scored {self.score} out of {len(self.questions)}!"
        )
        self.close()  # Optionally, close the quiz widget
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = StudyToolApp()
    window.show()
    sys.exit(app.exec())
