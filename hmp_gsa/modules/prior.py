from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from .models import Move

class GSAPrior(ABC):

    @abstractmethod
    def score(
        self,
        state: Any,
        move: Move,
    ) -> float:
        raise NotImplementedError