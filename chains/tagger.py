from operator import itemgetter
from langchain_community.chat_models import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.utils.openai_functions import convert_pydantic_to_openai_function
from langchain.output_parsers.openai_functions import PydanticOutputFunctionsParser
from schema.schema import TravelIntent  # Assuming TravelIntent schema for travel-related queries
from langchain.memory import ConversationBufferMemory
from langchain_core.runnables import RunnableLambda, RunnablePassthrough


class Tagger:
    """
    A class responsible for tagging and extracting important information about travel destinations from user input.

    Attributes:
        api_key (str): The API key used for authentication with the OpenAI API.
        prompt (ChatPromptTemplate): An instance of ChatPromptTemplate that defines the conversation prompt.
        functions (list): A list of functions converted to OpenAI format for use in the GPT-3 model.
        model (ChatOpenAI): An instance of ChatOpenAI that handles the interaction with the GPT-3 model.
        conversation_buffer (ConversationBufferMemory): A buffer for storing conversation history.
        parser (PydanticOutputFunctionsParser): A parser for parsing the output from the GPT-3 model.
        chain (Chain): A chain of operations to perform on the user input.
    """

    def __init__(self, api_key: str) -> None:
        """
        Initializes the Tagger with the given API key and sets up the necessary components for tagging and information extraction.

        Args:
            api_key (str): The API key used for authentication with the OpenAI API.
        """
        self.api_key = api_key
        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """You are a helpful AI that can tag and extract important information about travel destinations from the user's input. 
                    """,
                ),
                MessagesPlaceholder(variable_name="history"),
                ("user", "{input}"),
            ]
        )

        self.functions = [convert_pydantic_to_openai_function(TravelIntent)]

        self.model = ChatOpenAI(
            api_key=self.api_key, temperature=0.0, model="gpt-3.5-turbo-0125"
        ).bind(functions=self.functions)

        self.conversation_buffer = ConversationBufferMemory(return_messages=True)
        self.parser = PydanticOutputFunctionsParser(
            pydantic_schema={"TravelIntent": TravelIntent}
        )

        self.chain = (
            RunnablePassthrough.assign(
                history=RunnableLambda(self.conversation_buffer.load_memory_variables)
                | itemgetter("history")
            )
            | self.prompt
            | self.model
            | self.parser
        )

    def extract_information(self, input: str) -> TravelIntent:
        """
        Extracts the intent related to travel destinations from the user's input using the GPT-3 model.

        Args:
            input (str): The user's input string.

        Returns:
            TravelIntent: An object containing the extracted intent related to travel destinations.
        """
        self.conversation_buffer.load_memory_variables({})
        intent: TravelIntent = self.chain.invoke(
            {
                "input": f"Extract the intent related to travel destinations from the user's input. {input}"
            },
        )
        self.conversation_buffer.save_context(
            {"input": input},
            {
                "output": f"User wants to know about {intent.intent} related to {intent.destination}."
            },
        )
        print(intent)
        return intent
