from abc import ABC, abstractmethod
from typing import Generic, TypeVar

ViewType = TypeVar('ViewType')
ModelType = TypeVar('ModelType')

class BasePresenter(ABC, Generic[ViewType, ModelType]):
    """Base presenter interface for MVP pattern."""
    
    def __init__(self, view: ViewType, model: ModelType):
        self._view = view
        self._model = model
        
    @abstractmethod
    def initialize(self) -> None:
        """Initialize the presenter and set up initial state."""
        pass
    
    @abstractmethod
    def dispose(self) -> None:
        """Clean up resources when presenter is no longer needed."""
        pass