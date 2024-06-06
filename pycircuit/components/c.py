from .component import Component, Port, Analysis
from sympy import Matrix, symbols

class C(Component):
    def __init__(self, name: str, value:float|str, dc:float=0.0):
        super().__init__(name)

        self.value = value
        self.dc = dc
        """Initial dc value for AC and transient analysis"""
        self.ports["p"] = Port(name="p", parent=self)
        self.ports["n"] = Port(name="n", parent=self)

    def get_num_additional_row_columns(self, analysis:Analysis):
        if analysis in [Analysis.OP]:
            return 1
        return 0

    def apply_tran_matrix(self, factory, index:int, g:Matrix, c:Matrix, x:list, b:Matrix, dimension:int):
        """A capacitor behaves like a voltage source of voltage self.dc"""

        net_n = factory.get_net_of(self.ports["n"])
        net_p = factory.get_net_of(self.ports["p"])

        id_n, id_p = net_n.net_id, net_p.net_id

        c[id_p, id_p] +=  self.value
        c[id_n, id_n] +=  self.value
        c[id_p, id_n] += -self.value
        c[id_n, id_p] += -self.value

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

        x.append(symbols(f"I_initial_{id_n}_{id_p}"))


    def apply_symbolic_matrix(self, factory, index:int, m:Matrix, x:list, b:Matrix, dimension:int):

        value = self.value
        if isinstance(self.value, str):
            value = symbols(self.value)

        net_n = factory.get_net_of(self.ports["n"])
        net_p = factory.get_net_of(self.ports["p"])

        id_n, id_p = net_n.net_id, net_p.net_id

        s = symbols("s")
        m[id_p, id_p] += s*value
        m[id_n, id_n] += s*value
        m[id_p, id_n] += -s*value
        m[id_n, id_p] += -s*value
