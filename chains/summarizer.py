from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain.memory import ConversationBufferWindowMemory

class Summarizer:
    """
    A class used to summarize context and answer questions using OpenAI's GPT-3.5 model.

    Attributes
    ----------
    api_key : str
        The API key to access the OpenAI model.
    prompt : ChatPromptTemplate
        The template for the chat prompt.
    model : ChatOpenAI
        The OpenAI chat model.
    output_parser : StrOutputParser
        The parser to parse the output of the OpenAI model.
    chain : langchain.pipeline.Pipeline
        The pipeline to process the chat.

    Methods
    -------
    summarize(context, question)
        Summarizes the context and answers the question.
    """

    def __init__(self, api_key: str) -> None:
        """
        Constructs all the necessary attributes for the Summarizer object.

        Parameters
        ----------
        api_key : str
            The API key to access the OpenAI model.
        """
        self.api_key = api_key
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful AI that can answer user's questions based on the provided context."),
            ("user", "{input}"),
        ])
        self.model = ChatOpenAI(
            api_key=self.api_key,
            temperature=0.0,
            model="gpt-3.5-turbo-0125",
            streaming=True,
        )
        self.output_parser = StrOutputParser()
        self.chain = self.prompt | self.model | self.output_parser

    def summarize(self, context: str, question: str) -> str:
        """
        Summarizes the context and answers the question.

        Parameters
        ----------
        context : str
            The context to summarize.
        question : str
            The question to answer.

        Returns
        -------
        str
            The summary of the context and the answer to the question.
        """
        try:
            response = self.chain.invoke({
                "input": f"Context: {context} Question: {question}"
            })
            return response
        except Exception as e:
            return f"Error: {str(e)}"
