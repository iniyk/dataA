from cmath import *

def S_PJ_func(cap, k, cap_max):
    ep = exp(K * (cap - cap_max))
    return ep / (1.0 + ep)

def S_PJ(cell):
    return S_PJ_func(cell.cap, cell.K, cell.cap_max)

def N_PJ(cell):
    return 0.0

class Edge():
    def __init__(self, pnt, prob=1.0, delay=1):
        self.pnt = pnt
        self.prob = prob
        self.delay = delay

class Cell():
    def __init__(self, id=(-1, -1, 0), cap=0, K=1.0, cap_max=40, PJ=N_PJ, flow_in=0, flow_out=0):
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
        self.flow_in = flow_in
        self.flow_out = flow_out
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
            flow += 1.0 * it.data(t-d) * e.prob * self.PJ(it)
        for e in self.nxtList():
            it = e.pnt
            d = e.delay
            flow += 1.0 * it.data(t-d) * e.prob * (1.0 - self.PJ(it))
        flow += self.flow_in - self.flow_out
        self.time = t
        self.S.append(flow)
        return flow
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

if __name__=="__main__":
    g = Graph("graph01.txt")
    cam = CellAutomat(g)
    cam.showCell(18, 19, 1)
