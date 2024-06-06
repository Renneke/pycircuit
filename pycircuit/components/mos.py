from .component import Component, Port
from sympy import Matrix, symbols

class MOS(Component):
    def __init__(self, name: str, gm:float|str|None=None, gds:float|str|None=None, gmb:float|str|None=None):
        super().__init__(name)

        self.gm = gm
        self.gds = gds
        self.gmb = gmb

        self.ports["g"] = Port(name="g", parent=self)
        self.ports["d"] = Port(name="d", parent=self)
        self.ports["s"] = Port(name="s", parent=self)
        self.ports["b"] = Port(name="b", parent=self)

    def apply_symbolic_matrix(self, factory, index:int,   m:Matrix, x:list, b:Matrix, dimension:int):

        gm = self.gm
        if isinstance(self.gm, str):
            gm = symbols(self.gm)
        if gm is None:
            raise Exception("You need to provide a gm when doing a symbolic analysis")

        gds = self.gds
        if isinstance(self.gds, str):
            gds = symbols(self.gds)


        net_g = factory.get_net_of(self.ports["g"])
        net_d = factory.get_net_of(self.ports["d"])
        net_s = factory.get_net_of(self.ports["s"])
        net_b = factory.get_net_of(self.ports["b"])

        id_g = net_g.net_id
        id_d = net_d.net_id
        id_s = net_s.net_id
        id_b = net_b.net_id

        if gds is not None:
            m[id_d, id_d] += gds
            m[id_s, id_s] += gds
            m[id_d, id_s] += -gds
            m[id_s, id_d] += -gds

        m[id_d, id_g] += -gm
        m[id_s, id_g] += gm
        m[id_d, id_s] += gm
        m[id_s, id_s] += -gm

