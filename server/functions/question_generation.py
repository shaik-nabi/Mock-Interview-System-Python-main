import time
import random
from flask import g


def format_text(lines):
    questions = []
    question_buffer = ""

    for line in lines:
        if line.strip():  # Check if line is not empty
            if line.startswith(tuple(str(i) for i in range(1, 11))) and (line.rstrip().endswith("?") or line.rstrip().endswith(".")):
                if question_buffer:  # If there's a question in buffer, append it
                    questions.append(question_buffer.strip())
                question_buffer = line.strip() + " "  # Start new question buffer with current line
            else:
                question_buffer += line.strip() + " "  # Append line to current question buffer

    if question_buffer:  # Append the last question if there's any remaining in buffer
        questions.append(question_buffer.strip())

    return questions

def get_questions(job_title, experience_lvl, call_count):
    prompt = (
        f"Context: The user provided the job title '{job_title}' and experience level '{experience_lvl}'.\n\n"
        "Task:\n"
        "1. Validate if '{job_title}' is a legitimate job title. If it is nonsensical, inappropriate, or invalid, respond with EXACTLY the word 'INVALID'.\n"
        "2. If valid, generate exact 5 interview questions for this role and experience level.\n"
        "   - Format: Numbered list (1. ..., 2. ...)\n"
        "   - Do NOT include any intro/outro text, disclaimers, or titles. Just the 5 questions.\n"
    )

    retries = 3
    base_delay = 5  # Start with 5 seconds wait

    for attempt in range(retries):
        try:
            response = g.model.generate_content([prompt])
            text = response.text.strip()

            if text == "INVALID" or "INVALID" in text.splitlines()[0]:
                return "Please provide a valid job title."

            lines = text.split("\n")
            cleaned_lines = []
            text_to_remove = ["**Disclaimer:**","MCQs:","**MCQs:**","MCQ","Note:","Note","NOTE:","NOTE","**Note:**","**NOTE:**","**Disclaimer:**","Disclaimer:","Disclaimer"]
            
            for line in lines:
                for garbage in text_to_remove:
                    line = line.replace(garbage, "")
                if line.strip():
                    cleaned_lines.append(line.strip())

            return cleaned_lines

        except Exception as e:
            error_msg = str(e)
            print(f"Attempt {attempt+1} failed: {error_msg}")
            
            if "429" in error_msg:
                if attempt < retries - 1:
                    wait_time = base_delay * (2 ** attempt)
                    print(f"Rate limit hit. Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                    continue
                else:
                    return "Server is busy (Rate Limit). Please wait 1 minute and try again."
            
            return f"Error: {error_msg}"

def generate_questions(job_title, experience_lvl, question_count=None):
    import json
    import os

    INTRO_QUESTION = "Can you tell me about yourself and your background?"

    def is_constant_intro(question_text):
        return question_text.lower().strip() == INTRO_QUESTION.lower()

    def to_positive_int(value):
        if value is None:
            return None
        try:
            parsed = int(value)
            return parsed if parsed > 0 else None
        except (TypeError, ValueError):
            return None

    # Load role-specific preset questions
    question_pool = []
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(current_dir, '..', 'data', 'preset_questions.json')
        
        if os.path.exists(json_path):
            with open(json_path, 'r') as f:
                presets = json.load(f)
            
            # Normalize job title for case-insensitive matching
            normalized_title = job_title.lower().strip()
            
            if normalized_title in presets:
                print(f"Using preset questions for {job_title}")
                # Support both old object format and new string format.
                for item in presets[normalized_title]:
                    if isinstance(item, dict):
                        question_text = item.get('question', '').strip()
                    elif isinstance(item, str):
                        question_text = item.strip()
                    else:
                        question_text = ''

                    if question_text:
                        question_pool.append(question_text)
                
    except Exception as e:
        print(f"Error loading presets: {e}")

    if not question_pool:
        print(f"Job role '{job_title}' not found in presets. Using generic fallback questions.")
        
        question_pool = [
            "What are your greatest strengths and weaknesses?",
            "Why do you want to work for this role?",
            "Describe a challenging situation you faced and how you handled it.",
            "Where do you see yourself in 5 years?",
            "What motivates you in your work?"
        ]

    # Keep question 1 constant and randomize everything else.
    default_total = 10
    requested_total = to_positive_int(question_count) or default_total

    # Remove exact duplicate of the constant intro so question 1 remains the only fixed text.
    seen = set()
    unique_pool = []
    for question in question_pool:
        cleaned = question.strip()
        if not cleaned or is_constant_intro(cleaned):
            continue
        if cleaned not in seen:
            seen.add(cleaned)
            unique_pool.append(cleaned)

    random.shuffle(unique_pool)

    if requested_total is None:
        remaining_limit = len(unique_pool)
    else:
        remaining_limit = max(requested_total - 1, 0)

    return [INTRO_QUESTION] + unique_pool[:remaining_limit]

    # no_questions = 0
    # unformatted_qts = []
    # formatted_qts = []

    # call_count = 1

    # # keep repeating untill u get EXACTLY 5 questions
    # while no_questions != 5:

    #     # generate questions
    #     unformatted_qts=get_questions(job_title, experience_lvl, call_count)
    #     call_count += 1

    #     if not isinstance(unformatted_qts, list):
    #         return unformatted_qts

    #     # format the questions properly and store each questions in list
    #     formatted_qts = format_text(unformatted_qts)
    #     no_questions = len(formatted_qts)

    #     # print("Length = ",no_questions)
    #     if no_questions != 5:
    #         time.sleep(5)

    # # for question in formatted_qts:
    # #     print("one question = ",question)

    # return formatted_qts
