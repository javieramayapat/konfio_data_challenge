import abc


class Extractor(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def __init__(self) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def parameter_validation(self):
        raise NotImplementedError

    @abc.abstractmethod
    def extract_data_from_source(self):
        raise NotImplementedError
