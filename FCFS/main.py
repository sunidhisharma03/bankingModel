import threading
import time
import random
from queue import Queue
import matplotlib.pyplot as plt

numTellers = 3
maxQueueSize = 10

service_completion_times = [0] * numTellers
stop_simulation = threading.Event()

def customer_generator(queue):
    customer_id = 1
    while not stop_simulation.is_set():
        if queue.qsize() < maxQueueSize:
            print(f"Customer{customer_id} enters the Queue")
            arrival_time = time.time()  # Record arrival time
            queue.put((f"Customer{customer_id}", arrival_time))
            customer_id += 1
        else:
            print("Queue is FULL. Pausing for 5 seconds...")
            time.sleep(5)
            # Remove customers from the front of the queue to simulate them leaving
            for _ in range(min(3, queue.qsize())):
                queue.get()
                print("Customer left the queue due to full capacity")
                queue.task_done()
        time.sleep(random.uniform(0.5, 2))  # Random arrival time between 0.5 and 2 seconds

def teller_worker(queue, teller_id, waiting_times, turnaround_times, response_times):
    while not stop_simulation.is_set():
        if not queue.empty():
            customer, arrival_time = queue.get()
            start_service_time = time.time()  # Start service time

            waiting_time = start_service_time - arrival_time  # Calculate waiting time
            service_time = random.uniform(1, 5)  # Service time between 1 and 5 seconds

            print(f"{customer} is in Teller{teller_id} with Waiting Time: {waiting_time:.2f} seconds and Service Time: {service_time:.2f} seconds")
            
            service_completion_times[teller_id - 1] = start_service_time + service_time

            time.sleep(service_time)
            
            end_time = time.time()  # Customer leaves
            print(f"{customer} leaves the Teller{teller_id}")
            
            turnaround_time = end_time - arrival_time  # Calculate turnaround time
            response_time = start_service_time - arrival_time  # Calculate response time
            
            waiting_times.append(waiting_time)
            turnaround_times.append(turnaround_time)
            response_times.append(response_time)
            
            queue.task_done()

def main():
    global stop_simulation
    queue = Queue(maxsize=maxQueueSize)
    waiting_times = []
    turnaround_times = []
    response_times = []

    customer_thread = threading.Thread(target=customer_generator, args=(queue,), daemon=True)
    customer_thread.start()
    
    teller_threads = []
    for teller_id in range(1, numTellers + 1):
        thread = threading.Thread(target=teller_worker, args=(queue, teller_id, waiting_times, turnaround_times, response_times), daemon=True)
        thread.start()
        teller_threads.append(thread)

    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nSimulation interrupted. Calculating results...")
        stop_simulation.set()

        # Wait for threads to finish processing
        customer_thread.join()
        for thread in teller_threads:
            thread.join()

        if waiting_times and turnaround_times and response_times:
            avg_waiting_time = sum(waiting_times) / len(waiting_times)
            avg_turnaround_time = sum(turnaround_times) / len(turnaround_times)
            avg_response_time = sum(response_times) / len(response_times)
            
            print("Simulation ended.")
            print(f"Average Waiting Time: {avg_waiting_time:.2f} seconds")
            print(f"Average Turnaround Time: {avg_turnaround_time:.2f} seconds")
            print(f"Average Response Time: {avg_response_time:.2f} seconds")

            # Plotting the graph
            metrics = ['Avg Waiting Time', 'Avg Turnaround Time', 'Avg Response Time']
            values = [avg_waiting_time, avg_turnaround_time, avg_response_time]

            plt.figure(figsize=(10, 5))
            plt.bar(metrics, values, color=['blue', 'green', 'red'])
            plt.xlabel('Metrics')
            plt.ylabel('Time (seconds)')
            plt.title('Average Times for FCFS Scheduling')
            plt.show()
        else:
            print("No customers were processed.")

if __name__ == "__main__":
    main()
