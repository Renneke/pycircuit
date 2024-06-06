
from dataclasses import dataclass, field
from ..components  import Port, GND

class Net:

    def __init__(self, ports:list[Port]) -> None:
        self.name : str = ""
        self.ports: list[Port] = ports
        self.net_id : int = -1

    def __repr__(self) -> str:
        return f"Net({self.name}, {[(x.parent.name if x.parent else 'GND')+'.'+x.name for x in self.ports]})"

    def is_gnd(self)->bool:
        for port in self.ports:
            if port is GND:
                return True
        return False



class NetFactory:

    def __init__(self) -> None:
        self.nets: list[Net] = []

    def get(self, name:str)->Net|None:
        for net in self.nets:
            if net.name == name:
                return net

    def get_net_of(self, port:Port)->Net|None:
        for net in self.nets:
            if port in net.ports:
                return net

    def assign_net_ids(self):
        for i, net in enumerate(self.nets):
            net.net_id = i

    def set_name(self, port:Port, name:str):
        self.get_net_of(port).name = name

    def add_connection(self, port_a:Port, port_b:Port):

        net_a = self.get_net_of(port_a) or Net(ports=[port_a, port_b])
        net_b = self.get_net_of(port_b) or Net(ports=[port_a, port_b])

        if net_a == net_b:
            return # No connection needed

        if net_a not in self.nets:
            self.nets.append(net_a)

        if net_b not in self.nets:
            self.nets.append(net_b)

        self.merge_nets(net_a, net_b)

    def merge_nets(self, net_a:Net, net_b:Net):
        self.nets.remove(net_b)
        assert net_a != net_b
        net_a.ports += net_b.ports




