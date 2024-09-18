
import heapq
import random
import time

def nextRandom(a, c, m, x0):
	x = ((a * x0) + c) % m
	return x/m

class Event:
    def __init__(self, time, event_type, customer_id=None):
        self.time = time
        self.event_type = event_type
        self.customer_id = customer_id

    def __lt__(self, other):
        return self.time < other.time

class QueueSimulator:
    def __init__(self):
        self.event_queue = []
        self.current_time = 0
        self.queue = []
        self.next_customer_id = 1

    def schedule_event(self, event_time, event_type, customer_id=None):
        heapq.heappush(self.event_queue, Event(event_time, event_type, customer_id))

    def run(self, simulation_time):
        self.schedule_event(self.current_time + random.expovariate(1.0), 'ARRIVAL')
        
        while self.event_queue and self.current_time < simulation_time:
            event = heapq.heappop(self.event_queue)
            self.current_time = event.time
            
            if event.event_type == 'ARRIVAL':
                self.handle_arrival(event)
            elif event.event_type == 'DEPARTURE':
                self.handle_departure(event)

    def handle_arrival(self, event):
        customer_id = self.next_customer_id
        self.next_customer_id += 1
        self.queue.append(customer_id)
        print(f"Time {self.current_time:.2f}: Customer {customer_id} arrived and joined the queue.")
        
        # Schedule the next customer arrival
        self.schedule_event(self.current_time + random.expovariate(1.0), 'ARRIVAL')

        # Schedule departure if the queue was empty
        if len(self.queue) == 1:
            self.schedule_event(self.current_time + random.expovariate(0.5), 'DEPARTURE', customer_id)

    def handle_departure(self, event):
        if self.queue:
            customer_id = self.queue.pop(0)
            print(f"Time {self.current_time:.2f}: Customer {customer_id} has been served and left the queue.")
        
        # Schedule the next departure if there are still customers in the queue
        if self.queue:
            self.schedule_event(self.current_time + random.expovariate(0.5), 'DEPARTURE', self.queue[0])

if __name__ == "__main__":
    simulator = QueueSimulator()
    simulator.run(100)  # Simulate for 100 time units