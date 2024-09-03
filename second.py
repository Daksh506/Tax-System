import tkinter as tk
from tkinter import messagebox
import requests
import random
import re

# API URL for fetching quiz questions (filtered for general knowledge)
API_URL = "https://opentdb.com/api.php?amount=5&category=9&difficulty=medium&type=multiple"

# Pre-built fallback questions (focused on taxes)
prebuilt_questions = [
    {
        "question": "What is income tax?",
        "correct_answer": "A tax on earned income",
        "incorrect_answers": ["A tax on purchases", "A tax on property", "A tax on imports"]
    },
    {
        "question": "Which government agency is responsible for tax collection in the United States?",
        "correct_answer": "IRS (Internal Revenue Service)",
        "incorrect_answers": ["FBI", "CIA", "FDA"]
    },
    {
        "question": "What is a tax refund?",
        "correct_answer": "Money returned to taxpayers if they paid too much in taxes",
        "incorrect_answers": ["A penalty for underpaying taxes", "An additional tax for high earners", "A tax on returned goods"]
    },
    {
        "question": "What is the purpose of taxes?",
        "correct_answer": "To fund public services and government operations",
        "incorrect_answers": ["To reduce inflation", "To control population growth", "To punish citizens"]
    },
    {
        "question": "What is a sales tax?",
        "correct_answer": "A tax on purchased goods and services",
        "incorrect_answers": ["A tax on income", "A tax on property", "A tax on international trade"]
    }
]

# Function to clean text (remove special characters and emojis)
def clean_text(text):
    # Remove emojis and special characters using regex
    text = re.sub(r'[^\w\s,\'\"!?()-]', '', text)
    return text

# Function to fetch quiz questions from the API
def fetch_questions():
    try:
        response = requests.get(API_URL)
        data = response.json()
        questions = data['results']
        
        # Filter out non-tax-related questions and clean text
        tax_questions = []
        for question in questions:
            cleaned_question = clean_text(question['question'])
            cleaned_correct = clean_text(question['correct_answer'])
            cleaned_incorrect = [clean_text(ans) for ans in question['incorrect_answers']]
            
            if "tax" in cleaned_question.lower() or "taxes" in cleaned_question.lower():
                tax_questions.append({
                    "question": cleaned_question,
                    "correct_answer": cleaned_correct,
                    "incorrect_answers": cleaned_incorrect
                })

        return tax_questions if tax_questions else prebuilt_questions
    except:
        return prebuilt_questions

# Function to ask a question
def ask_question(questions, question_index, score):
    if question_index >= len(questions):
        messagebox.showinfo("Quiz Completed", f"You've completed the quiz!\nYour final score is {score}/{len(questions)}.")
        return

    question_data = questions[question_index]
    question = question_data["question"]
    correct_answer = question_data["correct_answer"]
    answers = question_data["incorrect_answers"] + [correct_answer]
    random.shuffle(answers)

    question_label.config(text=question)
    for i, answer in enumerate(answers):
        answer_buttons[i].config(text=answer, command=lambda answer=answer: check_answer(answer, correct_answer, questions, question_index, score))

# Function to check the answer
def check_answer(selected_answer, correct_answer, questions, question_index, score):
    if selected_answer == correct_answer:
        score += 1
        messagebox.showinfo("Correct!", "Well done! That's the right answer.")
    else:
        messagebox.showinfo("Incorrect", f"Oops! The correct answer was: {correct_answer}")
    ask_question(questions, question_index + 1, score)

# Create the main window with enhanced UI
root = tk.Tk()
root.title("Tax Quiz Game")
root.geometry("500x400")
root.configure(bg="#f0f0f0")

# Styling
font_large = ("Arial", 16, "bold")
font_medium = ("Arial", 14)
font_small = ("Arial", 12)

# Question label with better styling
question_label = tk.Label(root, text="", font=font_large, wraplength=450, justify="center", bg="#f0f0f0", fg="#333")
question_label.pack(pady=20)

# Answer buttons with enhanced look
answer_buttons = []
for _ in range(4):
    btn = tk.Button(root, text="", font=font_medium, width=45, bg="#ffffff", fg="#333", bd=2, relief="raised")
    btn.pack(pady=5)
    answer_buttons.append(btn)

# Automatically fetch questions and start the quiz when the window opens
questions = fetch_questions()
ask_question(questions, 0, 0)

# Start the main loop
root.mainloop()
