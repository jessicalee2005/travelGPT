from pydantic import BaseModel, Field
from typing import List, Optional


class UserIntent(BaseModel):
    """Tag the text with the following information.
    If you are not sure, you can leave the field empty.
    """

    name: str = Field(
        description="Name of the movie or the series that the user is talking about."
    )
    intent: str = Field(
        description="""The topic the user wants to talk about. Can be one of the following:
                         - "plot": The user wants to know the plot of the movie or the series.
                         - "cast": The user wants to know the cast of the movie or the series.
                         - "rating": The user wants to know the rating of the movie or the series.
                         - "awards": The user wants to know the awards of the movie or the series."""
    )
