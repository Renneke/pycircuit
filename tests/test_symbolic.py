from pycircuit import Circuit, GND
from pycircuit.components import VDC, R, C, MOS
from sympy import symbols

def test_symbolic():
    circuit = Circuit()

    vdc = VDC(name="V1", ac=1)
    r1 = R(name="R1", value=1)
    r2 = R(name="R2", value=1)

    r1["p"] << vdc["p"]
    r1["n"] << vdc["n"] << GND

    r1["p"] << r2["p"]
    r1["n"] << r2["n"]


    circuit.add(vdc, r1, r2)

    result = circuit.analyse_symbolic()

    assert result["V0"] == 1.0
    assert result["I1_0"] == 2.0

def test_symbolic_with_cap():
    circuit = Circuit()

    vdc = VDC(name="V1", ac=1)
    r1 = R(name="R1", value=1)
    cap = C(name="R2", value=1)

    r1["p"] << vdc["p"]
    vdc["n"] << GND << cap["n"]

    r1["n"] << cap["p"]



    circuit.add(vdc, r1, cap)

    netlist = circuit.netlist()

    netlist.set_name(r1["n"], "vout")

    result = circuit.analyse_symbolic(netlist)

    s = symbols("s")

    assert result["vout"] == 1.0/(s + 1)

def test_netlist():

    circuit = Circuit()

    vdc = VDC(name="V1", ac=1.9)
    r1 = R(name="R1", value=100)
    r2 = R(name="R2", value=100)
    r3 = R(name="R3", value=100)
    r4 = R(name="R4", value=100)

    r1["p"] << vdc["p"] << r2["p"] << r4["p"]
    r1["n"] << vdc["n"] << r3["n"] << r4["n"]
    r2["n"] << r3["p"]

    circuit.add(vdc, r1, r2, r3, r4)


    factory = circuit.netlist()

    assert len(factory.nets) == 3
    factory.set_name(r1["p"], "Node1")
    factory.set_name(r1["n"], "Node2")
    factory.set_name(r3["p"], "Node3")

    assert r1["p"] in factory.get("Node1").ports
    assert r2["p"] in factory.get("Node1").ports
    assert r4["p"] in factory.get("Node1").ports
    assert r3["p"] not in factory.get("Node1").ports
    assert vdc["p"] in factory.get("Node1").ports

    assert r1["n"] in factory.get("Node2").ports
    assert r3["n"] in factory.get("Node2").ports
    assert r4["n"] in factory.get("Node2").ports
    assert r2["n"] not in factory.get("Node2").ports
    assert vdc["n"] in factory.get("Node2").ports

    assert r2["n"] in factory.get("Node3").ports
    assert r3["p"] in factory.get("Node3").ports



def test_symbolic_amp():
    circuit = Circuit()

    vdc = VDC(name="V1", ac=1)
    vdd = VDC(name="VDD", ac=0)
    r1 = R(name="R1", value=1)
    m1 = MOS(name="M1", gm="gm", gds="gds")

    m1["s"] << m1["b"] << vdc["n"] << vdd["n"] << GND
    vdc["p"] << m1["g"]
    m1["d"] << r1["n"]
    r1["p"] << vdd["p"]


    circuit.add(vdc, r1, vdd, m1)

    netlist = circuit.netlist()

    netlist.set_name(m1["d"], "VOUT")

    result = circuit.analyse_symbolic(netlist)

    gm, gds = symbols("gm, gds")
    assert result["VOUT"] == 1.0*gm/(gds+1)


