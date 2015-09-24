from cmath import *
import math

def S_PJ_func(cap, k, cap_max):
    ep = exp(k * (cap - cap_max))
    return ep / (1.0 + ep)

def S_PJ(cell):
    return 0.0
    #return S_PJ_func(cell.cap, cell.K, cell.cap_max)

def N_PJ(cell):
    return 0.0

class Edge():
    def __init__(self, pnt, prob=0.25, delay=1):
        self.pnt = pnt
        self.prob = prob
        self.delay = delay

class Cell():
    def __init__(self, id=(-1, -1, 0), cap=0, K=1.0, cap_max=40, PJ=N_PJ):
        #runtime data
        self.id = id
        self.cap = cap
        #param defined
        self.K = K
        self.cap_max = cap_max
        self.nxt = []
        self.pre = []
        self.S = []
        self.S.append(cap)
        self.time = 0
        self.PJ = PJ
        self.flow_in = [0]
        self.flow_out = [0]
    def setCap(self, cap):
        self.cap = cap
        self.S[-1] = cap
    def gFlowIn(self, time):
        if len(self.flow_in) <= time:
            return 0
        return self.flow_in[time]
    def gFlowOut(self, time):
        if len(self.flow_out) <= time:
            return 0
        return self.flow_out[time]
    def addNxt(self, edge):
        self.nxt.append(edge)
    def addPre(self, edge):
        self.pre.append(edge)
    def nxtList(self):
        for edge in self.nxt:
            yield edge
    def preList(self):
        for edge in self.pre:
            yield edge
    def data(self, time):
        return self.S[time]
    def step(self):
        flow = 0.0
        t = self.time + 1
        for e in self.preList():
            it = e.pnt
            d = e.delay
            flow += 1.0 * it.data(t-d) * e.prob * (1.0 - self.PJ(it))
        for e in self.nxtList():
            it = e.pnt
            d = e.delay
            flow += 1.0 * it.data(t-d) * e.prob * self.PJ(it)
        flow += self.gFlowIn(t) - self.gFlowOut(t)
        if flow < 0:
            flow = 0
        flow = math.ceil(flow)
        self.time = t
        self.S.append(int(flow))
        return flow
    def fix(self, time, cap_view):
        while len(self.flow_in) <= time:
            self.flow_in.append(0)
        while len(self.flow_out) <= time:
            self.flow_out.append(0)
        delta = cap_view - self.S[time]
        self.flow_out[time] = -delta
        self.S[time] = cap_view
        return
        if self.id[2] == 0:
            if delta < 0:
                self.flow_in[time] = 0
            else:
                self.S[time] = self.S[time] + delta
                self.flow_in[time] = delta
        else:
            if delta > 0:
                self.flow_out[time] = 0
            else:
                self.S[time] = self.S[time] + delta
                self.flow_out[time] = -delta
    def action(self, start_time, end_time):
        for i in (1, end_time+1):
            if self.time<i:
                self.step()
            if i>=start_time:
                yield self.data(i)

class CellAutomat():
    def __init__(self, graph):
        print "Starting building CellAutomat..."
        self.cells = []
        self.cell_map = {}
        for node in graph.nodes:
            i = node.head
            while i != -1:
                #print "build cell " + str(node.id) + " " + str(graph.pnt[i])
                self.gCell(node.id, graph.pnt[i], 0)
                self.gCell(node.id, graph.pnt[i], 1)
                i = graph.nxt[i]
        for node in graph.nodes:
            i = node.head
            while i != -1:
                a = node.id
                b = graph.pnt[i]
                self.linkTo(self.gCell(a, b, 0), self.gCell(a, b, 1))
                #self.gLnk(a, b, a, 1, 0)
                j = graph.nodes[b].head
                while j != -1:
                    c = graph.pnt[j]
                    self.gLnk(a, b, c, 1, 0)
                    j = graph.nxt[j]
                i = graph.nxt[i]
        print "CellAutomat building complete."
    def reset(self):
        print "Starting reset threading..."
        for cell in self.cells:
            cell.time = 0
            cell.cap = 0
            cell.S = [cell.cap]
        print "Reset complete."
    def setCap(self, u, v, direct, cap):
        c = self.gCell(u, v, direct)
        c.cap = cap
    def linkTo(self, c1, c2):
        edge1 = Edge(c2)
        edge2 = Edge(c1)
        c1.addNxt(edge1)
        c2.addPre(edge2)

    def gLnk(self, a, b, c, d1, d2):
        c1 = self.gCell(a, b, d1)
        c2 = self.gCell(b, c, d2)
        self.linkTo(c1, c2)

    def gCell(self, u, v, direct):
        if (u, v, direct) in self.cell_map:
            return self.cell_map[(u, v, direct)]
        else:
            cell = Cell(id=(u, v, direct), PJ=S_PJ)
            self.cell_map[cell.id] = cell
            self.cells.append(cell)
            return cell
    def showCell(self, u, v, direct):
        cell = self.gCell(u, v, direct)
        print "Show (%d %d %d) 's pre list" % (u, v, direct)
        for e in cell.preList():
            print e.pnt.id
        print "Show (%d %d %d) 's nxt list" % (u, v, direct)
        for e in cell.nxtList():
            print e.pnt.id

class Node():
    def __init__(self, id, pos_x = 0, pos_y = 0):
        self.head = -1
        self.id = id
        self.pos_x = pos_x
        self.pos_y = pos_y

class Graph():
    def __init__(self, file_path):
        self.nxt = []
        self.pnt = []
        self.edge_map = {}
        self.caps = []
        self.edge_num = 0
        self.node_num = 0
        self.rdFile(file_path)

    def getCap(self, u, v, time):
        eID = self.gEdgeID(u, v)
        if eID == -1:
            return 0
        else:
            return self.caps[eID][time]

    def gEdgeID(self, u, v):
        if (u, v) in self.edge_map:
            return self.edge_map[(u, v)]
        else:
            return -1

    def edgeList(self):
        for node in self.nodes:
            i = node.head
            u = node.id
            while i != -1:
                v = self.pnt[i]
                i = self.nxt[i]
                yield (u, v)

    def addEdge(self, u, v, c):
        if (u, v) in self.edge_map:
            pt = self.edge_map[(u, v)]
            self.caps[pt].append(c)
        else:
            self.nxt.append(self.nodes[u].head)
            self.pnt.append(v)
            self.caps.append([c])
            self.nodes[u].head = self.edge_num
            self.edge_map[(u, v)] = self.edge_num
            self.edge_num += 1

    def setPos(self, id, pos_x, pos_y):
        self.nodes[id].pos_x = pos_x
        self.nodes[id].pos_y = pos_y

    def rdFile(self, file_path):
        print "Starting reading graph file..."
        f = open(file_path, "r")
        self.node_num = int(f.readline())
        self.nodes = [Node(i) for i in range(self.node_num+1)]
        for node in f.readlines():
            line_list = node.split(" ")
            u = int(line_list[0])
            v = int(line_list[1])
            for cap in line_list[2:]:
                self.addEdge(u, v, int(cap))
        print "Graph building complete."

def getParam():
    g = Graph("graph01.txt")
    all_time = len(g.caps)
    cam = CellAutomat(g)
    #init
    for (u, v) in g.edgeList():
        cell = cam.gCell(u, v, 1)
        cell.setCap(g.getCap(u, v, 0))
        #if cell.S[-1]!=0:
        #    print cell.id, " ", cell.time, " ", cell.S[-1]
    for time in range(1, all_time * 2):
        for cell in cam.cells:
            cell.step()
            #if int(cell.S[-1])!=0:
        #    if cell.S[-1]!=0:
        #        print cell.id, " ", time , " ", cell.S[-1]
            if cell.id[2] == 1:
                cell.fix(time, g.getCap(cell.id[0], cell.id[1], time/2))
                print cell.flow_in[time], " ", cell.flow_out[time]
    return cam

def runCellAutomat(cwp, data_file_handle):
    g = Graph("graph02.txt")
    all_time = len(g.caps)
    cwp.reset()
    for (u, v) in g.edgeList():
        cell = cwp.gCell(u, v, 1)
        cell.setCap(g.getCap(u, v, 0))
    for time in range(1, all_time * 2):
        for cell in cwp.cells:
            cell.step()
            if cell.id[2] == 1 and time % 2 == 0:
                u = int(cell.id[0])
                v = int(cell.id[1])
                #print cell.S[-1]
                cap = int(cell.S[-1])
                cap_view = int(g.getCap(cell.id[0], cell.id[1], time/2))
                data_file_handle.write("%d %d \t| %d \t| %d\n" % (u, v, cap, cap_view))

if __name__=="__main__":
    cwp = getParam()
    file_output = open("result.txt", "w")
    runCellAutomat(cwp, file_output)
    file_output.close()
