# Devices: Device objects for GridWorkbench
#
# Adam Birchfield, Texas A&M University
# 
# Log:
# 9/29/2021 Initial version, rearranged from prior draft so that most object fields
#   are only listed in one place, the PW_Fields table. Now to add a field you just
#   need to add it in that list.
# 11/2/2021 Renamed this file to core and added fuel type object
# 1/22/22 Separated from gridworkbench to contain Gen, Load, Shunt, Branch, (later ThreeWinder and Converter)
# 4/2/22 Need to add some default fields
# 8/10/2022 Support connecting and disconnecting branches, and creating branches
#   with buses instead of nodes (just choose first node)
#
from .containers import Node, Bus

class Gen:

    def __init__(self, node, id):
        self._node = node
        if not isinstance(node, Node):
            raise Exception(f"Invalid node provided to create gen {id}")
        self.id = id
        
        self.status = True
        self.p = 0
        self.q = 0
        self.pset = 0
        self.qset = 0
        self.pmax = 0
        self.pmin = 0
        self.qmax = 0
        self.qmin = 0
        self.reg_bus_num = self.bus.number
        self.reg_pu_v = 1
        self.p_auto_status = True
        self.q_auto_status = True
        self.fuel_type = "Unknown"
        self.sbase = 100
        self.fixed_cost = 0
        self.fuel_cost = 0
        self.cost_b = 0
        self.cost_c = 0
        self.cost_d = 0

    
    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        if hasattr(self, "_id"):
            del self.node._gen_map[self._id]
        if not isinstance(value, str):
            raise Exception(f"Gen id must be string")
        if len(value) < 1 or len(value) > 2:
            raise Exception(f"Gen ID '{value}' must be 1 or 2 characters")
        if value in self.node._gen_map:
            raise Exception(f"Gen ID '{value}' already exists!")
        self._id = value
        self.node._gen_map[self._id] = self

    def __str__(self):
        return f"Gen {self.node.number} {self.id} " \
            + f"{self.node.name if hasattr(self.node, 'name') else ''}"

    def __repr__(self):
        return str(self) + f" {hex(id(self))}"

    @property
    def node(self):
        return self._node

    @property
    def bus(self):
        return self.node.bus


class Load:

    def __init__(self, node, id):
        self._node = node
        if not isinstance(node, Node):
            raise Exception(f"Invalid node provided to create load {id}")
        self.id = id
        for f in self.bus.wb.load_pw_fields:
            setattr(self, f[0], f[2])

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        if hasattr(self, "_id"):
            del self.node._load_map[self._id]
        if not isinstance(value, str):
            raise Exception(f"Load id must be string")
        if len(value) < 1 or len(value) > 2:
            raise Exception(f"Load ID '{value}' must be 1 or 2 characters")
        if value in self.node._load_map:
            raise Exception(f"Load ID '{value}' already exists!")
        self._id = value
        self.node._load_map[self._id] = self

    def __str__(self):
        return f"Load {self.node.number} {self.id} " \
            + f"{self.node.name if hasattr(self.node, 'name') else ''}"

    def __repr__(self):
        return str(self) + f" {hex(id(self))}"

    @property
    def node(self):
        return self._node

    @property
    def bus(self):
        return self.node.bus


class Shunt:

    def __init__(self, node, id):
        self._node = node
        if not isinstance(node, Node):
            raise Exception(f"Invalid node provided to create shunt {id}")
        self.id = id
        node._shunt_map[id] = self
        for f in self.bus.wb.shunt_pw_fields:
            setattr(self, f[0], f[2])

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        if hasattr(self, "_id"):
            del self.node._shunt_map[self._id]
        if not isinstance(value, str):
            raise Exception(f"Shunt id must be string")
        if len(value) < 1 or len(value) > 2:
            raise Exception(f"Shunt ID '{value}' must be 1 or 2 characters")
        if value in self.node._shunt_map:
            raise Exception(f"Shunt ID '{value}' already exists!")
        self._id = value
        self.node._shunt_map[self._id] = self

    def __str__(self):
        return f"Shunt {self.node.number} {self.id} " \
            + f"{self.node.name if hasattr(self.node, 'name') else ''}"

    def __repr__(self):
        return str(self) + f" {hex(id(self))}"

    @property
    def node(self):
        return self._node

    @property
    def bus(self):
        return self.node.bus


class Branch:

    def __init__(self, from_node, to_node, id, connect=True):
        self._connected = False
        self._from_node = None
        self._to_node = None
        self._id = "0"
        self.from_node = from_node
        self.to_node = to_node
        self.id = id
        for f in self.from_bus.wb.branch_pw_fields:
            setattr(self, f[0], f[2])
        if connect:
            self.connect()

        self.tap = 1
        self.phase = 0
        self.status = True
        self.R = 0
        self.X = 0.1
        self.B = 0
        self.G = 0
        self.MVA_Limit_A = 0
        self.MVA_Limit_B = 0
        self.MVA_Limit_C = 0
        self.p1 = 0
        self.p2 = 0
        self.q1 = 0
        self.q2 = 0
        self.length = 0
        self.branch_device_type = "line"
        
    def connect(self):
        if not self.connected:
            if (self.to_node.number, self._id) in self.from_node._branch_from_map:
                raise Exception(f"Branch ID '{self._id}' already exists!")
            if (self.from_node.number, self._id) in self.to_node._branch_to_map:
                raise Exception(f"Branch ID '{self._id}' already exists!")
            self.from_node._branch_from_map[(self.to_node.number, self._id)] = self
            self.to_node._branch_to_map[(self.from_node.number, self._id)] = self
            self._connected = True

    def disconnect(self):
        if self.connected:
            del self.from_node._branch_from_map[(self.to_node.number, self._id)]
            del self.to_node._branch_to_map[(self.from_node.number, self._id)]
            self._connected = False

    @property
    def connected(self):
        return self._connected

    @connected.setter
    def connected(self, value):
        if value:
            self.connect()
        else:
            self.disconnect()

    @property
    def from_node(self):
        return self._from_node

    @from_node.setter
    def from_node(self, value):
        if not isinstance(value, Node):
            if isinstance(value, Bus):
                value = value.nodes[0]
            else:
                raise Exception(f"Invalid from node provided to create branch!")
        if self.connected:
            self.disconnect()
            self._from_node = value
            self.connect()
        else:
            self._from_node = value
    
    @property
    def to_node(self):
        return self._to_node

    @to_node.setter
    def to_node(self, value):
        if not isinstance(value, Node):
            if isinstance(value, Bus):
                value = value.nodes[0]
            else:
                raise Exception(f"Invalid to node provided to create branch!")
        if self.connected:
            self.disconnect()
            self._to_node = value
            self.connect()
        else:
            self._to_node = value

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        if not isinstance(value, str):
            raise Exception(f"Branch id must be string")
        if len(value) < 1 or len(value) > 2:
            raise Exception(f"Branch ID '{value}' must be 1 or 2 characters")
        if self.connected:
            self.disconnect()
            self._id = value
            self.connect()
        else:
            self._id = value
        
    def __str__(self):
        return f"Branch {self.from_node.number} {self.to_node.number} {self.id} " \
            + f"{self.from_node.name if hasattr(self.from_node, 'name') else ''} to " \
            + f"{self.to_node.name if hasattr(self.to_node, 'name') else ''}"

    def __repr__(self):
        return str(self) + f" {hex(id(self))}"

    @property
    def from_bus(self):
        return self.from_node.bus

    @property
    def to_bus(self):
        return self.to_node.bus