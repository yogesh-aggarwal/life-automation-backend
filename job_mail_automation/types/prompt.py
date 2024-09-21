import shutil


class LLMMessage:
    role: str
    content: str

    def __init__(self, role: str, content: str):
        self.role = role
        self.content = content

    def __str__(self):
        return f"{self.role}:\t {self.content}"

    def __repr__(self):
        return self.__str__()

    def to_dict(self):
        return {"role": self.role, "content": self.content}


class LLMPrompt:
    name: str
    messages: list[LLMMessage] = []

    def __init__(self, name: str, messages: list[LLMMessage]):
        self.name = name
        self.messages = messages

    def push(self, message: LLMMessage):
        self.messages.append(message)

    def __str__(self):
        size = shutil.get_terminal_size((80, 20)).columns
        separator = "=" * size

        result = separator
        result += f"\n{self.name}:"
        for message in self.messages:
            result += f"\n[{message.role.center(8, ' ')}] {message.content}"
        result += f"\n{separator}"
        return result

    def __repr__(self):
        return self.__str__()

    def to_dict(self):
        return [message.to_dict() for message in self.messages]
