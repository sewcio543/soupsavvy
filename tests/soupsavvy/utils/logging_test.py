"""Module for testing the package logging utilities."""

from logging import Logger

from pytest import LogCaptureFixture

from soupsavvy.utils.logging import LOGGER, NAME


class TestLogging:
    """Unit Tests suite for the package logging utilities."""

    def test_logger_is_setup_correctly(self):
        """
        Tests that the logger is setup correctly.
        It should be an instance of the Logger class and have the correct name.
        """
        assert isinstance(LOGGER, Logger)
        assert LOGGER.name == NAME

    def test_logger_logs_message(self, caplog: LogCaptureFixture):
        """
        Tests that the logger logs messages correctly.
        Message should be logged with the correct level. Testing for INFO level.
        """
        message = "Test message"

        with caplog.at_level("INFO"):
            LOGGER.info(message)

        assert len(caplog.records) == 1
        record = caplog.records[0]
        assert record.levelname == "INFO"
        assert record.message == message
