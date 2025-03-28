from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    TypeDecorator,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref, relationship

from ontologysim.ProductionSimulation.database.models.Base import Base

# from ontologysim.ProductionSimulation.database.models.MachineKPI import MachineKPI, MachineTimeKPI


class SimulationFacts(Base):
    __tablename__ = "SimulationFacts"
    id = Column(Integer, primary_key=True)
    numberOfParts = Column(Integer, nullable=True)
    simulationTime = Column(
        Float(decimal_return_scale=7, asdecimal=True), nullable=True
    )
    loggingTime = Column(Float(decimal_return_scale=7, asdecimal=True), nullable=True)
