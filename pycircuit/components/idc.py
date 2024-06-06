from .component import Component, Port, Analysis
from sympy import Matrix, symbols

class IDC(Component):
    def __init__(self, name: str, dc:float|str):
        super().__init__(name)

        self.dc = dc
        self.ports["p"] = Port(name="p", parent=self)
        self.ports["n"] = Port(name="n", parent=self)

    def get_num_additional_row_columns(self, analysis:Analysis):
        return 0

    def apply_symbolic_matrix(self, factory, index:int, m:Matrix, x:list, b:Matrix, dimension:int):

        dc = self.dc
        if isinstance(self.dc, str):
            dc = symbols(self.dc)

        net_n = factory.get_net_of(self.ports["n"])
        net_p = factory.get_net_of(self.ports["p"])

        id_n, id_p = net_n.net_id, net_p.net_id

        b[id_p] += dc
        b[id_n] -= dc


    def apply_tran_matrix(self, factory, index:int, g:Matrix, c:Matrix, x:list, b:Matrix, dimension:int):
        """A capacitor behaves like a voltage source of voltage self.dc"""

        net_n = factory.get_net_of(self.ports["n"])
        net_p = factory.get_net_of(self.ports["p"])

        id_n, id_p = net_n.net_id, net_p.net_id

        b[id_p, 0] += self.dc
        b[id_n, 0] -= self.dc

    def apply_op_matrix(self, factory, index:int, m:Matrix, x:list, b:Matrix, dimension:int):
        """A capacitor behaves like a voltage source of voltage self.dc"""

        net_n = factory.get_net_of(self.ports["n"])
        net_p = factory.get_net_of(self.ports["p"])

        id_n, id_p = net_n.net_id, net_p.net_id

        b[id_p, 0] += self.dc
        b[id_n, 0] -= self.dc



