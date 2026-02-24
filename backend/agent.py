import os
import uuid
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_experimental.tools.python.tool import PythonAstREPLTool

load_dotenv()

if os.getenv("gptoss"):
    os.environ["OPENAI_API_KEY"] = os.getenv("gptoss")

df = pd.read_csv("titanic/train.csv")

llm = ChatOpenAI(
    model="openai/gpt-oss-20b",
    openai_api_base="https://openrouter.ai/api/v1",
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0
)

tool = PythonAstREPLTool(locals={
    "df": df,
    "plt": plt,
    "sns": sns,
    "pd": pd,
    "np": np,
    "os": os,
    "uuid": uuid,
})

COLUMNS_INFO = str(list(df.columns)) + "\n" + str(df.dtypes.to_string())

CODE_GEN_PROMPT = (
    "You have a pandas DataFrame called `df` with these columns:\n"
    "{columns}\n\n"
    "The libraries plt, sns, pd, np, os, uuid are already imported.\n\n"
    "Write ONLY executable Python code (no explanation, no markdown) to answer: {question}\n\n"
    "Rules:\n"
    "- If a plot is needed, save with: plt.savefig(f'static/plot_{{uuid.uuid4().hex[:8]}}.png', bbox_inches='tight', dpi=100); plt.close()\n"
    "- Print the final result\n"
    "- Do NOT use plt.show()\n"
    "- Keep code concise"
)

CLASSIFY_PROMPT = (
    "Is this question about analyzing, querying, or visualizing data from a dataset? "
    "Answer ONLY 'yes' or 'no'.\n\n"
    "Question: {question}"
)

CHAT_PROMPT = (
    "You are a friendly assistant for a Titanic dataset explorer app. "
    "The user said: \"{question}\"\n\n"
    "This is not a data question, so just respond conversationally. "
    "Mention that you can help analyze the Titanic dataset if they have questions about it."
)

FORMAT_PROMPT = (
    "User asked: \"{question}\"\n\n"
    "Code output:\n{result}\n\n"
    "{image_note}\n"
    "Give a clear, concise answer based on this output."
)
GREETINGS = {"hello", "hi", "hey", "hallo", "hola", "howdy", "good morning", "good evening",
             "good afternoon", "how are you", "whats up", "what's up", "sup", "yo", "greetings"}


def run_query(question: str) -> dict:
    q_lower = question.strip().lower().rstrip("!?.,")

    if q_lower in GREETINGS or len(q_lower.split()) <= 3 and any(g in q_lower for g in GREETINGS):
        chat_response = llm.invoke(CHAT_PROMPT.format(question=question))
        return {"text": chat_response.content.strip(), "images": []}

    classify = llm.invoke(CLASSIFY_PROMPT.format(question=question))
    is_data_question = "yes" in classify.content.strip().lower()

    if not is_data_question:
        chat_response = llm.invoke(CHAT_PROMPT.format(question=question))
        return {"text": chat_response.content.strip(), "images": []}

    import glob
    before_plots = set(glob.glob("static/plot_*.png"))

    code_response = llm.invoke(CODE_GEN_PROMPT.format(columns=COLUMNS_INFO, question=question))
    code = code_response.content.strip()
    code = code.replace("```python", "").replace("```", "").strip()

    plt.close("all")

    try:
        result = tool.run(code)
    except Exception as e:
        result = f"Error: {e}"

    after_plots = set(glob.glob("static/plot_*.png"))
    new_plots = after_plots - before_plots
    images = [f"/{p.replace(chr(92), '/')}" for p in new_plots]

    image_note = "A chart was generated and will be shown to the user." if images else ""

    format_response = llm.invoke(FORMAT_PROMPT.format(
        question=question,
        result=result if result else "(no text output — a plot was generated)",
        image_note=image_note
    ))

    return {
        "text": format_response.content.strip(),
        "images": images
    }