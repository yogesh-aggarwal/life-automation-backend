from pydantic import BaseModel, Field

from life_automation.core.firebase import PUBLISHING_JOBS_COLLECTION

from .job import Job


class PublishingJobDetails(BaseModel):
    title: str = Field(..., title="Title of the post", alias="title")
    content: str = Field(..., title="Markdown content of the post", alias="content")
    tags: list[str] = Field(..., title="Tags for the post", alias="tags")
    canonical_url: str = Field(
        ..., title="Canonical URL of the post", alias="canonicalURL"
    )
    visibility: str = Field(..., title="Visibility of the post", alias="visibility")


class PublishingJobResult(BaseModel):
    url: str = Field(..., title="URL of the published post")


class PublishingJob(Job):
    details: PublishingJobDetails = Field(alias="details")
    result: PublishingJobResult | None = Field(alias="result", default=None)

    def update_status(
        self,
        status: str,
        result: PublishingJobResult | None,
        system_message: str | None,
    ) -> None:
        self.status = status
        PUBLISHING_JOBS_COLLECTION.document(self.id).update(
            {
                "status": status,
                "result": result,
                "systemMessage": system_message,
            }
        )
