import os
import subprocess
import unittest
import inspect
import sys
from os import listdir
from os.path import isfile
from pathlib import Path

from ontologysim import get_default_config_file_paths

current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
parent_parent_dir = os.path.dirname(parent_dir)
sys.path.insert(0, parent_dir)
sys.path.insert(0, parent_parent_dir)


from ontologysim.ProductionSimulation.utilities import Init


class MainTest(unittest.TestCase):
    """
    test all default files
    """

    def setUp(self):
        """
        set up method, which is called before every test
        :return:
        """
        self.init = None
        self.timeoutShort = 30
        self.timeoutMiddle = 60
        self.timeoutLong = 180

    # @unittest.skip
    def test_default_test(self):
        """
        test all files in /tests/configFiles/defaultTest/
        :return:
        """
        default_test_configs_root = (
            Path(__file__).parent.parent / "configFiles" / "defaultTest"
        )

        onlyfiles = [f for f in default_test_configs_root.iterdir() if f.is_file()]
        self.assertTrue(len(onlyfiles) == 4)

        process_result = subprocess.run(
            [
                sys.executable,
                "-m",
                "ontologysim",
                "run",
                str(default_test_configs_root / "production_config_lvl3.ini"),
                str(default_test_configs_root / "controller_config.ini"),
                str(default_test_configs_root / "owl_config.ini"),
                str(default_test_configs_root / "logger_config_lvl3.ini"),
            ],
            capture_output=True,
            timeout=self.timeoutMiddle
        )
        self.assertEqual(process_result.returncode, 0)

    # @unittest.skip
    def test_main_config_files(self):
        """
        test all predefined files in "/example/config/"
        :return:
        """
        defaultTestPath = "/example/config/"
        productionConifgFiles = [
            "production_config_lvl3.ini",
            "production_config_lvl2.ini",
            "production_config_lvl1.ini",
            "production_config.ini",
        ]
        controllerConfigFiles = ["controller_config.ini"]
        owlConfigFiles = ["owl_config.ini"]
        loggerConfigFiles = ["logger_config_lvl3.ini", "logger_config_lvl2.ini"]

        # TODO add production_config_merge_lvl1

        onlyfiles = [
            f
            for f in listdir(parent_parent_dir + defaultTestPath)
            if isfile(os.path.join(parent_parent_dir + defaultTestPath, f))
        ]

        for file in onlyfiles:
            init = Init(parent_parent_dir + defaultTestPath + file)
            init.read_ini_file()
            init.identifyType()
            for type in init.type:
                if type == "production":
                    # TODO remove or case
                    self.assertTrue(
                        file in productionConifgFiles
                        or file == "production_config_merge_lvl1.ini"
                    )
                elif type == "logger":
                    self.assertTrue(file in loggerConfigFiles)
                elif type == "controller":
                    self.assertTrue(file in controllerConfigFiles)
                elif type == "owl":
                    self.assertTrue(file in owlConfigFiles)
                else:
                    raise Exception(str(type) + "not defined")

        for i, productionConfigFile in enumerate(productionConifgFiles):
            listConfig = {}
            listConfig["production"] = defaultTestPath + productionConfigFile
            listConfig["config"] = (
                defaultTestPath + owlConfigFiles[i % len(owlConfigFiles)]
            )
            listConfig["controller"] = (
                defaultTestPath + controllerConfigFiles[i % len(controllerConfigFiles)]
            )
            listConfig["logger"] = (
                defaultTestPath + loggerConfigFiles[i % len(loggerConfigFiles)]
            )

            output = subprocess.check_output(
                "python "
                + parent_parent_dir
                + "/tests/processes/MainProcess.py "
                + ' "'
                + str(listConfig)
                + '"',
                shell=True,
                stderr=subprocess.STDOUT,
                timeout=self.timeoutLong,
            )

            self.assertTrue(output)

    def test_for_docu(self):
        """
        test all files in "/example/config/for_docu/"
        :return:
        """
        config_files_root = (
            Path(__file__).parent.parent.parent / "example" / "config" / "for_docu"
        )

        defaultTestPath = "/example/config/for_docu/"
        productionConifgFiles = [
            "production_config_lvl3.ini",
            "production_config_lvl2.ini",
            "production_config_lvl1.ini",
            "production_config.ini",
        ]
        controllerConfigFiles = [
            "controller_config.ini",
            "controller_config_extern.ini",
        ]
        owlConfigFiles = ["owl_config.ini"]
        loggerConfigFiles = ["logger_config_lvl3.ini", "logger_config_lvl2.ini"]
        listConfig = {}

        onlyfiles = [f for f in config_files_root.iterdir() if f.is_file()]

        for file in onlyfiles:
            init = Init(parent_parent_dir + defaultTestPath + file)
            init.read_ini_file()
            init.identifyType()
            for type in init.type:
                if type == "production":
                    # TODO remove or case
                    self.assertTrue(
                        file in productionConifgFiles
                        or file == "production_config_merge_lvl1.ini"
                    )
                elif type == "logger":
                    self.assertTrue(file in loggerConfigFiles)
                elif type == "controller":
                    self.assertTrue(file in controllerConfigFiles)
                elif type == "owl":
                    self.assertTrue(file in owlConfigFiles)
                else:
                    raise Exception(str(type) + "not defined")

        # NOTE(KC): This looks like an attempt at test parameterization ...
        for i, productionConfigFile in enumerate(productionConifgFiles):
            listConfig = {}
            listConfig["production"] = defaultTestPath + productionConfigFile
            listConfig["config"] = (
                defaultTestPath + owlConfigFiles[i % len(owlConfigFiles)]
            )
            listConfig["controller"] = (
                defaultTestPath + controllerConfigFiles[i % len(controllerConfigFiles)]
            )
            listConfig["logger"] = (
                defaultTestPath + loggerConfigFiles[i % len(loggerConfigFiles)]
            )

            output = subprocess.check_output(
                "python "
                + parent_parent_dir
                + "/tests/processes/MainProcess.py "
                + ' "'
                + str(listConfig)
                + '"',
                shell=True,
                stderr=subprocess.STDOUT,
                timeout=self.timeoutMiddle,
            )
            print(output)

            self.assertTrue(output)

    def test_flaskDefaultFiles(self):
        """
        test file in "/ontologysim/Flask/Assets/DefaultFiles/"
        :return:
        """
        # NOTE(KC): We could also parameterize this along with test_default_test.
        flask_defailt_configs = get_default_config_file_paths()
        process_result = subprocess.run(
            [
                sys.executable,
                "-m",
                "ontologysim",
                "run",
                str(flask_defailt_configs["production"]),
                str(flask_defailt_configs["controller"]),
                str(flask_defailt_configs["owl"]),
                str(flask_defailt_configs["logger"]),
            ],
            capture_output=True,
            timeout=self.timeoutMiddle
        )
        self.assertEqual(process_result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
