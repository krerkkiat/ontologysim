from ontologysim.ProductionSimulation.sim.Central import Central
from ontologysim.ProductionSimulation.sim.ProductType import ProductType
from ontologysim.ProductionSimulation.sim.ProductTypeNet.Process import Process
from ontologysim.ProductionSimulation.sim.SimCore import SimCore


class InitializerProducttypeAPI:
    """
    initialize all needed objects to create procudttype
    """

    def __init__(self):
        """ """
        self.s = SimCore()

        self.s.central = Central(self.s)
        self.s.product_type = ProductType(self.s)
        self.s.process = Process(self.s)

        self.s.createOWLStructure()
        self.s.central.init_class()
