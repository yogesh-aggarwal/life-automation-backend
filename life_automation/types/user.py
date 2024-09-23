from google.cloud.firestore_v1.base_query import FieldFilter
from pydantic import BaseModel, Field

from life_automation.core.firebase import USERS_COLLECTION, auth, db


class UserSampleEmail(BaseModel):
    subject: str = Field(..., alias="subject")
    body: str = Field(..., alias="body")


class UserResume(BaseModel):
    title: str = Field(..., alias="title")
    url: str = Field(..., alias="url")
    date_created: int = Field(..., alias="dateCreated")


class UserOAuthCredentials(BaseModel):
    access_token: str = Field(..., alias="access_token")
    refresh_token: str = Field(..., alias="refresh_token")


class UserCredentials(BaseModel):
    google_oauth: UserOAuthCredentials | None = Field(..., alias="googleOAuth")
    medium_oauth: UserOAuthCredentials | None = Field(..., alias="mediumOAuth")


class UserData(BaseModel):
    self_description: str = Field(..., alias="selfDescription")
    sample_email: UserSampleEmail = Field(..., alias="sampleEmail")

    resumes: list[UserResume] = Field(..., alias="resumes")


class User(BaseModel):
    id: str = Field(..., alias="id")
    dp: str = Field(..., alias="dp")
    email: str = Field(..., alias="email")
    name: str = Field(..., alias="name")

    data: UserData = Field(..., alias="data")
    credentials: UserCredentials = Field(..., alias="credentials")

    @staticmethod
    def get_from_email(email: str):
        user = USERS_COLLECTION.where(filter=FieldFilter("email", "==", email)).get()
        if not user:
            raise ValueError(f"User with email {email} not found")
        user = user[0].to_dict()

        return User.model_validate(user)

    @staticmethod
    def create(id: str, email: str, name: str, dp: str, password: str):
        with open("life_automation/templates/sample_email.txt") as f:
            sample_email_body = f.read().strip()

        user = User(
            id=id,
            email=email,
            dp=dp,
            name=name,
            data=UserData(
                selfDescription="",
                sampleEmail=UserSampleEmail(
                    subject="Referral request for a recent Backend Engineer job role (#3968102214)",
                    body=sample_email_body,
                ),
                resumes=[],
            ),
            credentials=UserCredentials(
                googleOAuth=None,
                mediumOAuth=None,
            ),
        )

        USERS_COLLECTION.document(user.id).set(user.model_dump(by_alias=True))

        try:
            auth.create_user(
                uid=user.id,
                display_name=user.name,
                email=user.email,
                photo_url=user.dp,
                email_verified=True,
                password=password,
            )
        except Exception as e:
            print(e)

        return user

    def update_creds_google_oauth(self, creds: UserOAuthCredentials | None):
        self.credentials.google_oauth = creds
        USERS_COLLECTION.document(self.id).set(self.model_dump(by_alias=True))

    def update_creds_medium_oauth(self, creds: UserOAuthCredentials | None):
        self.credentials.medium_oauth = creds
        USERS_COLLECTION.document(self.id).set(self.model_dump(by_alias=True))
