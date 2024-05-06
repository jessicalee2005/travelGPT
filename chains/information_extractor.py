from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.utils.openai_functions import convert_pydantic_to_openai_function
from langchain.output_parsers.openai_functions import PydanticOutputFunctionsParser
from utils.tools import get_id, get_cast_details, get_awards, get_plot, get_info, get_images
from utils.tools import (
    GetAwardsInput,
    GetCastDetailsInput,
    GetRatingInput,
    GetPlotInput,
    GetInfo
)
from langchain.tools.render import format_tool_to_openai_function
from schema.schema import UserIntent
from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser
from langchain.schema.agent import AgentFinish
from langchain.memory import ConversationBufferWindowMemory


class Information_Extractor:
    """
    A class used to extract information about movies and TV shows.

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
        Gets the information about a movie or TV show based on the user's intent.
    """

    def __init__(self, api_key) -> None:
        """
        Constructs all the necessary attributes for the Information_Extractor object.

        Parameters
        ----------
            api_key : str
                The API key to access the OpenAI model.
        """
        self.api_key = api_key
        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """You are a helpful ai designed to extract information about movies and TV shows.
                    """,
                ),
                ("user", "{input}"),
            ]
        )
        self.functions = [
            format_tool_to_openai_function(f)
            for f in [get_cast_details, get_awards, get_plot, get_info, get_images]
        ]
        self.model = ChatOpenAI(
            api_key=self.api_key, temperature=0.0, model="gpt-3.5-turbo-0125"
        ).bind(functions=self.functions)
        # self.output_parser = PydanticOutputFunctionsParser()
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
        #print(result)
        if isinstance(result, AgentFinish):
            return result.return_values["output"]
        else:
            tools = {
                "get_info": get_info,
                "get_plot": get_plot,
                "get_cast_details": get_cast_details,
                # "get_rating": get_rating,
                "get_awards": get_awards,
                "get_images": get_images
            }
            return tools[result.tool].run(result.tool_input)

    def get_information(self, user_intent: UserIntent) -> str:
        """
        Gets the information about a movie or TV show based on the user's intent.

        Parameters
        ----------
            user_intent : UserIntent
                The user's intent.

        Returns
        -------
            str
                The information about the movie or TV show.
        """
        #get_id(user_intent.name)
        movie_info: str = get_info(user_intent.name)
        input_query = f"I want to know about the movie with id {movie_info['id']} or name {movie_info['title']} and want to talk about the {user_intent.intent}."
        information: str = self.chain.invoke({"input": input_query})
        return information
