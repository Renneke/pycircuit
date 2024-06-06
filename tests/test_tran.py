from pycircuit import Circuit, GND, NetFactory
from pycircuit.components import VDC, R, C, Component, Port, CurrentPort, IDC, D
import matplotlib.pyplot as plt
import numpy as np

def test_op():
    circuit = Circuit()

    c = C(name="C1", value = 1e-12, dc=1)
    r1 = R(name="R1", value=10e3)

    c["p"] << r1["p"]
    c["n"] << r1["n"] << GND

    circuit.add(c, r1)

    x, result = circuit.analyse_op()

    assert x[0] == "V0"
    assert result[0] == 1.0
    assert result[1] == 1e-4

def test_tran():
    circuit = Circuit()

    c = C(name="C1", value = 10e-12, dc=3)
    r1 = R(name="R1", value=100e3)
    vdc = VDC(name="VDC", dc=1.5)

    c["p"] << r1["p"]
    c["n"] << r1["n"] << vdc["p"]

    vdc["n"] << GND


    circuit.add(c, r1, vdc)

    x, result, t = circuit.analyse_tran(tstop=10e-6, tstep=0.3e-6)
    #plt.plot(t, result[0,:])

    r1.value = 10e3

    x, result, t = circuit.analyse_tran(tstop=10e-6, tstep=0.3e-6)
    #plt.plot(t, result[0,:])
    #plt.grid(True)
    #plt.show()

class MyComponent(Component):
    def __init__(self, name: str):
        super().__init__(name)

        self.ports["cur_out"] = CurrentPort("cur_out", parent=self, dc=0.0)

        self.state = False

    def update(self, factory:NetFactory, t:float, dt:float, signals:np.ndarray, g:np.ndarray, c:np.ndarray, x:list, b:np.ndarray):

        net = factory.get_net_of(self.ports["cur_out"])

        cap_volt = signals[net.net_id]
        if cap_volt < 1.5:
            self.state = True
        elif cap_volt > 2.5:
            self.state = False

        if self.state:
            b[net.net_id] = 30e-6


def test_custom_component():
    circuit = Circuit()

    c = C(name="C1", value = 10e-12, dc=3)
    r1 = R(name="R1", value=100e3)

    idc = IDC(name="idc1", dc = 10e-6)

    c["p"] << r1["p"]
    c["n"] << r1["n"] << idc["n"] << GND

    idc["p"] << c["p"]

    my_comp = MyComponent("X0")
    my_comp["cur_out"] << c["p"]

    circuit.add(c, r1, my_comp, idc)

    x, result, t = circuit.analyse_tran(tstop=10e-6, tstep=0.01e-6)
    plt.plot(t, result[0,:])

    r1.value=90e3

    x, result, t = circuit.analyse_tran(tstop=10e-6, tstep=0.01e-6)
    plt.plot(t, result[0,:])

    plt.grid(True)
    plt.show()

def test_diode():

    circuit = Circuit()

    vdd = VDC(name="VDD", dc = 1)
    r = R(name="R1", value=10e3)
    diode = D("D1", 1e-12, 5)

    vdd["p"] << r["p"]
    r["n"] << diode["p"]
    diode["n"] << vdd["n"] << GND

    circuit.add(vdd, r, diode)

    #circuit.analyse_dc(component=vdd, dc=np.linspace(start=0, stop=1.5, num=30))
    circuit.analyse_op()