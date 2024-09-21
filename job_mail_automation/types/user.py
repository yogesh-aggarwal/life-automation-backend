from pydantic import BaseModel, Field

from job_mail_automation.core.firebase import auth, db


class UserSampleEmail(BaseModel):
    subject: str = Field(..., alias="subject")
    body: str = Field(..., alias="body")


class UserResume(BaseModel):
    title: str = Field(..., alias="title")
    url: str = Field(..., alias="url")
    date_created: int = Field(..., alias="dateCreated")


class UserOAuthCredentials(BaseModel):
    token: str = Field(..., alias="token")
    refresh_token: str = Field(..., alias="refresh_token")


class User(BaseModel):
    id: str = Field(..., alias="id")
    dp: str = Field(..., alias="dp")
    email: str = Field(..., alias="email")
    name: str = Field(..., alias="name")

    oauth_credentials: UserOAuthCredentials | None = Field(
        ..., alias="oauthCredentials"
    )

    self_description: str = Field(..., alias="selfDescription")
    sample_email: UserSampleEmail = Field(..., alias="sampleEmail")

    resumes: list[UserResume] = Field(..., alias="resumes")

    @staticmethod
    def create(id: str, email: str, name: str, dp: str):
        with open("job_mail_automation/templates/sample_email.txt") as f:
            sample_email_body = f.read().strip()

        user = User.model_validate(
            {
                "id": id,
                "email": email,
                "dp": dp,
                "name": name,
                "oauthCredentials": None,
                "selfDescription": "",
                "sampleEmail": {
                    "subject": "Referral request for a recent Backend Engineer job role (#3968102214)",
                    "body": sample_email_body,
                },
                "resumes": [],
            }
        )

        db.collection("users").document(user.id).set(user.model_dump(by_alias=True))

        # try:
        #     auth.create_user(
        #         uid=user.id,
        #         display_name=user.name,
        #         email=user.email,
        #         photo_url=user.dp,
        #         email_verified=True,
        #         password="thispasswordisinsecure",

        #     )
        # except Exception as e:
        #     print(e)

        return user

    def update_oauth(self, creds: UserOAuthCredentials | None):
        self.oauth_credentials = creds

        db.collection("users").document(self.id).update(
            {
                "oauthCredentials": creds.model_dump(by_alias=True) if creds else None,
            }
        )
