class TestModel:
    def __init__(self):
        pass

    @staticmethod
    def transcribe(audio, verbose=False, language="en"):
        return {"text": "This is a model for tests :)", "language": "en"}
