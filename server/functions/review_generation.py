from flask import g
import textwrap
import json
import os

def to_markdown(text):
    text = text.replace('•', '  *')
    return textwrap.indent(text, '> ', predicate=lambda _: True)

import re

def gen_review(job_role, qns, ans, suspiciousCount):
    # data = job_role + qns_ans + suspiciousCount

    # Calculate answered and skipped
    answered_count = 0
    skipped_count = 0
    for a in ans:
        if a and a.strip() and a != 'Skipped':
             answered_count += 1
        else:
             skipped_count += 1


    # Load preset questions to get ideal answers
    ideal_answers = {}
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(current_dir, '..', 'data', 'preset_questions.json')
        
        if os.path.exists(json_path):
            with open(json_path, 'r') as f:
                presets = json.load(f)
            
            normalized_title = job_role.lower().strip()
            if normalized_title in presets:
                # Create a map of question text to ideal answer (if available)
                for item in presets[normalized_title]:
                    if not isinstance(item, dict):
                        continue
                    question_text = item.get('question')
                    answer_text = item.get('answer')
                    if question_text and answer_text:
                        ideal_answers[question_text] = answer_text
                print(f"Loaded ideal answers for {job_role}")
    except Exception as e:
        print(f"Error loading ideal answers: {e}")

    data = "Job Role: " + job_role
    # data += "Experience level: " + experience_lvl
    data += "Question & Answers:"

    for i, (q_text, a_text) in enumerate(zip(qns, ans)):
        # Skip "Introduce yourself" question from review
        if "tell me about yourself" in q_text.lower():
            continue

        data += "\n Qtn " + str(i + 1) + ": " + q_text
        
        # Include ideal answer if available
        if q_text in ideal_answers:
             data += "\n Ideal Answer: " + ideal_answers[q_text]
             
        data += "\n My Answer: " + a_text

    data += "\nSuspicious Activity detected " + str(suspiciousCount) + " times while giving online mock interview."

    # print("\nData = ",data)

    msg = (
        f"Context = {data} \n"
        "The above context represents the data of an interviewee. "
        "Please write a 500-700 word review neatly for him/her, providing suggestions for areas of improvement based on the above context."
        "\nIMPORTANT : PLEASE FOLLOW THE BELOW RULES\n"
        "RULE 1: Write the review as if you are directly TALKING WITH HIM/HER."
        # "RULE 2: Be polite, but DONT use fake data or assumptions for review generation."
        "RULE 2: Don't write anything extra, only write the review."
        "RULE 3: Dont include any main headings such as 'review', use side-headings for explaining."
        # "RULE 4: If emotion analysis data is present then USE that for review also."
        "RULE 5: This review is for an interview given in an website where anyone take mock interviews,"
        "so write review based on that, but dont tell hi,thank u and all."
        "RULE 6: Dont use/assume or write fake data which is not in context for review."
        "RULE 7: If suspicious activiyt is detected more than 3 times, "
        "then also tell how to ensure things such as cameras are working proper and not to change tabs in online interviews "
        "and also tell that the interviewers might assume it as malpractice"
        "RULE 8: If 'Ideal Answer' is provided, compare the 'My Answer' with 'Ideal Answer' to give specific technical feedback."
        "RULE 9: Rate the candidate on a scale of 1 to 10 based on the quality of their answers. Provide this rating at the very end of your response in this strict format: [[RATING: X]] (e.g., [[RATING: 7]])."
    )

    # response = g.chat.send_message(msg)

    # call gemini with retry logic
    # max_retries = 3
    # retry_delay = 20  # Start with 20 seconds
    
    # # Try Gemini first
    # for attempt in range(max_retries):
    #     try:
    #         response = g.model.generate_content([msg])
    #         raw_text = response.text
    #         # Extract and remove rating
    #         rating = 0
    #         rating_match = re.search(r'\[\[RATING:\s*(\d+)\]\]', raw_text)
    #         if rating_match:
    #             rating = int(rating_match.group(1))
    #             raw_text = raw_text.replace(rating_match.group(0), '')
            
    #         final_text = to_markdown(raw_text)
    #         return {
    #             'review': final_text,
    #             'answered': answered_count,
    #             'skipped': skipped_count,
    #             'rating': rating
    #         }
    #     except Exception as e:
    #         error_str = str(e)
    #         print(f"Gemini Attempt {attempt+1} failed: {error_str}")
    #     ....
   
    # For now, sticking to the existing logic structure where we use Ollama fallback or return
    # Since the previous code block was a fallback to Ollama, let's implement the logic 
    # properly within the same structure. 

    # Wait, the previous code had commented out Gemini logic and used Ollama directly as fallback 
    # but based on imports in app.py it seems Gemini IS used first but maybe locally commented out?
    # app.py imports genai and sets g.model. 
    # Let's check `review_generation.py` again. It has `g.chat.send_message(msg)` commented out.
    # It has valid `import ollama` in the try/except block.
    
    # I will modify the function to try to use Gemini if `g.model` is available (it is set in app.py)
    # But wait, looking at the provided file content, the Gemini part is COMMENTED OUT. 
    # I should respect that and only modify the active parts (Ollama and fallback).
    
    rating = 0
    
    # Fallback to Ollama
    try:
        import ollama
        print("Using Ollama (llama3)...")
        response = ollama.chat(model='llama3', messages=[
            {
                'role': 'user',
                'content': msg,
            },
        ])
        raw_text = response['message']['content']
        
        # Extract and remove rating
        rating_match = re.search(r'\[\[RATING:\s*(\d+)\]\]', raw_text)
        if rating_match:
            try:
                rating = int(rating_match.group(1))
            except:
                rating = 5 # Default if parse fails
            raw_text = raw_text.replace(rating_match.group(0), '')

        final_text = to_markdown(raw_text)
        return {
            'review': final_text,
            'answered': answered_count,
            'skipped': skipped_count,
            'rating': rating
        }
    except Exception as e:
        print(f"Ollama failed: {e}")
        print("Switching to Rule-Based Fallback...")
        
        # Rule-Based Fallback
        review_text = (
            "## Interview Review\n\n"
            "**Overall Impression:**\n"
            "Thank you for completing the interview. Based on your responses, you showed a good attempt at answering the questions. "
            "**Technical Feedback:**\n"
            "*   **Response Length:** Your answers were received successfully.\n"
            f"*   **Suspicious Activity:** detected {suspiciousCount} times. "
            f"{'Great job maintaining focus!' if int(suspiciousCount) < 3 else 'Please ensure you look at the camera and avoid switching tabs.'}\n\n"
            "** Recommendations:**\n"
            "speak louder and clearer to ensure your answers are fully captured.\n"
            "*   Structure your answers using the STAR method (Situation, Task, Action, Result).\n"
            "*   Ensure clear audio and video lighting for future interviews.\n"
            "*   Practice common technical questions for your role.\n\n"
            "*(Note: Full AI analysis is unavailable at this time.)*"
        )
        
        # Calculate a basic rating for fallback
        if answered_count > 1:
            rating = 5
            if suspiciousCount == 0:
                rating += 1
            if skipped_count == 0:
                rating += 1
        else:
            rating = 0
            
        return {
            'review': to_markdown(review_text),
            'answered': answered_count,
            'skipped': skipped_count,
            'rating': rating
        }
