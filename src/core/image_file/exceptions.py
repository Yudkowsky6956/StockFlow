# TODO: Заменить этот Exception на базовый


class FilemakerError(Exception):
    def __init__(self, *args):
        super().__init__(*args)