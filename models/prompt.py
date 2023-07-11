class Prompt:
    def __init__(self, text, context="", *args, **kwargs):
        self.im_start_token = kwargs.get("IM_START_TOKEN", "<|im_start|>")
        self.im_end_token = kwargs.get("IM_END_TOKEN", "<|im_end|>")
        self.run_prompt_engine = kwargs.get("run_prompt_engine", False)
        self.context = context
        # self.text should be at the end
        self.text = self.prompt_engine(text) if self.run_prompt_engine else text

    def __str__(self):
        return self.text

    def get_text(self):
        return self.text

    def get_context(self):
        return self.context

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

    def chatml_to_prompt_list(self, chatml_string):
        prompt_list = []
        def chatml_to_list(string):
            result = []
            start_token = self.im_start_token
            end_token = self.im_end_token
            start_index = 0

            while True:
                start_pos = string.find(start_token, start_index)
                if start_pos == -1:
                    break

                end_pos = string.find(end_token, start_pos + len(start_token))
                if end_pos == -1:
                    break

                substring = string[start_pos + len(start_token):end_pos]
                result.append(substring)

                start_index = end_pos + len(end_token)

            return result
        
        l = chatml_to_list(chatml_string)
        for l1 in l:
            role, content = l1.split("\n", 1)
            chatml_dict = {"role": role.strip(), "content": content.strip()}
            prompt_list.append(chatml_dict)
        return prompt_list

    def prompt_list_to_chatml_list(self, prompt_list):
        for prompt_dic in prompt_list:
            yield self.completion_dic_to_chatml(prompt_dic)

    def prompt_engine(self, prompt):
        prompt_list = [
            {
                "role": "system",
                "content": "Your name is 'CodeMe' and you are an AI programming assistant like Codex who gives markdown formatted answers",
            },
        ]
        prompt_list.append({"role": "user", "content": prompt})
        prompt = (
            self.context
            + "".join(self.prompt_list_to_chatml_list(prompt_list))
            + "\nassistant: AI: "
        )
        # prompt = "".join(self.prompt_list_to_chatml_list(prompt_list))
        return prompt


if __name__ == "__main__":
    chatml_string = Prompt("<|im_start|>assistant\nYou are an AI programming assistant\n")
    print(chatml_string)
    print(repr(chatml_string.get_text()))
    result = chatml_string.chatml_to_completion_dic(chatml_string.get_text())
    print(result)