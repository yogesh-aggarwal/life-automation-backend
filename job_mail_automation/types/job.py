from pydantic import BaseModel, Field


class JobDetails(BaseModel):
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


class JobResult(BaseModel):
    subject: str = Field(alias="subject")
    body: str = Field(alias="body")


class Job(BaseModel):
    id: str = Field(alias="id")
    status: str = Field(alias="status")
    user_id: str = Field(alias="userID")

    task: str = Field(alias="task")

    date_created: int = Field(alias="dateCreated")
    date_updated: int = Field(alias="dateUpdated")
    date_email_sent: int | None = Field(alias="dateEmailSent")

    details: JobDetails = Field(alias="details")
    result: JobResult | None = Field(alias="result", default=None)
    system_message: str | None = Field(alias="systemMessage", default=None)
