from gpt4all import GPT4All

class GPT4AllLLM:
    def __init__(self):
        self.model = GPT4All("orca-mini-3b-gguf2-q4_0.gguf")

    def generate(self, prompt):
        return self.model.generate(prompt)
#pip install gpt4all
