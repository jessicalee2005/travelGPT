from pydantic import BaseModel, Field
from typing import List, Optional


class UserIntent(BaseModel):
    """
    Represents user intent related to travel destinations.
    """

    name: str = Field(
        description="Name of the travel destination that the user is asking about."
    )
    intent: str = Field(
        description="""The topic the user wants to know about the destination. Can be one of the following:
                         - "overview": The user wants to know general information about the destination.
                         - "attractions": The user wants to know about attractions or places to visit.
                         - "weather": The user wants to know about the weather in the destination.
                         - "activities": The user wants to know about activities available in the destination."""
    )
