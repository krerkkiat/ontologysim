import os
from os import listdir
from os.path import isfile, join
from pathlib import Path

from flask import json, request

from ontologysim.Flask.Actions.APIAction import APIAction
from ontologysim.ProductionSimulation.init.API.IntitializerProducttypeAPI import (
    InitializerProducttypeAPI,
)
from ontologysim.ProductionSimulation.utilities import PathTest


class SimulationLoadAction(APIAction):
    """
    parent class for simulation load, define default path
    """

    def __init__(self, action, flaskApp):
        """

        :param action:
        :param flaskApp:
        """
        super().__init__(action, flaskApp)

        self.path = Path(__file__).parent.parent.parent / "Assets" / "DefaultFiles"
        self.fullPath = self.path


class FileLoadAction(SimulationLoadAction):
    """
    get: /load_files: return all file names from default directory
    """

    def __call__(self, *args):
        """

        :param args:
        :return:
        """
        self.action()

        onlyfiles = [
            f for f in listdir(self.fullPath) if isfile(join(self.fullPath, f))
        ]

        self.response = self.response200OK(json.dumps({"files": onlyfiles}))

        return self.response
