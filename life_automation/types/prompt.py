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
        self.name = f"{name} Prompt".strip()
        for message in messages:
            self.push(message)

    def push(self, message: LLMMessage):
        # Check: First message must be a system message
        if not len(self.messages) and message.role != "system":
            raise ValueError(f"[{self.name}]: First message must be a system message.")

        # Check: Last message role must be different from the new message role
        if len(self.messages) and self.messages[-1].role == message.role:
            raise ValueError(f"[{self.name}]: Last message role must be different from the new message role.")

        self.messages.append(message)

    def validate_or_raise(self):
        if not len(self.messages):
            raise ValueError(f"[{self.name}]: No messages found.")

        if self.messages[-1].role != "user":
            raise ValueError(f"[{self.name}]: Last message must be a user message.")

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
        self.validate_or_raise()

        return [message.to_dict() for message in self.messages]
