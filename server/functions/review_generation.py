import json
import os
import re
import textwrap

from flask import g, has_app_context

SKIPPED_TOKEN = "Skipped"


def to_markdown(text):
    text = text.replace("\u2022", "  *")
    return textwrap.indent(text, "> ", predicate=lambda _: True)


def normalize_question(question_text):
    if not isinstance(question_text, str):
        return ""
    return " ".join(question_text.strip().lower().split())


def normalize_suspicious_count(suspicious_count):
    try:
        return int(suspicious_count)
    except (TypeError, ValueError):
        return 0


def load_preset_ideal_answers(job_role):
    ideal_answers = {}

    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(current_dir, "..", "data", "preset_questions.json")

        if not os.path.exists(json_path):
            return ideal_answers

        with open(json_path, "r") as file_obj:
            presets = json.load(file_obj)

        normalized_title = (job_role or "").lower().strip()
        role_questions = presets.get(normalized_title, [])

        for item in role_questions:
            if not isinstance(item, dict):
                continue

            question_text = item.get("question")
            answer_text = item.get("answer")
            if question_text and answer_text:
                ideal_answers[normalize_question(question_text)] = answer_text.strip()

        if ideal_answers:
            print(f"Loaded {len(ideal_answers)} preset ideal answers for {job_role}")
    except Exception as e:
        print(f"Error loading preset ideal answers: {e}")

    return ideal_answers


def parse_json_like(raw_text):
    if not raw_text:
        return None

    candidates = [raw_text.strip()]

    fenced_match = re.search(
        r"```(?:json)?\s*(\{[\s\S]*\}|\[[\s\S]*\])\s*```",
        raw_text,
        re.IGNORECASE,
    )
    if fenced_match:
        candidates.append(fenced_match.group(1).strip())

    first_curly = raw_text.find("{")
    last_curly = raw_text.rfind("}")
    if first_curly != -1 and last_curly != -1 and last_curly > first_curly:
        candidates.append(raw_text[first_curly : last_curly + 1].strip())

    first_square = raw_text.find("[")
    last_square = raw_text.rfind("]")
    if first_square != -1 and last_square != -1 and last_square > first_square:
        candidates.append(raw_text[first_square : last_square + 1].strip())

    for candidate in candidates:
        try:
            return json.loads(candidate)
        except Exception:
            continue

    return None


def generate_ai_ideal_answers(job_role, questions):
    if not questions:
        return {}

    if not has_app_context():
        return {}

    if not getattr(g, "model", None):
        return {}

    prompt = (
        "You are an expert technical interviewer.\n"
        "Generate one concise ideal answer for each interview question.\n"
        "Return ONLY valid JSON with this exact schema:\n"
        '{"answers":[{"question":"<question>","actual_answer":"<ideal answer>"}]}\n'
        "Rules:\n"
        "1. Keep each answer practical and interview-ready.\n"
        "2. Keep each answer under 120 words.\n"
        "3. Do not add markdown or any text outside JSON.\n\n"
        f"Job role: {job_role}\n"
        "Questions:\n"
        + "\n".join(
            [f"{index + 1}. {question}" for index, question in enumerate(questions)]
        )
    )

    try:
        response = g.model.generate_content([prompt])
        raw_text = (response.text or "").strip()
        parsed = parse_json_like(raw_text)
        if parsed is None:
            return {}

        answer_items = []
        if isinstance(parsed, dict):
            if isinstance(parsed.get("answers"), list):
                answer_items = parsed.get("answers")
            elif isinstance(parsed.get("qa_report"), list):
                answer_items = parsed.get("qa_report")
        elif isinstance(parsed, list):
            answer_items = parsed

        generated = {}
        for index, item in enumerate(answer_items):
            if isinstance(item, dict):
                question_text = item.get("question") or item.get("q")
                answer_text = (
                    item.get("actual_answer")
                    or item.get("ideal_answer")
                    or item.get("answer")
                )
            elif isinstance(item, str):
                question_text = questions[index] if index < len(questions) else None
                answer_text = item
            else:
                continue

            if not answer_text:
                continue

            if not question_text and index < len(questions):
                question_text = questions[index]

            normalized = normalize_question(question_text)
            if normalized:
                generated[normalized] = str(answer_text).strip()

        if generated:
            print(f"Generated ideal answers for {len(generated)} questions.")

        return generated
    except Exception as e:
        print(f"Unable to generate AI ideal answers: {e}")
        return {}


def build_qa_report(job_role, qns, ans):
    qns = qns or []
    ans = ans or []

    preset_ideal_answers = load_preset_ideal_answers(job_role)
    missing_questions = []

    for question_text in qns:
        normalized = normalize_question(question_text)
        if normalized and normalized not in preset_ideal_answers:
            missing_questions.append(question_text)

    generated_ideal_answers = generate_ai_ideal_answers(job_role, missing_questions)

    qa_report = []
    for index, question_text in enumerate(qns):
        answer_text = ans[index] if index < len(ans) else ""
        answer_text = answer_text if isinstance(answer_text, str) else str(answer_text)
        cleaned_answer = answer_text.strip()

        submitted_answer = cleaned_answer if cleaned_answer else SKIPPED_TOKEN
        if submitted_answer.lower() == SKIPPED_TOKEN.lower():
            submitted_answer = SKIPPED_TOKEN

        normalized_question = normalize_question(question_text)
        actual_answer = (
            preset_ideal_answers.get(normalized_question)
            or generated_ideal_answers.get(normalized_question)
        )

        qa_report.append(
            {
                "question_no": index + 1,
                "question": question_text,
                "submitted_answer": submitted_answer,
                "actual_answer": actual_answer if actual_answer else None,
            }
        )

    merged_ideal_answers = {**preset_ideal_answers, **generated_ideal_answers}
    return qa_report, merged_ideal_answers


def gen_review(job_role, qns, ans, suspiciousCount):
    qns = qns or []
    ans = ans or []
    suspicious_count = normalize_suspicious_count(suspiciousCount)

    answered_count = 0
    skipped_count = 0
    for index in range(len(qns)):
        answer_text = ans[index] if index < len(ans) else ""
        answer_text = answer_text if isinstance(answer_text, str) else str(answer_text)
        if answer_text.strip() and answer_text.strip().lower() != SKIPPED_TOKEN.lower():
            answered_count += 1
        else:
            skipped_count += 1

    qa_report, ideal_answers = build_qa_report(job_role, qns, ans)

    data = "Job Role: " + str(job_role)
    data += "Question & Answers:"

    for index, question_text in enumerate(qns):
        answer_text = ans[index] if index < len(ans) else SKIPPED_TOKEN
        answer_text = answer_text if isinstance(answer_text, str) else str(answer_text)

        if "tell me about yourself" in question_text.lower():
            continue

        data += "\n Qtn " + str(index + 1) + ": " + question_text

        normalized_question = normalize_question(question_text)
        if normalized_question in ideal_answers:
            data += "\n Ideal Answer: " + ideal_answers[normalized_question]

        data += "\n My Answer: " + (answer_text.strip() or SKIPPED_TOKEN)

    data += (
        "\nSuspicious Activity detected "
        + str(suspicious_count)
        + " times while giving online mock interview."
    )

    msg = (
        f"Context = {data} \n"
        "The above context represents the data of an interviewee. "
        "Please write a 500-700 word review neatly for him/her, providing suggestions for areas of improvement based on the above context."
        "\nIMPORTANT : PLEASE FOLLOW THE BELOW RULES\n"
        "RULE 1: Write the review as if you are directly TALKING WITH HIM/HER."
        "RULE 2: Don't write anything extra, only write the review."
        "RULE 3: Dont include any main headings such as 'review', use side-headings for explaining."
        "RULE 5: This review is for an interview given in an website where anyone take mock interviews,"
        "so write review based on that, but dont tell hi,thank u and all."
        "RULE 6: Dont use/assume or write fake data which is not in context for review."
        "RULE 7: If suspicious activiyt is detected more than 3 times, "
        "then also tell how to ensure things such as cameras are working proper and not to change tabs in online interviews "
        "and also tell that the interviewers might assume it as malpractice"
        "RULE 8: If 'Ideal Answer' is provided, compare the 'My Answer' with 'Ideal Answer' to give specific technical feedback."
        "RULE 9: Rate the candidate on a scale of 1 to 10 based on the quality of their answers. Provide this rating at the very end of your response in this strict format: [[RATING: X]] (e.g., [[RATING: 7]])."
    )

    rating = 0

    try:
        import ollama

        print("Using Ollama (llama3)...")
        response = ollama.chat(
            model="llama3",
            messages=[
                {
                    "role": "user",
                    "content": msg,
                },
            ],
        )
        raw_text = response["message"]["content"]

        rating_match = re.search(r"\[\[RATING:\s*(\d+)\]\]", raw_text)
        if rating_match:
            try:
                rating = int(rating_match.group(1))
            except Exception:
                rating = 5
            raw_text = raw_text.replace(rating_match.group(0), "")

        final_text = to_markdown(raw_text)
        return {
            "review": final_text,
            "answered": answered_count,
            "skipped": skipped_count,
            "rating": rating,
            "qa_report": qa_report,
        }
    except Exception as e:
        print(f"Ollama failed: {e}")
        print("Switching to Rule-Based Fallback...")

        review_text = (
            "## Interview Review\n\n"
            "**Overall Impression:**\n"
            "Thank you for completing the interview. Based on your responses, you showed a good attempt at answering the questions. "
            "**Technical Feedback:**\n"
            "*   **Response Length:** Your answers were received successfully.\n"
            f"*   **Suspicious Activity:** detected {suspicious_count} times. "
            f"{'Great job maintaining focus!' if suspicious_count < 3 else 'Please ensure you look at the camera and avoid switching tabs.'}\n\n"
            "** Recommendations:**\n"
            "speak louder and clearer to ensure your answers are fully captured.\n"
            "*   Structure your answers using the STAR method (Situation, Task, Action, Result).\n"
            "*   Ensure clear audio and video lighting for future interviews.\n"
            "*   Practice common technical questions for your role.\n\n"
            "*(Note: Full AI analysis is unavailable at this time.)*"
        )

        if answered_count > 1:
            rating = 5
            if suspicious_count == 0:
                rating += 1
            if skipped_count == 0:
                rating += 1
        else:
            rating = 0

        return {
            "review": to_markdown(review_text),
            "answered": answered_count,
            "skipped": skipped_count,
            "rating": rating,
            "qa_report": qa_report,
        }
