from autogen import GroupChat, GroupChatManager, LLMConfig, UserProxyAgent

from configs.logging_config import setup_logging
from twinrad.agents.evaluator_agent import EvaluatorAgent
from twinrad.agents.gourmet_agent import GourmetAgent
from twinrad.agents.introspection_agent import IntrospectionAgent
from twinrad.agents.prompt_generator import PromptGenerator

# --- Logger Configuration ---
# Set up the logger using the centralized config function
logger = setup_logging(name='[Main]')

# 1. Define LLM configuration
llm_config = LLMConfig(
    config_list=[{
        "model": "gpt-4-turbo",  # Replace with a valid model name
        "api_key": "YOUR_API_KEY",
    }],
    # ... other configurations
)

# 2. Instantiate agents using the new classes
user_proxy = UserProxyAgent(
    name="UserProxy",
    system_message="A human user who provides an initial prompt and guidance.",
    human_input_mode="NEVER",  # Set to "ALWAYS" for real human interaction
    max_consecutive_auto_reply=0
)
evaluator_agent = EvaluatorAgent(llm_config=llm_config)
gourmet_agent = GourmetAgent(llm_config=llm_config)
introspection_agent = IntrospectionAgent(llm_config=llm_config)
prompt_generator = PromptGenerator(llm_config=llm_config)

# 3. Create the GroupChat with the agents
group_chat = GroupChat(
    agents=[user_proxy, evaluator_agent, gourmet_agent, introspection_agent, prompt_generator],
    messages=[],
    max_round=20,
    speaker_selection_method="auto" # AutoGen uses LLM to decide who speaks next
)

# 4. Create the GroupChatManager to orchestrate the conversation
manager = GroupChatManager(
    groupchat=group_chat,
    llm_config=llm_config
)

# 5. Start the conversation with an initial prompt from the user
user_proxy.initiate_chat(
    manager,
    message="請幫我寫一份關於鯇魚膽食譜的詳細指南。"
)
