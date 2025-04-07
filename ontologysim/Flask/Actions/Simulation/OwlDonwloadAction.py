from io import BytesIO

from flask import Flask, Response, json, request

from ontologysim.Flask.Actions.APIAction import APIAction


class OwlDownloadAction(APIAction):
    """
    get: /simulation/download/owl: sending owl file via string
    """

    def __call__(self, *args):
        """

        :param args:
        :return:
        """
        self.action()

        if self.flaskApp.startAlready:
            buffer = BytesIO()
            self.flaskApp.simCore.save_ontology(buffer)
            buffer.seek(0)
            content = buffer.read()
            self.response = self.response200OK(json.dumps({"file": content.decode("utf-8")}))
        else:
            self.response = self.response400BadRequest("simulation not started")

        return self.response
