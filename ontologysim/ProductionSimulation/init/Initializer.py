import datetime
import logging
import os
from pathlib import Path

from owlready2 import get_ontology

from ontologysim.Flask.Actions.UtilMethods.StateStorage import StateStorage
from ontologysim.ProductionSimulation.controller import (
    MachineController,
    OrderReleaseController,
    ServiceControllerMachine,
    ServiceControllerTransporter,
    TransporterController,
)
from ontologysim.ProductionSimulation.database.DataBase import DataBase
from ontologysim.ProductionSimulation.init.TransformLoggerIni import TransformLoggerIni
from ontologysim.ProductionSimulation.init.TransformProductionIni import (
    TransformProductionIni,
)
from ontologysim.ProductionSimulation.logger.EventLogger import EventLogger
from ontologysim.ProductionSimulation.logger.Logger import Logger
from ontologysim.ProductionSimulation.sim.Central import Central
from ontologysim.ProductionSimulation.sim.Defect import Defect
from ontologysim.ProductionSimulation.sim.Distribution import Distribution
from ontologysim.ProductionSimulation.sim.Enum import Label
from ontologysim.ProductionSimulation.sim.Event import Event
from ontologysim.ProductionSimulation.sim.Location import Location
from ontologysim.ProductionSimulation.sim.Machine import Machine
from ontologysim.ProductionSimulation.sim.OrderRelease import (
    OrderRelease,
)
from ontologysim.ProductionSimulation.sim.Position import Position
from ontologysim.ProductionSimulation.sim.ProdProcess import ProdProcess
from ontologysim.ProductionSimulation.sim.Product import Product
from ontologysim.ProductionSimulation.sim.ProductType import ProductType
from ontologysim.ProductionSimulation.sim.ProductTypeNet.Process import (
    MergeProcess,
    Process,
)
from ontologysim.ProductionSimulation.sim.ProductTypeNet.State import State
from ontologysim.ProductionSimulation.sim.Queue import Queue
from ontologysim.ProductionSimulation.sim.RepairService.RepairServiceMachine import (
    RepairServiceMachine,
)
from ontologysim.ProductionSimulation.sim.RepairService.RepairServiceTransporter import (
    RepairServiceTransporter,
)
from ontologysim.ProductionSimulation.sim.SimCore import SimCore
from ontologysim.ProductionSimulation.sim.Task import Task
from ontologysim.ProductionSimulation.sim.Transporter import Transporter
from ontologysim.ProductionSimulation.utilities import (
    EventUtilities,
    Init,
    import_class,
    sanitize_path,
)


class Initializer:
    """
    The intitializer is the main connection for the use from outside

    important: all controller from the productionSimulation need to be imported at this position,
    alternatively you can create your own controller
    """

    def __init__(self):
        """
        defines run.log
        """
        logging.basicConfig(filename="run.log", level=logging.DEBUG)

        self.s: SimCore | None = None

    def initSimCore(self):
        """
        creating the sim core class
        """
        self.startSimulationTime = datetime.datetime.now()

        self.s = SimCore()
        self.s.central = Central(self.s)
        self.s.queue = Queue(self.s)
        self.s.machine = Machine(self.s)
        self.s.transport = Transporter(self.s)
        self.s.product_type = ProductType(self.s)
        self.s.product = Product(self.s)
        self.s.task = Task(self.s)
        self.s.order_release = OrderRelease(self.s)
        self.s.defect = Defect(self.s)
        self.s.repair_service_machine = RepairServiceMachine(self.s)
        self.s.repair_service_transporter = RepairServiceTransporter(self.s)
        self.s.event = Event(self.s)
        self.s.distribution = Distribution(self.s)
        self.s.location = Location(self.s)
        self.s.EventLogger = EventLogger(self.s)
        self.s.logger = Logger(self.s)
        self.s.event_utilities = EventUtilities(self.s)
        self.s.prod_process = ProdProcess(self.s)
        self.s.process = Process(self.s)
        self.s.merge_process = MergeProcess(self.s)
        self.s.state = State(self.s)
        self.s.position = Position(self.s)
        self.s.stateStorage = StateStorage(self.s)

    def restart(
        self,
        production_config_path,
        owl_config_path,
        controller_config_path,
        logger_config_path,
        dataBase,
    ):
        """
        resets the complete simulation and starts a new one

        :param production_config_path:
        :param owl_config_path:
        :param controller_config_path:
        :param logger_config_path:
        """

        # choose between load from owl or create from config
        self.createProduction(production_config_path, owl_config_path)
        # init.loadProductionFromOWL("ontologysim/example/owl/production_without_task_defect.owl")

        # add Tasks
        self.addTaskPathGiven(production_config_path)

        # (optional)
        self.addDefectPathGiven(production_config_path)

        # add Logger
        self.addLoggerPathGiven(logger_config_path)

        # create data base
        self.addDataBaseToLogger(dataBase)

        # set controller
        self.loadControllerPathGiven(controller_config_path)

        self.run_until_first_event()

    def createProduction(self, sim_config_path, owl_config_path):
        """
        initialize the simulation without tasks and defects
        creates the ontology
        calls the transformation of config files

        :param sim_config_path:
        :param owl_config_path:
        """
        sim_config_path = sanitize_path(os.getcwd(), sim_config_path)
        owl_config_path = sanitize_path(os.getcwd(), owl_config_path)

        """ -------------------------------------------Production initialization-------------------------------------------------"""
        # Read from Configuration File
        sim_conf = self.transformProductionPath(sim_config_path)

        """ -------------------------------------------OWL initialization-------------------------------------------------"""
        # Read from Configuration File
        owl_conf = Init(owl_config_path)
        owl_conf.read_ini_file()

        self.initProductionComponents(sim_conf)

        save_dict_list = owl_conf.configs["OWL"]["owl_save_path"]
        for save_dict in save_dict_list:
            if (
                save_dict["save"]
                and save_dict["type"] == "production_without_task_defect"
            ):
                self.s.createWorld()
                save_path = sanitize_path(os.getcwd(), save_dict["path"])
                self.s.onto.save(file=save_path, format="rdfxml")

    def transformProductionPath(self, sim_config_path):
        """
        transform ini input
        :param sim_config_path: path
        :return: Init object
        """

        sim_conf = Init(sim_config_path)
        sim_conf.read_ini_file()
        sim_conf.configs = TransformProductionIni(self.s).transform_ini(
            sim_conf.configs
        )
        return sim_conf

    def initProductionComponents(self, sim_conf):
        """
        init simulation
        :param sim_conf: Ini object
        :return:
        """
        """ -------------------------------------------SimCore initialization-------------------------------------------------"""

        owl_folder = Path("owl")
        owl_folder.mkdir(exist_ok=True)
        # NOTE(KC): No idea why we are saving the ontology. Originally, the method is empty (having just pass)
        # with the actual saving procedure commented out.
        self.s.save_ontology(str(owl_folder / "test.owl"))
        self.s.createOWLStructure()
        self.s.central.init_class()
        self.s.createSimInstance()
        self.s.createLogger()
        self.s.createEventList()
        """ -------------------------------------------Queue initialization-------------------------------------------------"""

        queue_start_list = sim_conf.configs["Start_Queue"]["settings"]
        queue_end_list = sim_conf.configs["End_Queue"]["settings"]
        queue_deadlock_list = sim_conf.configs["DeadLock_Queue"]["settings"]
        random_seed_add_value = sim_conf.configs["RandomSeed"]["appendvalue"]

        self.s.setRandomSeedAddValue(random_seed_add_value)

        """ -------------------------------------------Process initialization-------------------------------------------------"""

        process_list = sim_conf.configs["Process"]["settings"]

        for process_config in process_list:
            if "merged" not in process_config.keys():
                self.s.process.createProcess(process_config)
            else:
                self.s.merge_process.createProcess(process_config)

        """ -------------------------------------------ProductType initialization-------------------------------------------------"""

        product_type_config_list = sim_conf.configs["ProductType"]["settings"]

        for product_type_config in product_type_config_list:
            self.s.product_type.createProductType(product_type_config, process_config)

        """ -------------------------------------------Machine initialization-------------------------------------------------"""

        # print(sim_conf.configs['Machine'])
        machine_dict_list = sim_conf.configs["Machine"]["machine_dict"]
        process_config_list = sim_conf.configs["Process"]["settings"]

        queue_dict_list = sim_conf.configs["Machine"]["queue_dict"]
        queue_process_dict_list = sim_conf.configs["Machine"]["queue_process_dict"]

        self.s.prod_process.ini_dict(process_config_list)
        for queue_dict in queue_dict_list:
            if self.s.onto[Label.Queue.value + str(queue_dict["queue_id"])] is not None:
                raise Exception("queue id not unique " + str(queue_dict["queue_id"]))
            self.s.queue.createQueue(queue_dict, Label.Queue.value)

        for queue_process_dict in queue_process_dict_list:
            if (
                self.s.onto[Label.Queue.value + str(queue_process_dict["queue_id"])]
                is not None
            ):
                raise Exception(
                    "queue id not unique " + str(queue_process_dict["queue_id"])
                )
            self.s.queue.createQueue(queue_process_dict, Label.Queue.value)

        for machine_dict in machine_dict_list:
            if (
                self.s.onto[Label.Machine.value + str(machine_dict["machine_id"])]
                is not None
            ):
                raise Exception(
                    "machine id not unique " + str(machine_dict["machien_id"])
                )
            self.s.machine.createMachine(machine_dict, process_config_list)

        """ -------------------------------------------Transport initialization-------------------------------------------------"""

        number_of_transporter = sim_conf.configs["Transporter"]["number_of_transporter"]
        transporter_dict = sim_conf.configs["Transporter"]["settings"]
        start_location = sim_conf.configs["Transporter"]["start_location"]

        for i in range(len(start_location)):
            start_location[i]["location_onto"] = self.s.location.createLocation(
                start_location[i]["location"]
            )

        for i in range(number_of_transporter):
            locationFound = False
            for b in range(len(start_location)):
                if start_location[b]["id"] == transporter_dict[i]["location_id"]:
                    self.s.transport.createTransporter(
                        transporter_dict[i], start_location[b]["location_onto"]
                    )

                    locationFound = True
                    break
            if not locationFound:
                raise Exception("start location id error")

        """ -------------------------------------------Queue initialization-----------------------------------------------"""

        for i in range(len(queue_deadlock_list)):
            self.s.queue.createQueue(
                queue_deadlock_list[i], Label.DeadlockQueue.value, self.s.queue_id + i
            )
        self.s.queue.deadlockWaitingTime = sim_conf.configs["DeadLock_Queue"][
            "deadlock_waiting_time"
        ]

        for i in range(len(queue_start_list)):
            self.s.queue.createQueue(
                queue_start_list[i], Label.StartQueue.value, self.s.queue_id + i
            )

        for i in range(len(queue_end_list)):
            # TODO only 1 possible
            queue_end_list[i]["number_of_positions"] = 0
            self.s.queue.createQueue(
                queue_end_list[i], Label.EndQueue.value, self.s.queue_id + i
            )

        """ -------------------------------------------Producttype initialization-----------------------------------------------"""

        product_type_dict_list = sim_conf.configs["ProductType"]["settings"]
        for product_type_dict in product_type_dict_list:
            pass
            # path = sanitize_path(os.getcwd(), product_type_dict["path"])
            # self.s.product_type.loadPetriNet(path)

        self.s.location.init_distance_dict()
        self.s.product_type.init_percentage_dict()
        self.s.central.init_instance()
        self.s.transport.initTransporterDict()

        # print([ (queue.name,queue.size)     for queue in self.s.central.queue_list])

    def addTask(self, sim_conf):
        """
        add tasks the ontologysim

        :param production_config_path:
        """

        """ -------------------------------------------Task initialization-----------------------------------------------"""

        task_dict_list = sim_conf.configs["Task"]["settings"]
        for task_dict in task_dict_list:
            product_type_onto = self.s.onto[
                Label.ProductType.value + str(task_dict["product_type"])
            ]

            if "start_time" in task_dict.keys():
                self.s.task.createTask(
                    product_type_onto,
                    task_dict["number_of_parts"],
                    task_dict["type"],
                    task_dict["start_time"],
                )
            else:
                self.s.task.createTask(
                    product_type_onto, task_dict["number_of_parts"], task_dict["type"]
                )

        task_list = self.s.onto.search(type=self.s.central.task_class)
        number_of_products = sum([task.number for task in task_list])

        transporter_list = self.s.onto.search(type=self.s.central.transporter_class)
        number_of_position_transporter = sum(
            [
                len(transport_onto.has_for_transp_queue[0].has_for_position)
                for transport_onto in transporter_list
            ]
        )
        self.s.queue.addPositions(
            self.s.central.end_queue_list[0], number_of_position_transporter
        )

        self.s.central.init_instance()
        self.s.product.init_number_of_products()
        self.s.event_utilities.calc_position_dict()
        self.s.event_utilities.calc_process_dict()

    def addTaskPathGiven(self, sim_config_path):
        """
        adding task to simulation, given file path
        :param sim_config_path:
        :return:
        """
        sim_config_path = sanitize_path(os.getcwd(), sim_config_path)

        sim_conf = self.transformProductionPath(sim_config_path)
        self.addTask(sim_conf)

    def addDefectPathGiven(self, defect_config_path):
        """
        adding defect to simulationo, given file path
        :param defect_config_path:
        :return:
        """
        sim_config_path = sanitize_path(os.getcwd(), defect_config_path)
        sim_conf = self.transformProductionPath(sim_config_path)
        self.addDefect(sim_conf)

    def addDefect(self, sim_conf):
        """
        add defects to the ontology (optional)

        :param defect_config_path:
        """

        transporter_defect_possible = sim_conf.configs["Defect"][
            "transporter_defect_possible"
        ]
        machine_defect_possible = sim_conf.configs["Defect"]["machine_defect_possible"]

        transport_defect_type_random = sim_conf.configs["Defect"]["transporter_random"]
        transport_defect_normal_distribution = sim_conf.configs["Defect"][
            "transporter_normal"
        ]
        machine_defect_type_random = sim_conf.configs["Defect"]["machine_random"]
        machine_defect_normal_distribution = sim_conf.configs["Defect"][
            "machine_normal"
        ]

        machine_service_number = sim_conf.configs["Repair"]["machine_repair"]
        transporter_service_number = sim_conf.configs["Repair"]["transporter_repair"]

        if machine_defect_possible:
            self.s.defect.machine_defect_possible = machine_defect_possible
            for machine_onto in self.s.machine.getAllMachine():
                machine_defect_onto = self.s.defect.createDefect(
                    machine_defect_type_random, machine_defect_normal_distribution
                )
                self.s.machine.add_defect(machine_onto, machine_defect_onto)
                self.s.machine.setNextDefectTime(machine_onto, machine_defect_onto)

            self.s.repair_service_machine.createService(machine_service_number)
            self.s.repair_service_machine.initService()

        if transporter_defect_possible:
            self.s.defect.transport_defect_possible = transporter_defect_possible
            for transport_onto in self.s.transport.getAllTransporter():
                transport_defect_onto = self.s.defect.createDefect(
                    transport_defect_type_random, transport_defect_normal_distribution
                )
                self.s.transport.add_defect(transport_onto, transport_defect_onto)

                self.s.transport.setNextDefectTime(
                    transport_onto, transport_defect_onto
                )

            self.s.repair_service_transporter.createService(transporter_service_number)
            self.s.repair_service_transporter.initService()

    def setServiceControllerMachine(self, python_class):
        """
        adding a defect handling strategy for the machine, only needed if defect is added
        is already included in load controller

        :param python_class:
        """
        if not issubclass(python_class, ServiceControllerMachine):
            raise TypeError(f"'{python_class}' is not a subclass of ServiceControllerMachine.")

        service_controller = python_class()
        self.s.repair_service_machine.addRepairServiceController(service_controller)

    def setServiceControllerTransporter(self, python_class):
        """
        adding a defect handling strategy for the tranporter, only needed if defect is added
        is already included in load controller

        :param python_class:
        """
        if not issubclass(python_class, ServiceControllerTransporter):
            raise TypeError(f"'{python_class}' is not a subclass of ServiceControllerTransporter.")
        service_controller = python_class()
        self.s.repair_service_transporter.addRepairServiceController(
            service_controller
        )

    def setMachineController(self, python_class, controller_dict={}):
        """
        adding a scheduling strategy for the machine
        is already included in load controller

        :param python_class:
        """
        if not issubclass(python_class, MachineController):
            raise TypeError(f"'{python_class}' is not a subclass of MachineController.")

        m_controller = python_class()
        self.s.machine.addMachineController(m_controller)
        self.s.machine.machineController.addControllerDict(controller_dict)

    def setOrderReleaseController(self, python_class):
        """
        adding a order release strategy
        is already included in load controller

        :param python_class:
        """
        if not issubclass(python_class, OrderReleaseController):
            raise TypeError(f"'{python_class}' is not a subclass of OrderReleaseController.")

        order_release_controller = python_class()
        self.s.order_release.addOrderReleaseController(order_release_controller)

    def setTransporterController(self, python_class, controller_dict={}):
        """
        adding a routing strategy for the transporter
        is already included in load controller

        :param python_class:
        :param controller_dict: dict
        """
        if not issubclass(python_class, TransporterController):
            raise TypeError(f"'{python_class}' is not a subclass of TransporterController.")

        transportController = python_class()
        self.s.transport.addTransportController(transportController)
        self.s.transport.transportController.addControllerDict(controller_dict)

    def setFillLevel(self, fill_level):
        """
        defines the maximum number of products in the production in percentage

        :param fill_level: percentage
        """
        self.s.order_release.setMaxNumber(fill_level)

    def loadProductionFromOWL(self, owl_path):
        """
        allowes to load a owl file to the simulation, depending on the owl-File it could be necessary to add tasks, defect

        :param owl_path: .owl file
        """
        path = sanitize_path(os.getcwd(), owl_path)
        self.s.onto = get_ontology(path).load()
        self.s.central.init_class()
        self.s.central.simInstance = self.s.central.sim_class(Label.SimCore.value + "0")
        self.s.central.init_all_ids()

        for product_type_onto in self.s.onto.search(
            type=self.s.central.product_type_class
        ):
            self.s.product_type.loadPetrNetFromString(product_type_onto)

        self.s.location.init_distance_dict()
        self.s.product_type.init_percentage_dict()
        self.s.transport.initTransporterDict()

    def addLoggerAndDataBasePathGiven(self, log_config_path):
        """
        adding logger and database to simulation given path file
        :param log_config_path: string
        :return:
        """
        log_config_path = sanitize_path(os.getcwd(), log_config_path)

        # Read from Configuration File
        log_conf = Init(log_config_path)
        log_conf.read_ini_file()

        log_conf = TransformLoggerIni(self.s).transform_ini(log_conf.configs)
        self.addLogger(log_conf)
        if self.s.logger.save_config["database"]:
            db = DataBase(self.s.logger.save_config["sql_alchemy_database_uri"])
            self.addDataBaseToLogger(db)

    def addLoggerAndDataBase(self, log_conf):
        """
        add logger and data base to simulation
        :param log_conf: Ini object
        :return:
        """
        self.addLogger(log_conf)
        if self.s.logger.save_config["database"]:
            db = DataBase(self.s.logger.save_config["sql_alchemy_database_uri"])
            self.addDataBaseToLogger(db)

    def addLoggerPathGiven(self, log_config_path):
        """
        add logger to similuation given path
        :param log_config_path: string
        :return:
        """
        log_config_path = sanitize_path(os.getcwd(), log_config_path)

        # Read from Configuration File
        log_conf = Init(log_config_path)
        log_conf.read_ini_file()

        log_conf = TransformLoggerIni(self.s).transform_ini(log_conf.configs)
        self.addLogger(log_conf)

    def addLogger(self, log_conf):
        """
        add Logger to simulation
        :param log_config_path: Ini object
        """

        self.s.logger.initLogger(log_conf)

        self.s.logger.plot.initPlot(log_conf)
        if log_conf["KPIs"]["log_events"] and log_conf["Save"]["csv"]:
            self.s.event_logger.is_activated = True
        else:
            self.s.event_logger.is_activated = False

    def run(self):
        """
        starts the simulation run
        """
        self.test_production_config()

        self.s.distribution.ini_dict()
        self.s.createWorld()
        self.s.main()

        self.s.logger.create_output()

        if self.s.data_base is not None:
            self.s.data_base.close()

        print()
        print("simulation time", self.s.getCurrentTimestep())
        self.endSimulationTime = datetime.datetime.now()
        print("pc time:", str(self.endSimulationTime - self.startSimulationTime))
        # self.s.onto.save(file=self.s.transfrom_path_check_dir(log_conf.configs['OWL']['setting']['path']),
        #                format="rdfxml")

    def run_until_first_event(self):
        """
        runs the simulation until the first event, mainly creates the ontolgy world
        """
        self.test_production_config()
        self.s.distribution.ini_dict()
        self.s.createWorld()
        self.s.run = True
        self.s.order_release.orderReleaseController.evaluateCreateOrderRelease()

    def set_save_time(self, save_time):
        """
        the simulation only logs after x-seconds after the start of the simulation

        :param save_time: float
        """
        self.s.set_save_time(save_time)

    def loadControllerPathGiven(self, path):
        """
        load controller to simulation given path
        :param path: string
        :return:
        """
        controller_config_path = sanitize_path(os.getcwd(), path)

        # Read from Configuration File
        controller_conf = Init(controller_config_path)
        controller_conf.read_ini_file()
        self.loadController(controller_conf)

    def loadController(self, contoller_conf):
        """
        loads all controller, which are necessary to run the simulation

        :param path:
        """

        # NOTE(KC): They are not strings.
        machine_controller_string = contoller_conf.configs["Controller"]["machine"]
        transporter_controller_string = contoller_conf.configs["Controller"][
            "transporter"
        ]
        order_release_controller_string = contoller_conf.configs["Controller"][
            "orderrelease"
        ]
        service_machine_controller_string = contoller_conf.configs["Controller"][
            "service_machine"
        ]
        service_transporter_controller_string = contoller_conf.configs["Controller"][
            "service_transporter"
        ]

        order_release_controller_class = import_class(order_release_controller_string["type"], OrderReleaseController)
        self.setOrderReleaseController(order_release_controller_class)

        self.setFillLevel(order_release_controller_string["fillLevel"])

        service_machine_controller_class = import_class(service_machine_controller_string["type"], ServiceControllerMachine)
        self.setServiceControllerMachine(service_machine_controller_class)

        service_transporter_controller_class = import_class(service_transporter_controller_string["type"], ServiceControllerTransporter)
        self.setServiceControllerTransporter(service_transporter_controller_class)

        hybrid_controller_configs = {}
        if len(transporter_controller_string["add"]) > 0:
            hybrid_controller_configs = self._parse_hybrid_controller_config(transporter_controller_string["add"], TransporterController)

        transporter_controller_class = import_class(transporter_controller_string["type"], TransporterController)
        self.setTransporterController(transporter_controller_class, hybrid_controller_configs)

        hybrid_controller_configs = {}
        if len(machine_controller_string["add"]) > 0:
            hybrid_controller_configs = self._parse_hybrid_controller_config(machine_controller_string["add"], MachineController)

        machine_controller_class = import_class(machine_controller_string["type"], MachineController)
        self.setMachineController(machine_controller_class, hybrid_controller_configs)

    def _parse_hybrid_controller_config(self, configs: dict[str, float], parent: type) -> dict[type, float]:
        hybrid_controllers = {}
        for class_name, portion in configs.items():
            transporter_controller_class = import_class(class_name, parent)
            hybrid_controllers[transporter_controller_class] = portion
        return hybrid_controllers

    def test_production_config(self):
        """
        defines a short test if the owl and pnml files are set up correctly
        currently checked:
        - are all production ids defined
        - have the machines different location
        """

        machine_onto_list = [
            machine for machine in self.s.onto.search(type=self.s.central.machine_class)
        ]
        machine_prod_prcoess_ids = []
        for machine in machine_onto_list:
            for prod_process in machine.has_for_prodprocess:
                machine_prod_prcoess_ids.append(self.s.prod_process.getID(prod_process))

        prod_process_ids = [
            self.s.prod_process.getID(prod)
            for prod in self.s.onto.search(type=self.s.central.prod_process_class)
        ]

        product_prod_process_ids = self.s.product_type.getProdProcessId()

        if not set(product_prod_process_ids).issubset(prod_process_ids):
            raise Exception("pnml product process is not defined in production.ini")

        if not set(machine_prod_prcoess_ids).issubset(prod_process_ids):
            raise Exception("product process is not defined in production.ini")

        if not set(machine_prod_prcoess_ids).issubset(product_prod_process_ids):
            print("product process is not assigned to any machine")

        location_list = []
        for machine in machine_onto_list:
            for location in machine.has_for_machine_location:
                location_list.append(location)

        for i in range(len(location_list)):
            for j in range(len(location_list)):
                if i != j:
                    if (
                        self.s.location.calculateDistance(
                            location_list[i], location_list[j]
                        )
                        == 0
                    ):
                        print("warning machines have the same location")

    def addDataBaseToLogger(self, dataBase):
        """
        add database to logger
        :param dataBase: database object
        :return:
        """
        self.s.logger.setDataBase(dataBase)
