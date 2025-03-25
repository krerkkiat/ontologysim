import configparser

from tests.util.Generator import Generator


class OwlGenerator(Generator):
    """
    Owl generator
    """

    def __init__(self):
        """ """
        super().__init__(None)

    def createConfigDict(self):
        """
        main methode for creating config dict

        :return: configparser element
        """

        owl_config = configparser.ConfigParser()
        owl_config["OWL"] = self.addOWL()

        return owl_config

    def addOWL(self):
        """
        defines owl setttings

        :return: dict
        """
        config = {}
        config["owl_save_path"] = []
        return config
