import os
import autogen
from agents.router_agent import RouterAgent
from agents.faq_agent import FAQAgent
from agents.product_agent import ProductAgent
from agents.order_agent import OrderAgent
from agents.handover_agent import HandoverAgent
from tools.rag_tool import rag_tool
from tools.order_db_tool import order_db_tool
from tools.handover_tool import handover_tool

# --- Configuration ---
# You can load this from a YAML file for production environments
LLM_CONFIG = {
    "model": "gpt-4", # Replace with your preferred model
    "api_key": os.getenv("OPENAI_API_KEY"),
}

# --- Initialize Agents and Tools ---
print("Initializing agents and tools...")

# Initialize Router Agent (UserProxyAgent in AutoGen terms)
router_agent = RouterAgent(
    name="router_agent",
    llm_config=LLM_CONFIG,
    human_input_mode="ALWAYS", # Use "NEVER" for full automation
    is_termination_msg=lambda x: "bye" in x.get("content").lower(),
    function_map={
        "rag_tool": rag_tool,
        "order_db_tool": order_db_tool,
        "handover_tool": handover_tool,
    },
)

# Initialize specialized agents
faq_agent = FAQAgent(
    name="FAQ_Agent",
    llm_config=LLM_CONFIG,
    system_message="You are a helpful assistant specialized in answering FAQ questions. Use the provided tools and information to answer the user's questions about brand, policies, and product warranty. Be concise and friendly."
)

product_agent = ProductAgent(
    name="Product_Agent",
    llm_config=LLM_CONFIG,
    system_message="You are a helpful assistant for product recommendations. Your role is to understand the user's needs, use your tools to find relevant products, and suggest them with clear explanations. Ask for more details if needed."
)

order_agent = OrderAgent(
    name="Order_Agent",
    llm_config=LLM_CONFIG,
    system_message="You are a specialized agent for order and shipping inquiries. You will ask the user for their order ID and then use your tools to provide accurate order status and tracking information."
)

handover_agent = HandoverAgent(
    name="Handover_Agent",
    llm_config=LLM_CONFIG,
    system_message="You are the agent responsible for transferring the user to a human customer service representative. You will summarize the conversation and use your tools to inform the user about the transfer."
)

# --- Define the Group Chat (Workflow) ---
print("Configuring the group chat workflow...")

group_chat = autogen.GroupChat(
    agents=[router_agent, faq_agent, product_agent, order_agent, handover_agent],
    messages=[],
    max_rounds=50,
    allow_repeat_speaker=False,
)

manager = autogen.GroupChatManager(groupchat=group_chat, llm_config=LLM_CONFIG)

# --- Start the Conversation ---
print("Chatbot initialized. Type 'bye' to end the conversation.")
initial_message = "你好，我是 JTCG Shop 的智能客服，請問有什麼需要協助的嗎？"
router_agent.initiate_chat(manager, message=initial_message)