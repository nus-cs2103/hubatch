from abc import ABC, abstractmethod

class BaseController(ABC):
    """Base class for controllers"""
    @abstractmethod
    def setup_argparse(self, subparsers):
        raise NotImplementedError
