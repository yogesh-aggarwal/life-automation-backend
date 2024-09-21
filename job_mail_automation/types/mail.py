from abc import ABC


class MailService(ABC):
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def __str__(self):
        return f"LLM: {self.kwargs}"

    def get_oauth_authorization_url(self):
        raise NotImplementedError

    def send(self, to: str, subject: str, html_body: str):
        raise NotImplementedError
