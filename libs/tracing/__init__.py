""" Tracing module """

from collections import defaultdict
import io
import os
import string
import sys
import time

class TraceError(Exception):
    """ Class to handle tracing exception """

# [[[ Level

DEBUG = 40
INFO = 30
WARNING = 20
ERROR = 10
CRITICAL = 0

LEVEL_2_STRING = {
    DEBUG: "DEBUG",
    INFO: "INFO",
    WARNING: "WARNING",
    ERROR: "ERROR",
    CRITICAL: "CRITICAL",
}

STRING_2_LEVEL = {
    "DEBUG": DEBUG,
    "INFO": INFO,
    "WARNING": WARNING,
    "ERROR": ERROR,
    "CRITICAL": CRITICAL,
}

def _get_level(level):
    """ Converts input levels to internal integer value """

    if isinstance(level, int):
        return level

    if not isinstance(level, str):
        raise TypeError("invalid level type '{level}' ({type(level)}): int or "
                        "str expected")

    level = level.upper()

    if level not in STRING_2_LEVEL:
        raise ValueError(f"unknown trace level '{level}'")

    return STRING_2_LEVEL[level]

# ]]]
# [[[ Record

class StackInfo:
    """ Helpers to manipulate stack and retrieve information about the places
        logs were emitted.
    """

    ModulePath = os.path.normcase(__file__)

    def __init__(self, path, line_no, func_name):
        self.path = path
        self.line_no = line_no
        self.func_name = func_name

    @property
    def file_name(self):
        """ Returns the file name in which the log was generated """
        return os.path.basename(self.path)

    @classmethod
    def get(cls):
        """ Extracts info about the place log was generated. """

        frame = sys._getframe()
        code = frame.f_code

        while frame is not None:
            frame = frame.f_back
            code = frame.f_code
            path = os.path.normcase(code.co_filename)

            if path != cls.ModulePath:
                func_name = code.co_name
                line_no = frame.f_lineno

                break
        else:
            return None

        return cls(path, line_no, func_name)


class Record:
    """ Log Record """

    def __init__(self, tracer, level, message, stack_info):
        self.timestamp = int(time.time())

        self.tracer = tracer
        self.level = level
        self.message = message
        self.stack_info = stack_info

    @property
    def file_name(self):
        """ Returns the function name where trace was generated """

        return self.stack_info.file_name

    @property
    def func_name(self):
        """ Returns the function name where trace was generated """

        return self.stack_info.func_name

    @property
    def level_name(self):
        """ Returns the level as a string """

        return LEVEL_2_STRING.get(self.level, str(self.level))

# ]]]
# [[[ Printers
# [[[ Basic Printer

class Printer:
    """ Log Printer """

    Formatter = string.Formatter()

    RecordFields = [
        "datetime",
        "file_name",
        "func_name",
        "level",
        "level_name",
        "message",
        "timestamp",
        "tracer",
    ]

    def __init__(self, record_fmt, date_fmt):
        self.record_fmt = record_fmt
        self.date_fmt = date_fmt

        self.args = list(self._get_fmt_args(record_fmt))

    @classmethod
    def _get_fmt_args(cls, record_fmt):
        """ Builds the list of field to generate to format log message """

        try:
            iterator = cls.Formatter.parse(record_fmt)
        except ValueError as exn:
            raise TraceError(f"invalid record format '{record_fmt}': {exn}")


        for _, field_name, *_ in iterator:
            if field_name not in cls.RecordFields:
                raise TraceError(f"invalid record format '{record_fmt}': unknown "
                                 f"field '{field_name}")
            yield field_name

    def get_datetime(self, record):
        """ Formats the datetime field for the log record """

        return time.strftime(self.date_fmt, time.localtime(record.timestamp))

    @classmethod
    def get_file_name(cls, record):
        """ Formats the function name field for the log record """

        return record.file_name

    @classmethod
    def get_func_name(cls, record):
        """ Formats the function name field for the log record """

        return record.func_name

    @classmethod
    def get_level(cls, record):
        """ Formats the level field for the log record """

        return record.level

    @classmethod
    def get_level_name(cls, record):
        """ Formats the level name field for the log record """

        return record.level_name

    @classmethod
    def get_message(cls, record):
        """ Formats the message field for the log record """

        return record.message


    @classmethod
    def get_timestamp(cls, record):
        """ Formats the timestamp field for the log record """

        return record.timestamp

    def print(self, record):
        """ Formats and prints the record """

        kwargs = dict((f, getattr(self, f"get_{f}")(record)) for f in self.args)
        sys.stderr.write(self.record_fmt.format(**kwargs))
        sys.stderr.write("\n")

# ]]]
# [[[ Petty Printer

class PrettyPrinter(Printer):
    """ Prints the tracing records with colors """

    ColorsByLevel = {
        DEBUG: defaultdict(str, {
            "datetime": "\033[2;30m",
            "level_name": "\033[1;30m",
            "message": "\033[0;30m",
        }),

        INFO: defaultdict(str, {
            "datetime": "\033[2;30m",
            "level_name": "\033[1;32m",
            "message": "",
        }),

        WARNING: defaultdict(str, {
            "datetime": "\033[2;30m",
            "level_name": "\033[1;33m",
            "message": "\033[0;33m",
        }),

        ERROR: defaultdict(str, {
            "datetime": "\033[2;30m",
            "level_name": "\033[1;31m",
            "message": "\033[0;31m",
        }),

        CRITICAL: defaultdict(str, {
            "datetime": "\033[2;30m",
            "level_name": "\033[1;30m",
            "message": "\033[1;30m",
        }),
    }

    def _get_fmt_args(self, record_fmt):
        """ Builds the list of field to generate to format log message """

        try:
            iterator = self.Formatter.parse(record_fmt)
        except ValueError as exn:
            raise TraceError(f"invalid record format '{record_fmt}': {exn}")

        yield "colors"

        color_fmt = io.StringIO()

        for text, field_name, spec, conv  in iterator:

            if field_name not in self.RecordFields:
                raise TraceError(f"invalid record format '{record_fmt}': unknown "
                                 f"field '{field_name}")

            yield field_name

            color_fmt.write(text)
            color_fmt.write(f"{{colors[{field_name}]}}")
            color_fmt.write(f"{{{field_name}")

            if conv:
                color_fmt.write(f"!{conv}")

            if spec:
                color_fmt.write(f":{spec}")

            color_fmt.write("}")
            color_fmt.write("\033[0m")

        self.record_fmt = color_fmt.getvalue()

    def get_colors(self, record):
        """ Returns the colors to format the log record """

        return self.ColorsByLevel.get(record.level, defaultdict(str))

# ]]]
# ]]]
# [[[ Tracer

class Tracer:
    """ Class that prints some messages """

    def __init__(self, name=None, level=INFO, parent=None, propagate=True):
        self.name = name

        self.level = _get_level(level)
        self.parent = parent
        self.propagate = propagate

        self.printers = []

    def add_printer(self, printer):
        """ Appends a printer to the tracer """

        self.printers.append(printer)

    def emit(self, record):
        """ Sends the record to all printers and parent """

        for printer in self.printers:
            printer.print(record)

        if self.propagate and self.parent:
            self.parent.emit(record)

    @classmethod
    def prepare_message(cls, base, *args, **kwargs):
        """ Format the trace message """

        if isinstance(base, str):
            try:
                return base.format(*args, **kwargs)
            except IndexError:
                raise TraceError(f"failed to format ({repr(base)}, {args}, {kwargs})")

        if args or kwargs:
            raise TraceError(f"unused parameters for ({repr(base)}, {args}, {kwargs})")

        return str(base)


    def _log(self, level, base, *args, **kwargs):
        """ Generate log event

        Arguments:
            level: the log level for the message.
            base: base text to be displayed
            *args: arguments to format the base text.
            **kwargs: keywords to format the base text.
        """

        if level > self.level:
            return


        msg = self.prepare_message(base, *args, **kwargs)
        self.emit(Record(self, level, msg, StackInfo.get()))

    def log(self, level, base, *args, **kwargs):
        """ Prints a log message """
        return self._log(_get_level(level), base, *args, **kwargs)

    def debug(self, base, *args, **kwargs):
        """ Prints a debug message """
        return self._log(DEBUG, base, *args, **kwargs)

    def info(self, base, *args, **kwargs):
        """ Prints a info message """
        return self._log(INFO, base, *args, **kwargs)

    def warn(self, base, *args, **kwargs):
        """ Prints a warning message """
        return self._log(WARNING, base, *args, **kwargs)

    def error(self, base, *args, **kwargs):
        """ Prints an error message """
        return self._log(ERROR, base, *args, **kwargs)

    def critical(self, base, *args, **kwargs):
        """ Prints a critial  message """
        return self._log(CRITICAL, base, *args, **kwargs)

# ]]]

def _init():
    """ Intialises the root tracer """

    default_record_fmt = "{datetime} {level_name:>9} ({file_name}:{func_name}) {message}"
    default_date_fmt = "%Y-%m-%d %H:%M:%S%z"
    default_level = "INFO"

    level = _get_level(os.getenv("TRACE_LEVEL", default_level))
    record_fmt = os.getenv("TRACE_RECORD_FMT", default_record_fmt)
    date_fmt = os.getenv("TRACE_DATE_FMT", default_date_fmt)

    printer = PrettyPrinter(record_fmt, date_fmt)
    root = Tracer(level=level)
    root.add_printer(printer)

    return root

TRACER = _init()

def log(level, base, *args, **kwargs):
    """ Prints a log message """
    TRACER.log(level, base, *args, **kwargs)

def debug(base, *args, **kwargs):
    """ Prints a debug message """
    TRACER.debug(base, *args, **kwargs)

def info(base, *args, **kwargs):
    """ Prints an info message """
    TRACER.info(base, *args, **kwargs)

def warn(base, *args, **kwargs):
    """ Prints a warning message """
    TRACER.warn(base, *args, **kwargs)

def error(base, *args, **kwargs):
    """ Prints an error message """
    TRACER.error(base, *args, **kwargs)

def critial(base, *args, **kwargs):
    """ Prints a critical message """
    TRACER.critical(base, *args, **kwargs)
