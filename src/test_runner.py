import argparse
import pprint
import time
from collections import defaultdict

from loguru import logger

from .transcript_test import TranscriptTest


class TestRegistry:
    """
    Registry for tests, use this to register tests in the test runners
    """

    _registry = defaultdict(list)

    @classmethod
    def register(cls, *tests) -> callable:
        """
        Decorator for registering tests

        Args:
            tests: tests to register
        """

        def _register_test(test_runner):
            cls._registry[test_runner].extend(tests)
            return test_runner

        return _register_test

    @classmethod
    def get_registry(cls, test_runner) -> list[TranscriptTest]:
        """
        Get the registry for a test runner

        Args:
            test_runner: test runner to get the registry for

        Returns:
            registry for the test runner
        """
        return cls._registry[test_runner]


class TestRunner:
    """
    Base class for test runners, all test runners should inherit from this class
    """

    def __init__(self, tester: TranscriptTest, **kwargs):
        self.tester = tester 

    def run(self) -> None:
        """
        Main method for running the test
        """
        raise NotImplementedError

    @staticmethod
    def runner_args(parser: argparse.ArgumentParser) -> None:
        """
        Use this method to add arguments to the parser

        Args:
            parser: parser to add arguments to
        """
        pass

    @classmethod
    def from_command_line(cls) -> "TestRunner":
        """
        Creates a test runner from command line arguments
        """

        args, unknown = cls.parser().parse_known_args()
        logger.info(f"Command line args:\n{pprint.pformat(vars(args))}")

        # Get the tester class from the registry
        tester = [
            x for x in TestRegistry.get_registry(cls) if x.__name__ == args.test_class
        ][0]
        logger.info(f"Chosen tester name: {tester.__name__}")

        obj = cls(**vars(args), tester=tester(**vars(args)))
        logger.add(f"output/logs/{repr(obj)}_{time.strftime('%Y%m%d-%H%M%S')}.log")
        return obj

    @classmethod
    def parser(cls) -> argparse.ArgumentParser:
        """
        Creates a parser for the test runner
        """

        parser = argparse.ArgumentParser()
        cls.runner_args(parser)

        if registry := TestRegistry.get_registry(cls):
            subparsers = parser.add_subparsers(
                required=True,
                help="Select the test you want to run",
                dest="test_class",
            )

            # Add the subparsers for each test
            for test in registry:
                subparser = subparsers.add_parser(test.__name__)
                test.subparser(subparser)
        else:
            raise ValueError(f"Registry is empty, no test classes was found for {cls}")

        return parser
