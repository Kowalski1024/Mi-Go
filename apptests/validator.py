import argparse
import importlib.util
import pprint

from src.transcript_test import TranscriptTest


class ModelClassValidator:
    def __init__(self, model: TranscriptTest):
        if not isinstance(model, TranscriptTest):
            raise TypeError("model must be instance of TranscriptTest class")

        self.model_instance = model

    def check_attributes(self) -> dict:
        expected_attributes = ["transcriber", "differ", "normalizer"]

        for e in expected_attributes:
            if (
                not hasattr(self.model_instance, e)
                or getattr(self.model_instance, e) is None
            ):
                raise AttributeError(f"model must have {e} attribute")

    def run_transcribe(self) -> str:
        returned_transcript = self.model_instance.transcribe("apptests/data/sample.mp3")

        if type(returned_transcript) is not str:
            raise TypeError("transcribe method must return str")

        return returned_transcript

    def run_compare(self, model_transcript: str, target_transcript: str) -> dict:
        print(f"Target transcript:\n{target_transcript}\n")
        print(f"Model transcript:\n{model_transcript}\n")

        differ_results = self.model_instance.compare(
            model_transcript, target_transcript
        )

        if type(differ_results) is not dict:
            raise TypeError("compare method must return dict")

        print("Differ results:")
        pprint.pprint(differ_results)
        print()

        return differ_results

    def run_additional_info(self) -> dict:
        except_attributes = ["modelName", "language"]
        additional_info = self.model_instance.additional_info()

        if type(additional_info) is not dict:
            raise TypeError("additional_info method must return dict")

        for e in except_attributes:
            if not e in additional_info:
                raise AttributeError(f"additional_info must have {e} attribute")

    def check_model(self) -> dict:
        self.check_attributes()
        model_transcript = self.run_transcribe()
        target_transcript = self.get_yt_transcript()
        self.run_compare(model_transcript, target_transcript)
        self.run_additional_info()

        print("Model is ready to use!")

    @staticmethod
    def get_yt_transcript() -> str:
        with open("data/transcript.txt", "r") as file:
            content = file.read()
            return content


def main():
    parser = argparse.ArgumentParser(
        prog="Models class validator",
        description="Test if user model class is ready to use",
    )
    parser.add_argument(type=str, dest="module_name", help="Module name")
    parser.add_argument(type=str, dest="class_name", help="Class name")

    args, extra_args = parser.parse_known_args()

    spec = importlib.util.spec_from_file_location("model.test", args.module_name)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    model_cls = getattr(module, args.class_name)

    model_parser = argparse.ArgumentParser()
    model_cls.subparser(model_parser)
    model_args = model_parser.parse_args(extra_args, namespace=args)

    model = model_cls(**vars(model_args))

    mc = ModelClassValidator(model)
    mc.check_model()


if __name__ == "__main__":
    main()
