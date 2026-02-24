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

CODE_GEN_PROMPT = """You are a Python data analyst. You have a pandas DataFrame called `df` with these columns:
{columns}

The libraries plt, sns, pd, np, os, uuid are already imported and available.

Write ONLY Python code (no explanation, no markdown fences) to answer this question:
{question}

Rules:
- If a plot is requested, save it with: plt.savefig(f'static/plot_{{uuid.uuid4().hex[:8]}}.png', bbox_inches='tight') and plt.close()
- Print the final result so it appears in output
- Do NOT use plt.show()
- Keep code concise"""

FORMAT_PROMPT = """You are a helpful data analyst. The user asked: "{question}"

The Python code produced this output:
{result}

{image_note}

Give a clear, concise answer based on this output. If there was an error, explain what went wrong simply."""


def run_query(question: str) -> dict:
    code_response = llm.invoke(CODE_GEN_PROMPT.format(columns=COLUMNS_INFO, question=question))
    code = code_response.content.strip()
    code = code.replace("```python", "").replace("```", "").strip()

    plt.close("all")

    try:
        result = tool.run(code)
    except Exception as e:
        result = f"Error: {e}"

    images = []
    import glob
    current_plots = glob.glob("static/plot_*.png")
    for p in current_plots:
        p_normalized = p.replace("\\", "/")
        images.append(f"/{p_normalized}")

    image_note = ""
    if images:
        image_note = "A plot image was saved and will be shown to the user."

    format_response = llm.invoke(FORMAT_PROMPT.format(
        question=question,
        result=result if result else "(no text output — likely a plot was generated)",
        image_note=image_note
    ))

    return {
        "text": format_response.content.strip(),
        "images": images
    }