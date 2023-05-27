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
                "content": "You are an AI programming assistant.",
            },
            {
                "role": "system",
                "content": "If the user asks for code or technical questions, you must provide code suggestions and adhere to technical information.",
            },
            {
                "role": "system",
                "content": "Think of a step by step approach to the problem and give a code implementation first. Then describe your approach in great detail.",
            },
            {
                "role": "system",
                "content": "Then output the code in a single code block.",
            },
            {
                "role": "system",
                "content": "Use markdown formatting in your answers with really small headings.",
            },
            {
                "role": "system",
                "content": "Avoid wrapping the whole response in triple backticks.",
            },
            {
                "role": "system",
                "content": "If you are asked to explain code then use bullet points",
            },
            {
                "role": "system",
                "content": "If you are asked to debug code then think carefully and describe what is wrong with the code in question.",
            },
            {
                "role": "system",
                "content": "If you have nothing to say, then say 'I don't know the answer to your question.'",
            },
        ]
        prompt_list.append({"role": "user", "content": prompt})
        prompt = "".join(self.prompt_list_to_chatml_list(prompt_list))
        return prompt
