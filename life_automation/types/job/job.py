from typing import Any

from pydantic import BaseModel, Field


class Job(BaseModel):
    id: str = Field(alias="id", title="Job ID")
    status: str = Field(alias="status", title="Job Status")
    user_id: str = Field(alias="userID", title="User ID")

    date_created: int = Field(alias="dateCreated", title="Date Created")
    date_updated: int = Field(alias="dateUpdated", title="Date Updated")

    system_message: str | None = Field(
        alias="systemMessage", default=None, title="System Message"
    )

    task: str = Field(alias="task", title="Task Description")
    result: Any | None = Field(alias="result", default=None, title="Result")
