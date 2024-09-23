from pydantic import BaseModel, Field

from life_automation.core.firebase import EMAIL_JOBS_COLLECTION

from .job import Job


class EmailJobDetails(BaseModel):
    target_company_name: str = Field(alias="targetCompanyName")

    target_job_id: str = Field(alias="targetJobID")
    target_job_link: str = Field(alias="targetJobLink")
    target_job_title: str = Field(alias="targetJobTitle")
    target_job_description: str = Field(alias="targetJobDescription")

    target_person_name: str = Field(alias="targetPersonName")
    target_person_email: str = Field(alias="targetPersonEmail")
    target_person_position: str = Field(alias="targetPersonPosition")
    target_person_linkedin_profile_content: str = Field(
        alias="targetPersonLinkedinProfileContent"
    )

    resume_url: str = Field(alias="resumeURL")


class EmailJobResult(BaseModel):
    subject: str = Field(alias="subject")
    body: str = Field(alias="body")


class EmailJob(Job):
    date_email_sent: int | None = Field(alias="dateEmailSent", title="Date Email Sent")

    details: EmailJobDetails = Field(alias="details")
    result: EmailJobResult | None = Field(alias="result", default=None)

    def update_status(self, status: str) -> None:
        self.status = status
        EMAIL_JOBS_COLLECTION.document(self.id).update({"status": status})
