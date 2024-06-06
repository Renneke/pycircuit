from .component import Component, Port
from sympy import Matrix, symbols

class R(Component):
    def __init__(self, name: str, value:float|str):
        super().__init__(name)

        self.value = value
        self.ports["p"] = Port(name="p", parent=self)
        self.ports["n"] = Port(name="n", parent=self)


    def apply_tran_matrix(self, factory, index:int, g:Matrix, c:Matrix, x:list, b:Matrix, dimension:int):
        """A capacitor behaves like a voltage source of voltage self.dc"""

        net_n = factory.get_net_of(self.ports["n"])
        net_p = factory.get_net_of(self.ports["p"])

        id_n, id_p = net_n.net_id, net_p.net_id

        g[id_p, id_p] +=  1/self.value
        g[id_n, id_n] +=  1/self.value
        g[id_p, id_n] += -1/self.value
        g[id_n, id_p] += -1/self.value

    def apply_op_matrix(self, factory, index:int, m:Matrix, x:list, b:Matrix, dimension:int):
        """A capacitor behaves like a voltage source of voltage self.dc"""

        net_n = factory.get_net_of(self.ports["n"])
        net_p = factory.get_net_of(self.ports["p"])

        id_n, id_p = net_n.net_id, net_p.net_id

        m[id_p, id_p] +=  1/self.value
        m[id_n, id_n] +=  1/self.value
        m[id_p, id_n] += -1/self.value
        m[id_n, id_p] += -1/self.value


    def apply_symbolic_matrix(self, factory, index:int,   m:Matrix, x:list, b:Matrix, dimension:int):

        value = self.value
        if isinstance(self.value, str):
            value = symbols(self.value)

        net_n = factory.get_net_of(self.ports["n"])
        net_p = factory.get_net_of(self.ports["p"])

        id_n, id_p = net_n.net_id, net_p.net_id

        m[id_p, id_p] += 1/value
        m[id_n, id_n] += 1/value
        m[id_p, id_n] += -1/value
        m[id_n, id_p] += -1/value
