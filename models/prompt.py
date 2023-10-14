from .advanced_prompt_generator import generate_advanced_prompt
class Prompt:
    def __init__(self, text, context="", **kwargs):
        """
        Initialize the Prompt object.

        :param text: The main text of the prompt.
        :param context: Additional context for the prompt.
        :param kwargs: Additional keyword arguments.
        """
        self.im_start_token = kwargs.get("IM_START_TOKEN", "<start>")
        self.im_end_token = kwargs.get("IM_END_TOKEN", "<end>")
        self.run_prompt_engine = kwargs.get("run_prompt_engine", False)
        self.context = context
        text = generate_advanced_prompt(text)
        self.text = self.prompt_engine(text) if self.run_prompt_engine else text

    def __str__(self):
        """
        Returns the string representation of the Prompt object.
        """
        return self.text

    def get_text(self):
        """
        Retrieves the main text of the prompt.
        """
        return self.text

    def get_context(self):
        """
        Retrieves the context associated with the prompt.
        """
        return self.context

    def completion_dic_to_chatml(self, completion_dic):
        """
        Convert a dictionary of completions to ChatML format.

        :param completion_dic: Dictionary containing role and content.
        :return: A ChatML formatted string.
        """
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
        """
        Converts a ChatML string to a list of prompt dictionaries.

        :param chatml_string: Input string in ChatML format.
        :return: A list of dictionaries with role and content.
        """
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
        prompt_list = [{"role": role.strip(), "content": content.strip()} for role, content in [l1.split("\n", 1) for l1 in l]]
        return prompt_list

    def prompt_list_to_chatml_list(self, prompt_list):
        """
        Converts a list of prompt dictionaries to a ChatML formatted string.

        :param prompt_list: List of dictionaries with role and content.
        :return: A generator yielding ChatML formatted strings.
        """
        for prompt_dic in prompt_list:
            yield self.completion_dic_to_chatml(prompt_dic)

    def prompt_engine(self, prompt):
        """
        Generates a full prompt including system and user roles.

        :param prompt: The main user prompt.
        :return: A ChatML formatted string.
        """
        prompt_list = [
            {
                "role": "system",
                "content": "Your name is 'CodeMe' and you are an AI programming assistant like Codex who gives markdown formatted answers",
            },
            {"role": "user", "content": prompt}
        ]
        full_prompt = self.context + "".join(self.prompt_list_to_chatml_list(prompt_list)) + "\nassistant: AI: "
        return full_prompt


if __name__ == "__main__":
    # Example usage:
    chatml_instance = Prompt(
        text="assistant\nYou are an AI programming assistant\n",
        IM_START_TOKEN="<start>",
        IM_END_TOKEN="<end>",
        run_prompt_engine=True
    )
    print(chatml_instance)  # Display the generated ChatML formatted string
    print(repr(chatml_instance.get_text()))  # Display the raw text for verification

    # Convert back to dictionary representation
    result = chatml_instance.chatml_to_prompt_list(chatml_instance.get_text())
    print(result)  # Display the list of role-content dictionaries
