import heapq
import bisect
import yaml

with open('model.yml', 'r') as f:
   data = yaml.load(f, Loader=yaml.Loader)
     
print(data.get('arrivals').get('Q1'))

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
    def __init__(self, id, popMax, server, minChegada, maxChegada, minSaida, maxSaida):
        self.id = id
        self.status = {}
        self.ultimoEvento = 0
        self.pop = 0
        self.popMax = popMax
        self.server = server
        self.minChegada = minChegada 
        self.maxChegada = maxChegada 
        self.minSaida = minSaida
        self.maxSaida = maxSaida 
        self.destinos = {}
        self.perdidos = 0
        self.tandem = None

    def setTandem(self, tandem):
        self.tandem = tandem

    def chegada(self, tempo, entrada):
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
            novoEvento = Evento(tempoEvento, "saida", self.id, destino, False)
            self.tandem.addToHeap(novoEvento)
         if entrada:
            tempoEvento = tempo + (self.maxChegada - self.minChegada) * self.tandem.aleatorio.getNext() + self.minChegada
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
            novoEvento = Evento(tempoEvento, "saida", self.id, destino, False)
            self.tandem.addToHeap(novoEvento)

    def updateTempo(self):
         tempo = self.tempo - self.ultimoEvento + (self.status.get(self.pop) if self.status.get(self.pop) is not None else 0)
         self.status[self.pop] = tempo

    def setDestinos(self, destinos, destinosProb):
        self.destinos = sorted(zip(destinos, destinosProb), key=lambda x : x[1])

    def getDestino(self):
        if not self.destinos:
            return None
        if self.destinos[0][1] == 1:
            return self.destinos[0][0]
        prob = self.tandem.aleatorio.getNext()
        index = bisect.bisect_right(self.destinos, prob, key= lambda x: x[1])
        if index > (len(self.destinos) - 1):
            index -= 1
        return self.destinos[index][0]

class TandemFila:
    def __init__(self, filas):
        self.filas = {}
        self.tempo = 0
        self.tempoTotal = 0
        self.eventos = []
        self.aleatorio = None
        for f in filas:
            f.setTandem(self)
            self.filas[f.id] = f

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

    def clear(self):
        self.tempoTotal += self.tempo
        self.tempo = 0

class CongruenteLinear:
    def __init__(self, seed):
        self.repeticoes = 10
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
        return self.seed/self.m

Q1 = Fila("Q1", 5, 1, 20.0, 40.0, 10.0, 12.0)
Q2 = Fila("Q2", 2, 5, -1, -1, 30, 120)
Q3 = Fila("Q3", 2, 5, -1, -1, 15, 60)
Q4 = Fila("Q4", -1, 3, -1, -1, 5, 15)
Q1_destinos = ["Q2", "Q3"]
Q1_prob = [0.78, 0.12]
Q2_destinos = ["Q1", "Q3", "Q4"]
Q2_prob = [0.1, 0.27, 0.63]
Q3_destinos = ["Q4"]
Q3_prob = [1]
Q1.setDestinos(Q1_destinos, Q1_prob)
Q2.setDestinos(Q2_destinos, Q2_prob)
Q3.setDestinos(Q3_destinos, Q3_prob)
eventoInicial = Evento(45, "entrada", "Q1", None, True)
Tandem = TandemFila([Q1, Q2, Q3, Q4])
Tandem.addToHeap(eventoInicial)

for i in range(1, 2):
    congruenteLinear = CongruenteLinear(i)
    Tandem.setAleatorio(congruenteLinear)
    try:
        while congruenteLinear.hasNext():
            Tandem.nextEvent()
    except:
        pass
    Tandem.clear()

for f in list(Tandem.filas.values()):
    keys = list(f.status.keys())
    print(f.id, end = '\n')
    for k in keys:
        print(k, f.status[k], round(f.status[k]/Tandem.tempoTotal * 100, 2), end='\n', sep="            ")

