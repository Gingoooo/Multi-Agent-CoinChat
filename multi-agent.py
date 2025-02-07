import os
import uuid
from dotenv import load_dotenv
from config import API_SETTING
from langchain_google_genai import ChatGoogleGenerativeAI

from langchain_core.messages import ToolMessage
from langchain_core.tools import tool

from typing import Annotated, Literal

from langchain_core.tools.base import InjectedToolCallId
from langgraph.prebuilt import InjectedState

from langgraph.graph import MessagesState, StateGraph, START
from langgraph.prebuilt import create_react_agent, InjectedState
from langgraph.types import Command, interrupt
from langgraph.checkpoint.memory import MemorySaver

# 從 config 檔案匯入設定
from prompts import INTENT_CHECKER_AGENT_PROMPT, INSERT_AGENT_PROMPT, QUERY_AGENT_PROMPT
from tools import execute_sql, exec_sqlite3_sql


load_dotenv()

os.environ['GOOGLE_API_KEY'] = os.getenv('API_KEY', default=None)

model = ChatGoogleGenerativeAI(model=API_SETTING['MODEL_NAME'])


# Define a helper for each of the agent nodes to call

def make_handoff_tool(*, agent_name: str):
    """Create a tool that can return handoff via a Command"""
    tool_name = f"transfer_to_{agent_name}"

    @tool(tool_name)
    def handoff_to_agent(
        state: Annotated[dict, InjectedState],
        tool_call_id: Annotated[str, InjectedToolCallId],
    ):
        """Ask another agent for help."""
        tool_message = {
            "role": "tool",
            "content": f"Successfully transferred to {agent_name}",
            "name": tool_name,
            "tool_call_id": tool_call_id,
        }
        return Command(
            goto=agent_name,
            graph=Command.PARENT,
            update={"messages": state["messages"] + [tool_message]},
        )

    return handoff_to_agent



# Define travel advisor ReAct agent
intent_checker_agent_tools = [
    make_handoff_tool(agent_name="insert_agent"),
    make_handoff_tool(agent_name="query_agent"),
]

intent_checker_agent = create_react_agent(
    model,
    intent_checker_agent_tools,
    state_modifier=(
        INTENT_CHECKER_AGENT_PROMPT
    ),
)

def call_intent_checker_agent(
    state: MessagesState,
) -> Command[Literal["insert_agent", "human"]]:
    return intent_checker_agent.invoke(state)




# Define hotel advisor ReAct agent
insert_agent_tools = [
    exec_sqlite3_sql,
    make_handoff_tool(agent_name="intent_checker_agent"),
]

insert_agent = create_react_agent(
    model,
    insert_agent_tools,
    state_modifier=(
        INSERT_AGENT_PROMPT
    ),
)

def call_insert_agent(
    state: MessagesState,
) -> Command[Literal["intent_checker_agent", "human"]]:
    print("Insert Agent 被呼叫")  # 除錯用
    print("收到的狀態:", state)  # 除錯用
    result = insert_agent.invoke(state)
    print("Insert Agent 執行結果:", result)  # 除錯用
    return result



# Define hotel advisor ReAct agent
query_agent_tools = [
    execute_sql,
    make_handoff_tool(agent_name="intent_checker_agent"),
]

query_agent = create_react_agent(
    model,
    query_agent_tools,
    state_modifier=(
        QUERY_AGENT_PROMPT
    ),
)

def call_query_agent(
    state: MessagesState,
) -> Command[Literal["intent_checker_agent", "human"]]:
    return query_agent.invoke(state)

def human_node(
    state: MessagesState, config
) -> Command[Literal["intent_checker_agent", "human"]]:
    """A node for collecting user input."""

    user_input = interrupt(value="Ready for user input.")

    # identify the last active agent
    # (the last active node before returning to human)
    langgraph_triggers = config["metadata"]["langgraph_triggers"]
    if len(langgraph_triggers) != 1:
        raise AssertionError("Expected exactly 1 trigger in human node")

    active_agent = langgraph_triggers[0].split(":")[1]

    return Command(
        update={
            "messages": [
                {
                    "role": "human",
                    "content": user_input,
                }
            ]
        },
        goto=active_agent,
    )


builder = StateGraph(MessagesState)
builder.add_node("intent_checker_agent", call_intent_checker_agent)
builder.add_node("insert_agent", call_insert_agent)
builder.add_node("query_agent", call_query_agent)

# This adds a node to collect human input, which will route
# back to the active agent.
builder.add_node("human", human_node)

# We'll always start with a general travel advisor.
builder.add_edge(START, "intent_checker_agent")

checkpointer = MemorySaver()
graph = builder.compile(checkpointer=checkpointer)




thread_config = {"configurable": {"thread_id": uuid.uuid4()}}

def stream_graph_updates(user_input_str: str):
    user_input_dict = {
        "messages": [
            {"role": "user", "content": user_input_str}
        ]
    }

    for update in graph.stream(
        user_input_dict,
        config=thread_config,
        stream_mode="updates",
    ):
        
        for node_id, value in update.items():
            print(node_id, value)
            print("-----------------------------------------------")
            if isinstance(value, dict) and value.get("messages", []):
                for message in value["messages"]:
                    if hasattr(message, 'content') and message.content:  # 檢查是否有 content 屬性且不為空
                        print(message.content)

def main():
    """
    主迴圈：持續詢問使用者輸入，輸入 'quit' / 'exit' / 'q' 時結束。
    """
    while True:
        user_input = input("User: ")
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break

        # 呼叫我們的函式，將使用者輸入丟給 graph
        stream_graph_updates(user_input)

# 執行主函式
if __name__ == '__main__':
    main()
