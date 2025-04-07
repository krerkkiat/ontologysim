import operator
from collections import defaultdict
from enum import Enum

from numpy.random import MT19937, RandomState
from owlready2 import *

from ontologysim.ProductionSimulation.analyse.TimeAnalyse import TimeAnalyse
from ontologysim.ProductionSimulation.sim.Enum import Evaluate_Enum, Label, Queue_Enum
from ontologysim.ProductionSimulation.sim.Machine import Machine


class Queue_Selection(Enum):
    """
    Defines the two strategies for selecting the next station
    SQF: Shortest Queue First
    NJF: Earliest Job First (nearest queue)
    """

    SQF = "SQF"
    NJF = "NJF"

from .base import TransporterController  # noqa
from .edd import TransporterController_EDD  # noqa
from .fifo import TransporterController_FIFO  # noqa
from .hybrid import TransporterController_Hybrid  # noqa
from .lifo import TransporterController_LIFO  # noqa
from .njf import TransporterController_NJF  # noqa
from .sqf import TransporterController_SQF  # noqa

__all__ = [
    "Queue_Selection",
    "TransporterController",
    "TransporterController_EDD",
    "TransporterController_FIFO",
    "TransporterController_Hybrid",
    "TransporterController_LIFO",
    "TransporterController_NJF",
    "TransporterController_SQF",
]
