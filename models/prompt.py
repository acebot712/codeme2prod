class Prompt:
    def __init__(self, text, *args, **kwargs):
        self.im_start_token = kwargs.get("IM_START_TOKEN", "<|im_start|>")
        self.im_end_token = kwargs.get("IM_END_TOKEN", "<|im_end|>")
        self.run_prompt_engine = kwargs.get("run_prompt_engine", False)
        self.text = self.prompt_engine(text) if self.run_prompt_engine else text

    def __str__(self):
        return self.text

    def get_text(self):
        return self.text

    def set_text(self, text):
        self.text = text

    def completion_dic_to_chatml(self, completion_dic):
        return (
            self.im_start_token
            + completion_dic.get("role", "user")
            + "\n"
            + completion_dic.get("content", "")
            + "\n"
            + self.im_end_token
            + "\n"
        )

    def prompt_list_to_chatml_list(self, prompt_list):
        for prompt_dic in prompt_list:
            yield self.completion_dic_to_chatml(prompt_dic)

    def prompt_engine(self, prompt):
        prompt_list = [
            {
                "role": "system",
                "content": "You are an AI programming assistant like Codex who gives markdown formatted answers",
            },
        ]
        prompt_list.append({"role": "user", "content": prompt})
        prompt = "".join(self.prompt_list_to_chatml_list(prompt_list))
        return prompt
