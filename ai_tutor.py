import json
from openai import OpenAI
import os
from dotenv import load_dotenv
load_dotenv()
client = OpenAI()

# fisier pentru chat istoric per topic
CHAT_DB_PATH = "data/chat_history.json"


def load_chat_history():
    try:
        with open(CHAT_DB_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}


def save_chat_history(data):
    with open(CHAT_DB_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# -------------------------------
# AI Tutor Logic
# -------------------------------
def build_prompt(topic_name, topic_desc, note_titles, selected_note_content, settings):
    lang = settings.get("language", "RO")
    depth = settings.get("depth", "medium")

    depth_map = {
        "short": "Răspunde scurt în 2-3 rânduri.",
        "medium": "Răspunde moderat, 4-8 rânduri.",
        "detailed": "Explică detaliat și pas cu pas, 8-15 rânduri."
    }

    return f"""
Ești un tutor AI care ajută utilizatorul să înțeleagă topicul: **{topic_name}**.

Descriere topic:
{topic_desc}

Titlurile notelor:
{', '.join(note_titles)}

Conținut extras:
{selected_note_content}

Instrucțiuni stil:
- Toate răspunsurile tale trebuie să fie ÎNTOTDEAUNA în limba: {lang}.
- Dacă întrebarea utilizatorului este în altă limbă, răspunde tot în {lang}.
- Nivel detaliu: {depth_map.get(depth, "")}
"""


def ask_tutor(topic_id, topic_name, topic_desc, note_titles, selected_note_content, question, settings):
    history = load_chat_history()
    if str(topic_id) not in history:
        history[str(topic_id)] = []

    # BUILD SYSTEM + USER MESSAGE
    system_msg = build_prompt(topic_name, topic_desc, note_titles, selected_note_content, settings)

    messages = [{"role": "system", "content": system_msg}]

    # Add history
    for msg in history[str(topic_id)]:
        messages.append(msg)

    # Add new question
    messages.append({"role": "user", "content": question})

    # CALL OPENAI
    response = client.chat.completions.create(
        model=settings.get("model", "gpt-4.1-mini"),
        messages=messages,
        temperature=settings.get("temperature", 0.5),
        max_tokens=settings.get("max_tokens", 300)
    )

    answer = response.choices[0].message.content

    # Save history
    
    tid = str(topic_id)
    if tid not in history:
        history[tid] = []

    history[tid].append({"role": "user", "content": question})
    history[tid].append({"role": "assistant", "content": answer})
    MAX_HISTORY = 10
    if len(history[tid]) > MAX_HISTORY:
        history[tid] = history[tid][-MAX_HISTORY:]
    save_chat_history(history)

    return answer
