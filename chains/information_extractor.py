from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.utils.openai_functions import convert_pydantic_to_openai_function
from langchain.output_parsers.openai_functions import PydanticOutputFunctionsParser
from utils.tools import get_destination_info, get_travel_guide, get_local_events, get_restaurant_recommendations, get_accommodation_options, get_images
from schema.schema import UserIntent
from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser
from langchain.schema.agent import AgentFinish
from langchain.memory import ConversationBufferWindowMemory
from langchain.tools.render import format_tool_to_openai_function

class Information_Extractor:
    """
    A class used to extract information about travel destinations.

    Attributes
    ----------
    api_key : str
        The API key to access the OpenAI model.
    prompt : ChatPromptTemplate
        The template for the chat prompt.
    functions : list
        A list of functions to format the tools to OpenAI functions.
    model : ChatOpenAI
        The OpenAI chat model.
    chain : langchain.pipeline.Pipeline
        The pipeline to process the chat.

    Methods
    -------
    route(result)
        Routes the result based on its type.
    get_information(user_intent)
        Gets the information about a travel destination based on the user's intent.
    """

    def __init__(self, api_key: str) -> None:
        """
        Constructs all the necessary attributes for the Information_Extractor object.

        Parameters
        ----------
        api_key : str
            The API key to access the OpenAI model.
        """
        self.api_key = api_key
        self.prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                """You are a helpful AI designed to extract information about travel destinations.""",
            ),
            ("user", "{input}"),
        ])
        self.functions = [
            format_tool_to_openai_function(f)
            for f in [get_destination_info, get_travel_guide, get_local_events, get_restaurant_recommendations, get_accommodation_options, get_images]
        ]
        self.model = ChatOpenAI(
            api_key=self.api_key, temperature=0.0, model="gpt-3.5-turbo-0125"
        ).bind(functions=self.functions)
        self.chain = (
            self.prompt | self.model | OpenAIFunctionsAgentOutputParser() | self.route
        )

    def route(self, result):
        """
        Routes the result based on its type.

        Parameters
        ----------
        result : AgentFinish or other
            The result to route.

        Returns
        -------
        str
            The output if the result is an AgentFinish, otherwise runs the tool with the tool input.
        """
        if isinstance(result, AgentFinish):
            return result.return_values["output"]
        else:
            tools = {
                "get_destination_info": get_destination_info,
                "get_travel_guide": get_travel_guide,
                "get_local_events": get_local_events,
                "get_restaurant_recommendations": get_restaurant_recommendations,
                "get_accommodation_options": get_accommodation_options,
                "get_images": get_images
            }
            return tools[result.tool].run(result.tool_input)

    def get_information(self, user_intent: UserIntent) -> str:
        """
        Gets the information about a travel destination based on the user's intent.

        Parameters
        ----------
        user_intent : UserIntent
            The user's intent.

        Returns
        -------
        str
            The information about the travel destination.
        """
        # Assuming user_intent provides details like destination name or ID
        destination_info: str = get_destination_info(user_intent.name)
        input_query = f"I want to know about the travel destination with id {destination_info['id']} or name {destination_info['name']} and want to talk about the {user_intent.intent}."
        information: str = self.chain.invoke({"input": input_query})
        return information
