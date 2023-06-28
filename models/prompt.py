class Prompt:
    def __init__(self, text, context="", *args, **kwargs):
        self.im_start_token = kwargs.get("IM_START_TOKEN", "<|im_start|>")
        self.im_end_token = kwargs.get("IM_END_TOKEN", "<|im_end|>")
        self.run_prompt_engine = kwargs.get("run_prompt_engine", False)
        self.text = self.prompt_engine(text) if self.run_prompt_engine else text
        self.context = context

    def __str__(self):
        return self.text

    def get_text(self):
        return self.text
    
    def get_context(self):
        return self.context

    def set_text(self, text):
        self.text = text

    """
    prompt_engine -> 
    Input:- 
    prompt_list = [
            {
                "role": "system",
                "content": "You are an AI programming assistant like Codex who gives markdown formatted answers",
            },
        ]
    Output:- ChatML
    <|im_start|>system
    You are ChatGPT, a large language model trained by OpenAI. Answer as concisely as possible.
    Knowledge cutoff: 2021-09-01
    Current date: 2023-03-01<|im_end|>
    <|im_start|>user
    How are you<|im_end|>
    <|im_start|>assistant
    I am doing well!<|im_end|>
    <|im_start|>user
    How are you now?<|im_end|>

    prompt_list_to_chatml_list -> 
    Input:- 
    prompt_list = [
            {
                "role": "system",
                "content": "You are an AI programming assistant like Codex who gives markdown formatted answers",
            },
        ]

    Output
    [
        "<|im_start|>assistant\nYou are an AI programming assistant\n<|im_end|>", 
        "<|im_start|>assistant\nYou are an AI programming assistant\n<|im_end|>"
        ]
    completion_dic_to_chatml
    Input:-
    {
                "role": "system",
                "content": "You are an AI programming assistant like Codex who gives markdown formatted answers",
            }

    Output:-
    "<|im_start|>assistant\nYou are an AI programming assistant\n<|im_end|>"
    """

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
        prompt = "".join(self.prompt_list_to_chatml_list(prompt_list)) + "\nassistant: AI: "
        return prompt
