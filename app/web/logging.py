"""Keep bearer tracking tokens out of Uvicorn's request logs."""

import logging
import re


class TrackingTokenFilter(logging.Filter):
    def filter(self, record):
        if isinstance(record.args, tuple):
            record.args = tuple(
                re.sub(r"([?&]token=)[^&\s]*", r"\1[redacted]", value)
                if isinstance(value, str)
                else value
                for value in record.args
            )
        return True


logging.getLogger("uvicorn.access").addFilter(TrackingTokenFilter())
