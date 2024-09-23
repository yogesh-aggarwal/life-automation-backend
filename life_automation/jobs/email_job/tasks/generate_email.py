import json

from life_automation.core.firebase import USERS_COLLECTION
from life_automation.core.prompt_factory import PromptFactory
from life_automation.services.llm.gpt4omini import GPT4oMini
from life_automation.types.job.email_job import EmailJob
from life_automation.types.user import User


def generate_email_task(job: EmailJob) -> tuple[str, str]:
    # Step 1: Get user details
    try:
        user = User.model_validate(
            USERS_COLLECTION.document(job.user_id).get().to_dict()
        )
    except Exception as e:
        raise Exception(f"Failed to fetch user details: {e}")

    # Step 2: Prepare email
    prompt = PromptFactory.make_email_write_prompt(
        # User details
        self_description=user.data.self_description,
        sample_email=user.data.sample_email,
        # Company details
        target_company_name=job.details.target_company_name,
        # Job details
        target_job_id=job.details.target_job_id,
        target_job_link=job.details.target_job_link,
        target_job_title=job.details.target_job_title,
        target_job_description=job.details.target_job_description,
        # Prospect details
        target_person_name=job.details.target_person_name,
        target_person_position=job.details.target_person_position,
        target_person_linkedin_profile_content=job.details.target_person_linkedin_profile_content,
    )
    for _ in range(5):
        try:
            llm = GPT4oMini()
            res = llm.run(prompt)
            if res is None:
                raise Exception("LLM failed to generate content")
            res = json.loads(res)

            return res["subject"].strip(), res["body"].strip()
        except Exception as e:
            print(f"LLM failed with exception: {e}")

    raise Exception("LLM failed to generate content")
