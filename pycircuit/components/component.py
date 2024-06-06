from __future__ import annotations
from abc import ABC
from dataclasses import dataclass, field
from typing import Self
from sympy import Matrix
from enum import Enum, auto
import numpy as np

@dataclass
class Port:
    name:str
    parent: Component | None
    connections:list[Self] = field(default_factory=list)

    def __hash__(self) -> int:
        return id(self)

    def __lshift__(self, other_port:Self)->Self:
        other_port.connections.append(self)
        self.connections.append(other_port)
        return self

    def __rshift__(self, other_port:Self)->Self:
        self.__lshift__(other_port)
        return other_port

    def __repr__(self) -> str:
        if not self.parent:
            return self.name

        return f"{self.parent.name}.{self.name}"

@dataclass
class CurrentPort(Port):
    dc : float = 0.0

@dataclass
class VoltagePort(Port):
    dc : float = 0.0

GND = Port("GND", None)

class Analysis(Enum):
    SYMBOLIC = auto()
    TRANSIENT = auto()
    OP = auto()

class Component(ABC):
    def __init__(self, name:str):
        self.name = name
        self.ports : dict[str, Port] = {}

    def get_num_additional_row_columns(self, analysis:Analysis):
        """Some components (voltage sources, inductors) need an additional rows and columns"""
        return 0

    def __getitem__(self, port_name:str)->Port:
        return self.ports[port_name]

    def apply_tran_matrix(self, factory, index:int, g:np.ndarray, c:np.ndarray, x:list, b:np.ndarray, dimension:int):
        for name, port in self.ports.items():
            if isinstance(port, CurrentPort):
                net = factory.get_net_of(port)
                b[net.net_id] += port.dc
            else:
                raise NotImplementedError(f"You have to specify all ports correctly for transient analysis or overwrite apply_tran_matrix() method.")

    def apply_op_matrix(self, factory, index:int, m:np.ndarray, x:list, b:np.ndarray, dimension:int):
        for name, port in self.ports.items():
            if isinstance(port, CurrentPort):
                net = factory.get_net_of(port)
                b[net.net_id] += port.dc
            else:
                raise NotImplementedError(f"You have to specify all ports correctly for OP analysis or overwrite apply_op_matrix() method.")

    def apply_symbolic_matrix(self, factory, index:int, m:Matrix, x:list, b:Matrix, dimension:int):
        raise NotImplementedError(f"Symbolic analysis is not implemented for {self}")

    def update(self, factory, t:float, dt:float, signals:np.ndarray, g:np.ndarray, c:np.ndarray, x:list, b:np.ndarray):
        pass