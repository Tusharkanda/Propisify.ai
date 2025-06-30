from dotenv import load_dotenv
import os
from langgraph.graph import StateGraph, START, END
from langgraph.types import Interrupt, interrupt, Command
from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, ToolMessage
from operator import add as add_messages
from langchain_openai import AzureChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode
from data_manager import DataManager
from langgraph.checkpoint.memory import MemorySaver
from typing import Union
import pypandoc
from pathlib import Path
import datetime
import uuid

load_dotenv()

# Initialize the OpenAI LLM
from pydantic import SecretStr

LLM = AzureChatOpenAI(
    api_key=SecretStr(os.getenv("AZURE_OPENAI_API_KEY") or ""),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview"),
    temperature=0.01,
)

# Create the DataManager instance
dm = DataManager(persist_directory="./chromadb_data") 
dm.initialize_database()

@tool
def retrieve_proposals(query: str, industry: Union[str, None] = None, service_type: Union[str, None] = None) -> str:
    """
    Retrieve proposals from the database based on a query.
    Args:
        query (str): The search query to find relevant proposals.
    Returns:
        str: A formatted string of retrieved proposal summaries.
    """
    try:
        results = dm.search_similar_proposals(
            query=query,
        )

        if not results:
            return "No proposals found matching your query."
        
        return "\n".join([f"{i+1}. {res['text']}" for i, res in enumerate(results)])
    
    except Exception as e:
        return f"Error retrieving proposals: {str(e)}"
    

@tool
def download_proposal_or_contract(file_content_md: str, client_name: str = "client") -> str:
    '''
    Download the proposal or contract content as a .docx file.
    Args:
        file_content_md (str): The content of the proposal or contract to be downloaded in markdown.
        client_name (str): The client name to use in the filename.
    Returns:
        str: The path to the downloaded .docx file or an error message.
    '''
    try:
        downloads_path = Path.home() / "Downloads"
        now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_client = "".join(c for c in client_name if c.isalnum() or c in (' ', '_')).rstrip().replace(" ", "_")
        filename = downloads_path / f"{safe_client}_{now}.docx"
        pypandoc.convert_text(file_content_md, to='docx', format='md', outputfile=str(filename))
        return f"File successfully downloaded to: {filename}"
    except Exception as e:
        return f"Error downloading file: {str(e)}"
tools = [retrieve_proposals, download_proposal_or_contract]
LLM = LLM.bind_tools(tools)
# print(f"{LLM.bound}")  # Removed: LLM has no attribute 'bound'

class AgentState(TypedDict):
    """
    State for the AI agent.
    """
    messages: Annotated[Sequence[BaseMessage], add_messages]

system_prompt = """
You are an expert business proposal and contract writer.
Your task is to revise and improve proposals or contracts based on the latest client feedback and by referencing relevant examples from the proposal/contract database.

Instructions:

Carefully analyze the client's feedback and requirements.
Retrieve and review similar proposals or contracts from the database to guide your revisions in terms of structure, tone, and content.
Integrate the client's feedback and any new requirements into the revised document.
Ensure the revised proposal or contract is clear, professional, and tailored to the client's industry and needs.
If any information is unclear or missing, ask for clarification before proceeding.
Maintain a positive, confident, and business-appropriate tone throughout.
Your goal is to deliver a revised proposal or contract that fully addresses the client's feedback and leverages best practices from previous successful documents.  
"""

def LLM_response(state: AgentState) -> AgentState:
    """
    Generate a response from the LLM based on the current state.
    Args:
        state (AgentState): The current state of the agent.
    Returns:
        AgentState: Updated state with the LLM's response.
    """
    # Prepare the messages for the LLM
    messages = list(state['messages'])
    
    # Generate the response
    messages = [SystemMessage(content=system_prompt)] + messages
    response = LLM.invoke(messages)
    

    return {'messages': [response]}

def wait_for_human_response(state: AgentState) -> AgentState:
    """
    Pauses the graph and waits for human input from the frontend.
    The payload can include any info you want to show the user.
    """
    
    payload = {
        "messages": state['messages'],
        "instructions": "Please review the proposal and provide your feedback or additional requirements.",
    }

    human_message = interrupt(payload)

    return {'messages': human_message}


graph = StateGraph(AgentState)

graph.add_node("LLM", LLM_response)
graph.add_node("Human", wait_for_human_response)

retrieveProposalToolNode = ToolNode(tools=[retrieve_proposals])
downloadFileToolNode = ToolNode(tools=[download_proposal_or_contract])

graph.add_node("retrieveProposalToolNode", retrieveProposalToolNode)
graph.add_node("downloadFileToolNode", downloadFileToolNode)

graph.add_edge(START, "LLM")
graph.add_edge("Human", "LLM")
graph.add_edge("retrieveProposalToolNode", "LLM")
graph.add_edge("downloadFileToolNode", "LLM")

def direct_to_next_node(state: AgentState) -> str:
    """
    Directs the flow to the next node based on the state.
    If the state contains a human message, it goes to 'Human', otherwise
    it goes back to 'LLM'.
    """

    messages = list(state['messages'])
    finalMessage = messages[-1] if messages else None

    tool_calls = getattr(finalMessage, "tool_calls", None)
    if tool_calls:
        for call in tool_calls:
            if call.get("name") == "retrieve_proposals":
                return "retrieveProposalToolNode"
            elif call.get("name") == "download_proposal_or_contract":
                return "downloadFileToolNode"
        # If tool_calls exist but none match, default to "Human"
        return "Human"
    else:
        return "Human"

graph.add_conditional_edges(
    "LLM",
    direct_to_next_node,
    {
        "Human": "Human",
        "retrieveProposalToolNode": "retrieveProposalToolNode",
        "downloadFileToolNode": "downloadFileToolNode",
        END: END
    }
)

checkpointer = MemorySaver()
app = graph.compile(checkpointer=checkpointer)

export = app # Export the app for use in other modules
# This allows the app to be used in a web framework or other interfaces.