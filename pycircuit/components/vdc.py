from .component import Component, Port, Analysis
from sympy import Matrix, symbols

class VDC(Component):
    def __init__(self, name: str, dc:float=0.0, ac:float|str=0.0):
        super().__init__(name)

        self.dc = dc
        self.ac = ac
        self.ports["p"] = Port(name="p", parent=self)
        self.ports["n"] = Port(name="n", parent=self)

    def get_num_additional_row_columns(self, analysis:Analysis):
        return 1

    def apply_symbolic_matrix(self, factory, index:int, m:Matrix, x:list, b:Matrix, dimension:int):

        ac = self.ac
        if isinstance(self.ac, str):
            ac = symbols(self.ac)

        net_n = factory.get_net_of(self.ports["n"])
        net_p = factory.get_net_of(self.ports["p"])

        id_n, id_p = net_n.net_id, net_p.net_id

        m[index, id_p] += 1
        m[index, id_n] += -1
        m[id_p, index] += -1
        m[id_n, index] += 1

        b[index] = ac

        x.append(symbols(f"I{id_n}_{id_p}"))


    def apply_tran_matrix(self, factory, index:int, g:Matrix, c:Matrix, x:list, b:Matrix, dimension:int):
        """A capacitor behaves like a voltage source of voltage self.dc"""

        net_n = factory.get_net_of(self.ports["n"])
        net_p = factory.get_net_of(self.ports["p"])

        id_n, id_p = net_n.net_id, net_p.net_id

        g[index, id_p] += 1
        g[index, id_n] += -1
        g[id_p, index] += -1
        g[id_n, index] += 1

        b[index] = self.dc

        x.append(symbols(f"I{id_n}_{id_p}"))

    def apply_op_matrix(self, factory, index:int, m:Matrix, x:list, b:Matrix, dimension:int):
        """A capacitor behaves like a voltage source of voltage self.dc"""

        net_n = factory.get_net_of(self.ports["n"])
        net_p = factory.get_net_of(self.ports["p"])

        id_n, id_p = net_n.net_id, net_p.net_id

        m[index, id_p] += 1
        m[index, id_n] += -1
        m[id_p, index] += -1
        m[id_n, index] += 1

        b[index] = self.dc

        x.append(symbols(f"I{id_n}_{id_p}"))



