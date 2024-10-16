import heapq
import bisect
import traceback
import yaml

congruenteLinear = None

def p(s):
    with open('compara.txt', 'a') as arquivo:
        # Escreve a saída no arquivo usando o parâmetro file
        string = "{}{}".format(congruenteLinear.seed, s)
        print(string, file=arquivo)
class Evento:
    def __init__(self, tempo, evento_tipo, fila, destino, entrada):
        self.tempo = tempo
        self.evento_tipo = evento_tipo
        self.fila = fila
        self.destino = destino
        self.entrada = entrada

    def __lt__(self, other):
        return self.tempo < other.tempo
    

class Fila:
    def __init__(self, id, server, popMax, minChegada, maxChegada, minSaida, maxSaida):
        self.id = id
        self.status = {}
        self.ultimoEvento = 0
        self.pop = 0
        self.popMax = -1 if popMax is None else popMax
        self.server = server
        self.minChegada = -1 if minChegada is None else minChegada
        self.maxChegada = -1 if maxChegada is None else maxChegada
        self.minSaida = minSaida
        self.maxSaida = maxSaida 
        self.destinos = {}
        self.perdidos = 0
        self.chegados = 0
        self.tandem = None
        self.destinosStats = {"Rua" : 0}

    def setTandem(self, tandem):
        self.tandem = tandem

    def chegada(self, tempo, entrada):
         self.chegados += 1
         if self.pop == self.popMax and self.popMax >= 0:
            self.perdidos += 1
            return
         self.tempo = tempo
         self.updateTempo()
         self.pop += 1
         self.ultimoEvento = tempo
         if self.pop <= self.server:
            destino = self.getDestino()
            tempoEvento = tempo + (self.maxSaida - self.minSaida) * self.tandem.aleatorio.getNext() + self.minSaida
            p(" Delay Saida {:.4f}".format(tempoEvento))
            novoEvento = Evento(tempoEvento, "saida", self.id, destino, False)
            self.tandem.addToHeap(novoEvento)
         if entrada:
            tempoEvento = tempo + (self.maxChegada - self.minChegada) * self.tandem.aleatorio.getNext() + self.minChegada
            p(" Delay Chegada {:.4f}".format(tempoEvento))
            novoEvento = Evento(tempoEvento, "entrada", self.id, None, True)
            self.tandem.addToHeap(novoEvento)

    def saida(self, tempo):
        self.tempo = tempo
        self.updateTempo()
        self.pop -= 1
        self.ultimoEvento = tempo
        if self.pop >= self.server:
            destino = self.getDestino()
            tempoEvento = tempo + (self.maxSaida - self.minSaida) * self.tandem.aleatorio.getNext() + self.minSaida
            p(" Delay Saida {:.4f}".format(tempoEvento))
            novoEvento = Evento(tempoEvento, "saida", self.id, destino, False)
            self.tandem.addToHeap(novoEvento)

    def updateTempo(self):
         tempo = self.tempo - self.ultimoEvento + (self.status.get(self.pop) if self.status.get(self.pop) is not None else 0)
         self.status[self.pop] = tempo

    def setDestinos(self, destinos, destinosProb):
        self.destinos = sorted(zip(destinos, destinosProb), key=lambda x : x[1])
        for d in destinos:
            self.destinosStats[d] = 0

    def getDestino(self):
        if not self.destinos:
            self.destinosStats["Rua"] += 1
            return None
        if self.destinos[0][1] == 1:
            self.destinosStats[self.destinos[0][0]] += 1
            return self.destinos[0][0]
        prob = self.tandem.aleatorio.getNext()
        index = bisect.bisect_right(self.destinos, prob, key= lambda x: x[1])
        if index > (len(self.destinos) - 1):
            p(" Destino: {} -> null".format(self.id))
            self.destinosStats["Rua"] += 1
            return None
        self.destinosStats[self.destinos[index][0]] += 1
        p(" Destino: {} -> {}".format(self.id, self.destinos[index][0]))
        return self.destinos[index][0]

class TandemFila:
    def __init__(self, filas):
        self.filas = {}
        self.tempo = 0
        self.tempoTotal = 0
        self.eventos = []
        self.eventosIniciais = []
        self.aleatorio = None
        self.filas = filas
        for f in filas.values():
            f.setTandem(self)

    def setAleatorio(self, aleatorio):
        self.aleatorio = aleatorio

    def nextEvent(self):
        evento = heapq.heappop(self.eventos)
        self.tempo = evento.tempo
        fila = self.filas[evento.fila]
        if evento.evento_tipo == "entrada":
            fila.chegada(evento.tempo, evento.entrada)
        elif evento.evento_tipo == "saida":
            fila.saida(evento.tempo)
            if evento.destino is not None:
                destino = self.filas[evento.destino]
                destino.chegada(evento.tempo, evento.entrada)

    def addToHeap(self, evento):
        heapq.heappush(self.eventos, evento)

    def addToInicial(self, evento):
        heapq.heappush(self.eventos, evento)
        heapq.heappush(self.eventosIniciais, evento)

    def clear(self):
        for f in Tandem.filas.values():
            f.tempo = self.tempo
            f.updateTempo()
            f.tempo = 0
            f.ultimoEvento = 0
            f.pop = 0
        self.tempoTotal += self.tempo
        self.tempo = 0
        self.eventos.clear()
        for e in self.eventosIniciais:
            self.addToHeap(e)

class CongruenteLinear:
    def __init__(self, seed, perSeed):
        self.repeticoes = perSeed
        self.m = 281474976710656
        self.a = 25214903917
        self.c = 11
        self.count = 0
        self.seed = seed

    def hasNext(self):
        return self.count < self.repeticoes
    
    def getNext(self):
        if(self.count >= self.repeticoes):
            raise Exception("Acabou os numeros!")
        self.count += 1
        self.seed = ((self.a * self.seed) + self.c) % self.m
        if self.seed == 223576932655868:
            pass
        return self.seed/self.m

import yaml

with open('model.yml', 'r') as file:
    data = yaml.safe_load(file)

queues = data["queues"]
network = data["network"]
filas = {}
for id in queues.keys():
    f = queues[id]
    fila = Fila(id, f.get("servers"), f.get("capacity"), f.get("minArrival"), f.get("maxArrival"), f.get("minService"), f.get("maxService"))
    resultado = [origem for origem in network if origem['source'] == id]
    destinos = [item["target"] for item in resultado if "target" in item]
    destinos_prob = [item["probability"] for item in resultado if "probability" in item]
    fila.setDestinos(destinos, destinos_prob)
    filas[id] = fila

Tandem = TandemFila(filas)
arrivals = data['arrivals'] 
for id in arrivals.keys():
    Tandem.addToInicial(Evento(arrivals[id], "entrada", id, None, True))
seeds = data['seeds']
perSeed = data['rndnumbersPerSeed']

for i in seeds:
    congruenteLinear = CongruenteLinear(i, perSeed)
    Tandem.setAleatorio(congruenteLinear)
    print("Calculando para a seed ", i)
    try:
        while congruenteLinear.hasNext():
            Tandem.nextEvent()
    except Exception as e:
        pass
    Tandem.clear()

with open('output.txt', 'w') as arquivo:
    for f in list(Tandem.filas.values()):
        keys = list(f.status.keys())
        print(f.id, "(G/G/{}{})".format(f.server, "/{}".format(f.popMax) if f.popMax > 0 else ""), end = '\n')
        print(f.id, "(G/G/{}{})".format(f.server, "/{}".format(f.popMax) if f.popMax > 0 else ""), end = '\n', file=arquivo)
        for k in keys:
            print("{:7d}{:21.4f}{:21.2f}%".format(k, f.status[k], f.status[k] / (Tandem.tempo + Tandem.tempoTotal) * 100.0))
            print("{:7d}{:21.4f}{:21.2f}%".format(k, f.status[k], f.status[k] / (Tandem.tempo + Tandem.tempoTotal) * 100.0), file=arquivo)
        keys = list(f.destinosStats)
        for k in keys:
            print("Enviados para ", k, ": ", f.destinosStats[k], file=arquivo)
            print("Enviados para ", k, ": ", f.destinosStats[k])
        print("Numero de perdidos : ", f.perdidos, " Chegados : ", f.chegados, end = '\n\n', file=arquivo)
        print("Numero de perdidos : ", f.perdidos, " Chegados : ", f.chegados, end = '\n\n')
    
    print("Tempo", " medio" if len(seeds) > 1 else "" ," de simulacao global: ", "{:.4f}".format(Tandem.tempoTotal/len(seeds)), sep= '',file=arquivo)
    print("Tempo", " medio" if len(seeds) > 1 else "" ," de simulacao global: ",  "{:.4f}".format(Tandem.tempoTotal/len(seeds)), sep= '')
arquivo.close()
input()