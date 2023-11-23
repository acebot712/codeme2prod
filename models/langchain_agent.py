import os
from langchain.agents import load_tools
from langchain.memory import ConversationBufferMemory
from langchain.chat_models import AzureChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import Tool, AgentType, initialize_agent
from langchain.schema import HumanMessage, SystemMessage

class CodeGenerator:
    def __init__(self):
        # Load necessary tools
        tool_names = ["ddg-search", "google-search"]
        self.tools = load_tools(tool_names)

        # Initialize memory and LLM
        self.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        self.llm = AzureChatOpenAI(
            openai_api_base=os.environ.get("OPENAI_API_BASE"),
            deployment_name=os.environ.get("DEPLOYMENT_NAME"),
            openai_api_version=os.environ.get("OPENAI_API_VERSION"),
            openai_api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
            model_name=os.environ.get("MODEL_NAME")
        )

        # Initialize agent chain
        self.agent_chain = initialize_agent(
            self.tools,
            self.llm,
            agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
            memory=self.memory,
            max_iterations=5
        )

        self.agent_chain.agent.llm_chain.prompt.messages[0].prompt.template = os.environ.get("SYSTEM_PROMPT")

    def generate_code(self, prompt):
        # Invoke the agent chain with the provided prompt
        return self.agent_chain.invoke({"input": prompt})["output"]

# Example usage
if __name__ == '__main__':
    generator = CodeGenerator()
    output = generator.generate_code("Tell me more about the latest lamborghini car that got released. Do tell me its release date")
    print(output)
