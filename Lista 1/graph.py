import csv
import heapq
import time
from datetime import datetime, timedelta
import random


class Graph:
    graph = {}
    coords = {}
   
    def __init__(self, data):
        self.add_nodes(data)
        self.add_edges(data)
        self.sort_graph()
        self.add_coords(data)

    def add_nodes(self, data):
        for row in data:
            if row[5] not in self.graph:
                self.graph[row[5]] = {}
            if row[6] not in self.graph:
                self.graph[row[6]] = {}

    def add_edges(self, data):
         for row in data:          
            if row[6] in self.graph[row[5]]:
                self.graph[row[5]][row[6]].append((change_hour(row[3]), change_hour(row[4]), row[2])) 
            else:
                self.graph[row[5]][row[6]] = [(change_hour(row[3]), change_hour(row[4]), row[2])]

    def get_graph(self):
        return self.graph
    
    def add_coords(self, data):
        for row in data:
            if row[5] not in self.coords:
                self.coords[row[5]] = (row[7], row[8])
            if row[6] not in self.coords:
                self.coords[row[6]] = (row[9], row[10])

    def get_coords(self):
        return self.coords
    
    def sort_graph(self):
        for key, value in self.graph.items(): 
            for key_value, value_value in value.items():
                self.graph[key][key_value] = sorted(value_value, key=lambda d: d[0])

    def get_heuristic(self, start_stop, end_stop):
        ax = float(self.coords[start_stop][0])
        ay = float(self.coords[start_stop][1])
        bx = float(self.coords[end_stop][0])
        by = float(self.coords[end_stop][1])

        h = abs(ax - bx) + abs(ay - by)  
        return h 
    
    def get_heuristic2(self, curr_line, end_stop):
        end_lines = set()

        for list in self.graph[end_stop].values():
            for conn in list:
                end_lines.add(conn[2])

        return 0 if curr_line in end_lines else 5
        
                
def read_file():
    # wczytanie danych z pliku CSV
    with open('C:/Users/karol/python/connection_graph.csv', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # pomijamy pierwszy wiersz z nagłówkami kolumn
        return [row for row in reader]
    
def measure_time(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"Czas wykonania {func.__name__}: {end - start} sekund")
        return result
    return wrapper

def change_hour(time):
    t = time.split(":")
    t[0] = str(int(t[0]) % 24)
    if len(t[0]) == 1:
        t[0] = "0" + t[0]
    return ":".join(t)

@measure_time
def dijkstra(g, start, end, time):
    graph = g.get_graph() 

    distances = {stop: 9999999 for stop in graph.keys()}
    distances[start] = 0
    visited = 0
    found = False
    
    header = [f"{'Nazwa przystanku':<30}", f"{'Odjazd':<10}", f"{'Przyjazd':<10}", f"{'Linia':<5}"]
     
    # (dystans, nazwa przystanku, trasa, czas odjazdu, czas przyjazdu, linia)
    unvisited = [(0, start, [header], "00:00:00", time.strftime('%H:%M:%S'), 0)]
    heapq.heapify(unvisited)

    while unvisited:
        (distance, current_stop, path, departure_time, current_arrival, current_line) = heapq.heappop(unvisited)
        
        #departure_time - czas odjazdu z poprzedniego przystanku
        #current_arrival - czas przyjazdu na obecny przystanek
        path.append([f"{current_stop:<40}", f"{departure_time:<10}", f"{current_arrival:<10}", f"{current_line:<5}", distance / 60])
        visited += 1
        
        if current_stop == end:
            print("Odwiedzone węzły:", visited)
            return (distances[end] / 60, path)

        for neigbor_name, neighbor_list in graph[current_stop].items():
            found = False     
          
            for n in neighbor_list:            
                
                if n[0] >= current_arrival:
                    neighbor_departure = n[0]
                    neighbor_arrival = n[1]
                   
                    neighbor_distance = (datetime.strptime(neighbor_arrival, '%H:%M:%S') - datetime.strptime(current_arrival, '%H:%M:%S')).seconds
                    new_distance = distances[current_stop] + neighbor_distance 
                    
                    if new_distance < distances[neigbor_name]:
                        distances[neigbor_name] = new_distance
                        heapq.heappush(unvisited, (distances[neigbor_name], neigbor_name, path.copy(), neighbor_departure, neighbor_arrival, n[2]))
                    
                    found = True
                    break
            
            if not found:
                n = neighbor_list[0]
                neighbor_departure = n[0]
                neighbor_arrival = n[1]
                   
                neighbor_distance = (datetime.strptime(neighbor_arrival, '%H:%M:%S') - datetime.strptime(current_arrival, '%H:%M:%S')).seconds
                new_distance = distances[current_stop] + neighbor_distance 
                    
                if new_distance < distances[neigbor_name]:
                    distances[neigbor_name] = new_distance
                    heapq.heappush(unvisited, (distances[neigbor_name], neigbor_name, path.copy(), neighbor_departure, neighbor_arrival, n[2]))
                    
             

    return (None, path)

@measure_time
def a_star(g, start, end, time, p):
    graph = g.get_graph()

    
    distances = {stop: 99999 for stop in graph.keys()}
    distances[start] = 0
    
    visited = 0

    fcost = {stop: 999999 for stop in graph.keys()}
    fcost[start] = 0
    
    header = [f"{'Nazwa przystanku':<40}", f"{'Odjazd':<10}", f"{'Przyjazd':<10}", f"{'Linia':<5}"]

    closed_list = []
            
    # (dystans, nazwa przystanku, trasa, czas odjazdu, czas przyjazdu, linia)
    unvisited = [(fcost[start], start, [header], "00:00:00", time.strftime('%H:%M:%S'), 0)]
    heapq.heapify(unvisited)

    while unvisited:
        (f, current_stop, path, departure_time, current_arrival, current_line) = heapq.heappop(unvisited)
        
        #departure_time - czas odjazdu z poprzedniego przystanku
        #current_arrival - czas przyjazdu na obecny przystanek
        path.append([f"{current_stop:<40}", f"{departure_time:<10}", f"{current_arrival:<10}", f"{current_line:<5}", f])
        visited += 1
        
        if current_stop == end:
            print("Odwiedzone węzły:", visited)
            return (distances[end] / 60, path)
        
        closed_list.append(current_stop)
        
        for neigbor_name, neighbor_list in graph[current_stop].items():
            found = False
            if neigbor_name in closed_list:
                    continue
            for n in neighbor_list:
        
                if n[0] >= current_arrival:
                    if p:
                        neighbor_distance = 0 if n[2] == current_line and current_arrival == n[0] else 1 + g.get_heuristic2(n[2], end)
                        new_distance = distances[current_stop] + neighbor_distance 

                        if new_distance < distances[neigbor_name]:
                            distances[neigbor_name] = new_distance
                            fcost[neigbor_name] = new_distance + g.get_heuristic(neigbor_name, end) * 10
                            heapq.heappush(unvisited, (fcost[neigbor_name], neigbor_name, path.copy(), n[0], n[1], n[2]))

                        found = True
                    else:
                        neighbor_distance = (datetime.strptime(n[1], '%H:%M:%S') - datetime.strptime(current_arrival, '%H:%M:%S')).seconds
                        new_distance = distances[current_stop] + neighbor_distance
                       
                        if new_distance < distances[neigbor_name]:
                            distances[neigbor_name] = new_distance
                            fcost[neigbor_name] = new_distance + g.get_heuristic(neigbor_name, end) * 10000
                            heapq.heappush(unvisited, (fcost[neigbor_name], neigbor_name, path.copy(), n[0], n[1], n[2]))
                        found = True
                        break

            if not found:
                n = neighbor_list[0]
                if p:
                    neighbor_distance = 0 if n[2] == current_line and current_arrival == n[0] else 1 + g.get_heuristic2(n[2], end)
                    new_distance = fcost[current_stop] + neighbor_distance 

                    if new_distance < fcost[neigbor_name]:
                        fcost[neigbor_name] = new_distance 
                        heapq.heappush(unvisited, (fcost[neigbor_name], neigbor_name, path.copy(), n[0], n[1], n[2]))
                else:
                    neighbor_distance = (datetime.strptime(n[1], '%H:%M:%S') - datetime.strptime(current_arrival, '%H:%M:%S')).seconds
                    new_distance = distances[current_stop] + neighbor_distance
                       
                    if new_distance < distances[neigbor_name]:
                        distances[neigbor_name] = new_distance
                        fcost[neigbor_name] = new_distance + g.get_heuristic(neigbor_name, end) * 10000
                        heapq.heappush(unvisited, (fcost[neigbor_name], neigbor_name, path.copy(), n[0], n[1], n[2]))
                    found = True
                    
    return (None, path)


def tests(n):
    data = read_file()
    graph = Graph(data)
    
    dlist = []
    aplist = []
    atlist = []
 
    for i in range(0,n):
        start = random.choice(list(graph.get_graph().keys()))
        end = random.choice(list(graph.get_graph().keys()))
        while end == start:
            end = random.choice(list(graph.get_graph().keys()))

        s_time = str(random.randint(0, 23)) + ":" + str(random.randint(0, 59)) + ":" + str(random.randint(0, 59))

        start_time = time.time()
        sek, path = dijkstra(graph, start, end, datetime.strptime(s_time, '%H:%M:%S'))
        end_time = time.time()
        dlist.append(end_time - start_time)

        if path != None:
            for i in path:
                print(i)
            print("czas:", sek)

        start_time = time.time()
        time2, path2 = a_star(graph, start, end, datetime.strptime(s_time, '%H:%M:%S'), True)
        end_time = time.time()
        atlist.append(end_time - start_time)

        if path2 != None:
            for i in path2:
                print(i)
            print("czas:", time2)

        # start_time = time.time()
        # time3, path3 = a_star(graph, "Kozia", "Rysia", datetime.strptime("23:50:00", '%H:%M:%S'), True)
        # end_time = time.time()
        # aplist.append(end_time - start_time)

        # if path3 != None:
        #     for i in path3:
        #         print(i)
        #     print("czas:", time3)

    return dlist, atlist, aplist
def main():
    # dlist, atlist, aplist = tests(20)
    # print(sum(dlist) / len(dlist))
    # print(sum(atlist) / len(atlist))
    #print(sum(aplist) / len(aplist))

    
    data = read_file()
    graph = Graph(data)

    sek, path = a_star(graph, "Brodzka", "Psie Pole", datetime.strptime("15:30:00", '%H:%M:%S'), True)
   
    if path != None:
        for i in path:
            print(i)
        print("czas:", sek)    

    
if __name__ == "__main__":
    main()