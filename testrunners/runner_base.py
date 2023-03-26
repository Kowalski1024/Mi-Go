import argparse
from collections import defaultdict

from loguru import logger

from testrunners.tests import TranscriptTestBase


class TestRegistry:
    _registry = defaultdict(list)

    @classmethod
    def register(cls, *tests):
        def _register_test(test_runner):
            cls._registry[test_runner].extend(tests)
            return test_runner

        return _register_test

    @classmethod
    def get_registry(cls, test_runner):
        return cls._registry[test_runner]


class TestRunnerBase:
    def __init__(self, tester: TranscriptTestBase, **kwargs):
        self.tester = tester

    def run(self):
        raise NotImplementedError

    @staticmethod
    def runner_args(parser: argparse.ArgumentParser):
        pass

    @classmethod
    def from_command_line(cls):
        args, unknown = cls.parser().parse_known_args()
        logger.info(f"Command line args: {vars(args)}")
        tester = [x for x in TestRegistry.get_registry(cls) if x.__name__ == args.test_class][0]
        logger.info(f"Chosen tester name: {tester.__name__}")
        return cls(**vars(args), tester=tester(**vars(args)))

    @classmethod
    def parser(cls):
        parser = argparse.ArgumentParser()
        cls.runner_args(parser)

        if registry := TestRegistry.get_registry(cls):
            subparsers = parser.add_subparsers(required=True, help="Select the test you want to run", dest="test_class")

            for test in registry:
                subparser = subparsers.add_parser(test.__name__)
                test.subparser(subparser)
        else:
            raise ValueError(f"Registry is empty, no test classes was found for {cls}")

        return parser
