class Model:
    def __init__(self, api_key=None, endpoint=None):
        self.api_key = api_key
        self.endpoint = endpoint

    def generate_code(self, prompt):
        return prompt

    def get_api_key(self):
        return self.api_key
    
    def set_api_key(self, api_key):
        self.api_key = api_key
