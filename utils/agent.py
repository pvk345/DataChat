from dotenv import load_dotenv
import os
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

import pandas as pd
import traceback
from typing import Tuple, Optional



from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.tools import tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from utils.data_loader import describe_dataframe
from utils.chart_detector import build_chart_from_result

# ── Global df reference (set when agent is created) ──────────────────────────
# We store the df at module level so the @tool function can access it.
_df: Optional[pd.DataFrame] = None


# ── Tool: run pandas code ─────────────────────────────────────────────────────
@tool
def run_pandas_code(code: str) -> str:
    """
    Execute a pandas code snippet against the user's dataframe (called `df`).
    Use this to answer any question about the data.
    The dataframe is already loaded as `df`.
    Return the result as a string.
    Always assign your final result to a variable called `result`.

    Example:
        result = df.groupby('product')['revenue'].sum().sort_values(ascending=False).head(5)
    """
    global _df
    if _df is None:
        return "Error: no dataframe loaded."

    local_vars = {"df": _df.copy(), "pd": pd}
    try:
        exec(code, {}, local_vars)
        result = local_vars.get("result", "Code ran but no `result` variable was set.")
        # Convert result to a readable string
        if isinstance(result, pd.DataFrame):
            return result.to_string(index=True, max_rows=30)
        elif isinstance(result, pd.Series):
            return result.to_string()
        else:
            return str(result)
    except Exception:
        return f"Code execution error:\n{traceback.format_exc()}"


# ── System prompt ─────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are an expert data analyst assistant.
The user has uploaded a dataset and you help them understand it by answering questions in plain English.

Here is a description of the dataset:
{df_description}

Rules:
- ALWAYS use the run_pandas_code tool to answer data questions. Never guess or make up numbers.
- Write clean, correct pandas code. Always store your final answer in a variable called `result`.
- After getting the tool result, summarise the finding in 1-3 clear sentences for the user.
- If the user asks for a chart, graph, or visual, you MUST include this on the last line of your response:
  CHART: <chart_type> | x=<column> | y=<column>
  Supported chart types: bar, line, scatter
- For monthly trends always use: CHART: line | x=date | y=revenue
- Never skip the CHART line if the user asks for a visual.
- Be concise. No unnecessary filler text.
- If the user asks a follow-up, use the conversation history to understand context.
"""


def create_agent(df: pd.DataFrame) -> AgentExecutor:
    """
    Create a LangChain agent with memory, bound to the provided dataframe.
    """
    global _df
    _df = df

    llm = ChatOpenAI(
        model="gpt-4o",
        temperature=0,       # deterministic for data tasks
    )

    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True,
    )

    df_description = describe_dataframe(df)

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT.format(df_description=df_description)),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    tools = [run_pandas_code]

    agent = create_openai_functions_agent(
        llm=llm,
        tools=tools,
        prompt=prompt,
    )

    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        memory=memory,
        verbose=True,          # set to False in production
        handle_parsing_errors=True,
        max_iterations=10,      # prevent infinite loops
    )

    return agent_executor


def run_agent(
    agent: AgentExecutor,
    df: pd.DataFrame,
    question: str,
) -> Tuple[str, Optional[object]]:
    """
    Run the agent on a user question.
    Returns (response_text, plotly_chart_or_None).
    """
    global _df
    _df = df  # keep module-level df in sync (in case of reupload)

    try:
        result = agent.invoke({"input": question})
        response = result.get("output", "Sorry, I couldn't generate an answer.")
    except Exception as e:
        response = f"Something went wrong: {str(e)}"
        return response, None

    # Check if agent requested a chart
    chart = build_chart_from_result(response, df)

    # Strip the CHART: line from the displayed response
    clean_response = "\n".join(
        line for line in response.splitlines()
        if not line.strip().startswith("CHART:")
    ).strip()

    return clean_response, chart
