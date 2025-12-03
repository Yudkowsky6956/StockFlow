class GenerationError(Exception):
    def __init__(self, message: str, log: str = None, delay: int = 0, fatal: bool = False, mark: bool = False, lock: bool = False):
        super().__init__(message)
        self.log = log
        self.delay = delay
        self.fatal = fatal
        self.mark = mark
        self.lock = lock