
import math
from dataclasses import dataclass

import numpy as np
from scipy.sparse import csc_matrix, csr_matrix
from scipy.sparse.linalg import spsolve
from sympy import Matrix, linsolve, simplify, symbols, zeros

from .components import Analysis, Component, Port
from .netlister.net_factory import Net, NetFactory
from .utils import delete_from_csr


@dataclass
class Node:
    name: str
    connected : dict[str, Port]


class Circuit:
    def __init__(self) -> None:
        self.components : list[Component] = []

    def add(self, *components):
        for component in components:
            self.components.append(component)

    def netlist(self) -> NetFactory:
        factory = NetFactory()

        for component in self.components:
            for port in component.ports.values():
                for connected_port in port.connections:
                    factory.add_connection(port, connected_port)

        # Make sure that each net gets an unique id starting from 0 to N
        # N is the number of nodes
        # These values are used for identifying the row/cols in the Matrix
        # for each net
        factory.assign_net_ids()

        return factory

    def _get_num_additional_row_columns(self, analysis:Analysis)->int:
        counter = 0
        for component in self.components:
            counter += component.get_num_additional_row_columns(analysis)
        return counter

    def analyse_op(self, factory: NetFactory|None = None):

        # Create a netlist if it has not been created yet
        factory = factory or self.netlist()

        # Find out the dimensions of the matrix
        additional_row_columns = self._get_num_additional_row_columns(Analysis.OP)
        dimension = len(factory.nets) + additional_row_columns

        m = csr_matrix((dimension, dimension), dtype=np.float64)
        b = csr_matrix((dimension, 1), dtype=np.float64)

        # Create x (variables to solve for)
        x = []
        for net in factory.nets:
            if net.name:
                x.append(net.name)
            else:
                x.append(f"V{net.net_id}")

        # Construct matrix
        additiona_row_cols_counter = len(factory.nets)
        for component in self.components:
            additional_row_columns = component.get_num_additional_row_columns(Analysis.OP)
            component.apply_op_matrix(factory,
                                      additiona_row_cols_counter if additional_row_columns else -1,
                                      m,
                                      x,
                                      b,
                                      dimension)
            additiona_row_cols_counter += additional_row_columns

        # Remove ground nets
        ids_to_remove = []
        for net in factory.nets:
            if net.is_gnd():
                ids_to_remove.append(net.net_id)
                del x[net.net_id]

        m = delete_from_csr(m, ids_to_remove, ids_to_remove)
        b = delete_from_csr(b, ids_to_remove, [])

        answ = spsolve(m, b)
        return x, answ

    def analyse_tran(self, tstop:float, tstep:float, tstart:float=0.0, factory: NetFactory|None = None):

        # Create a netlist if it has not been created yet
        factory = factory or self.netlist()

        # Find out the dimensions of the matrix
        additional_row_columns = self._get_num_additional_row_columns(Analysis.TRANSIENT)
        dimension = len(factory.nets) + additional_row_columns

        g = csr_matrix((dimension, dimension), dtype=np.float64)
        c = csr_matrix((dimension, dimension), dtype=np.float64)
        b = csr_matrix((dimension, 1), dtype=np.float64)

        # Create x (variables to solve for)
        x = []
        for net in factory.nets:
            if net.name:
                x.append(net.name)
            else:
                x.append(f"V{net.net_id}")



        sig = csr_matrix((dimension, 1), dtype=np.float64)
        sig[0] = 1

        # Construct matrix
        additiona_row_cols_counter = len(factory.nets)
        for component in self.components:
            additional_row_columns = component.get_num_additional_row_columns(Analysis.TRANSIENT)
            component.apply_tran_matrix(factory,
                                            additiona_row_cols_counter if additional_row_columns else -1,
                                            g,
                                            c,
                                            x,
                                            b,
                                            dimension)
            additiona_row_cols_counter += additional_row_columns

        # Remove ground nets
        ids_to_remove = []
        for net in factory.nets:
            if net.is_gnd():
                ids_to_remove.append(net.net_id)
                del x[net.net_id]
        sig = delete_from_csr(sig, ids_to_remove, [])
        g = delete_from_csr(g, ids_to_remove, ids_to_remove)
        c = delete_from_csr(c, ids_to_remove, ids_to_remove)
        b = delete_from_csr(b, ids_to_remove, [])

        print("Solve for OP solution")
        op_x, op_solution = self.analyse_op(factory)

        for var in x:
            op_val_id = op_x.index(var)
            val_id = x.index(var)
            sig[val_id,0] = op_solution[op_val_id]

            print(f"{var} = {op_solution[op_val_id]}")

        print("Start transient solution")
        N = math.ceil(tstop/tstep)
        signals = sig.toarray()

        for i in range(N):

            percentage = round(i*100/N)
            if (percentage+1)%3 == 0:
                print(percentage, "%", end='\r')

            last_solution = signals[:, -1].reshape(-1, 1)

            # Apply dynamic updates of components

            g_add = csr_matrix(g.shape, dtype=np.float64)
            c_add = csr_matrix(c.shape, dtype=np.float64)
            b_add = csr_matrix(b.shape, dtype=np.float64)

            for component in self.components:
                component.update(factory, i*tstep, tstep, last_solution, g_add, c_add, x, b_add)

            solution = spsolve((tstep*(g+g_add)+(c+c_add)), (b+b_add)*tstep+(c+c_add)*last_solution)
            signals = np.c_[signals, solution]


        return x, signals, np.array(range(N+1))*tstep


    def analyse_symbolic(self, factory: NetFactory|None = None)->dict[str, Matrix]:

        # Create a netlist if it has not been created yet
        factory = factory or self.netlist()

        # Find out the dimensions of the matrix
        additional_row_columns = self._get_num_additional_row_columns(Analysis.SYMBOLIC)
        dimension = len(factory.nets) + additional_row_columns


        # Create matrix
        m = zeros(dimension, dimension)
        # Create right hand side
        b = zeros(dimension, 1)
        # Create x (variables to solve for)
        x = []
        for net in factory.nets:
            if net.name:
                x.append(symbols(net.name))
            else:
                x.append(symbols(f"V{net.net_id}"))

        # Construct matrix
        additiona_row_cols_counter = len(factory.nets)
        for component in self.components:
            additional_row_columns = component.get_num_additional_row_columns(Analysis.SYMBOLIC)
            component.apply_symbolic_matrix(factory,
                                            additiona_row_cols_counter if additional_row_columns else -1,
                                            m,
                                            x,
                                            b,
                                            dimension)
            additiona_row_cols_counter += additional_row_columns

        # Remove ground nets
        for net in factory.nets:
            if net.is_gnd():
                m.col_del(net.net_id)
                m.row_del(net.net_id)
                del x[net.net_id]
                b.row_del(net.net_id)

        answ = simplify(m.solve(b))

        return {str(x[i]): answ[i] for i, _ in enumerate(x)}
