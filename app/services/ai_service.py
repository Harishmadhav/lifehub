import json
import os
from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def generate_daily_plan(tasks, habits):
    if not tasks and not habits:
        return "You have no pending tasks or habits right now. Great time to plan ahead or take a break!"

    task_lines = "\n".join(
        f"- {t.title} (priority: {t.priority}, due: {t.due_date if t.due_date else 'no due date'})"
        for t in tasks
    ) or "No pending tasks."

    habit_lines = "\n".join(
        f"- {h.name} (current streak: {h.current_streak} days)"
        for h in habits
    ) or "No habits tracked."

    prompt = f"""You are a helpful productivity assistant. Based on the user's tasks and habits below, 
write a short, motivating daily plan (max 150 words) suggesting what to focus on today and in what order. 
Be specific and practical, not generic.

Pending Tasks:
{task_lines}

Habits to maintain:
{habit_lines}

Daily Plan:"""

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300,
        temperature=0.7
    )

    return response.choices[0].message.content

def chat_with_assistant(user_message, tasks, habits):
    task_lines = "\n".join(
        f"- {t.title} (priority: {t.priority}, status: {t.status}, due: {t.due_date if t.due_date else 'no due date'})"
        for t in tasks
    ) or "No tasks."

    habit_lines = "\n".join(
        f"- {h.name} (current streak: {h.current_streak} days)"
        for h in habits
    ) or "No habits tracked."

    system_prompt = f"""You are LifeHub's productivity assistant. You help the user manage their tasks and habits.
Answer their question helpfully and concisely (max 250 words), using the context below when relevant.

User's Tasks:
{task_lines}

User's Habits:
{habit_lines}"""

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        max_tokens=600,
        temperature=0.7
    )

    return response.choices[0].message.content

def suggest_task(tasks, habits, hint=""):
    task_lines = "\n".join(
        f"- {t.title} (priority: {t.priority}, status: {t.status})"
        for t in tasks
    ) or "No existing tasks."

    habit_lines = "\n".join(f"- {h.name}" for h in habits) or "No habits tracked."

    hint_line = f'The user has started typing this idea: "{hint}". Build on it.' if hint else "Suggest one useful new task."

    prompt = f"""You are a productivity assistant. {hint_line}

User's recent tasks:
{task_lines}

User's habits:
{habit_lines}

Respond with ONLY a JSON object, no explanation, no markdown, in exactly this format:
{{"title": "short task title", "description": "one or two sentence description", "priority": "low or medium or high"}}"""

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=800,
        temperature=0.7
    )

    text = response.choices[0].message.content.strip()

    # Remove markdown code fences if the model added them
    if text.startswith("```"):
        text = text.strip("`").strip()
        if text.lower().startswith("json"):
            text = text[4:].strip()

    data = json.loads(text)

    priority = str(data.get("priority", "medium")).lower()
    if priority not in ("low", "medium", "high"):
        priority = "medium"

    return {
        "title": str(data.get("title", ""))[:200],
        "description": str(data.get("description", "")),
        "priority": priority
    }