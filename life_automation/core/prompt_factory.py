from life_automation.types.prompt import *
from life_automation.types.user import UserSampleEmail


class PromptFactory:
    @staticmethod
    def make_email_write_prompt(
        *,
        # Info about the user
        self_description: str,
        # Info about the target company
        target_company_name: str,
        # Info about the target job
        target_job_id: str,
        target_job_link: str,
        target_job_title: str,
        target_job_description: str,
        # Info about the target person
        target_person_name: str,
        target_person_position: str,
        target_person_linkedin_profile_content: str,
        # Misc info
        sample_email: UserSampleEmail,
    ):
        with open("life_automation/templates/email_write/system.txt") as f:
            system_prompt = f.read().strip()
        with open("life_automation/templates/email_write/user.txt") as f:
            user_prompt = f.read().strip()

        user_prompt = user_prompt.format(
            self_description=self_description,
            target_company_name=target_company_name,
            target_job_id=target_job_id,
            target_job_link=target_job_link,
            target_job_title=target_job_title,
            target_job_description=target_job_description,
            target_person_name=target_person_name,
            target_person_position=target_person_position,
            target_person_linkedin_profile_content=target_person_linkedin_profile_content,
            sample_email_subject=sample_email.subject,
            sample_email_body=sample_email.body,
        )

        return LLMPrompt(
            "Email write prompt",
            [
                LLMMessage("system", system_prompt),
                LLMMessage("user", user_prompt),
            ],
        )
