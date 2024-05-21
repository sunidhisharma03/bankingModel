import threading
import time
import random
from queue import Queue
import matplotlib.pyplot as plt
# Here we have imported the necessary libraries required for our program.

numTellers = 3
maxQueueSize = 10
quantum_time = 2  # Fixed quantum time (in seconds)

def customer_generator(queue):
    customer_id = 1
    while True:
        if queue.qsize() < maxQueueSize:
            service_time = random.uniform(1, 5)
            print(f"Customer{customer_id} enters the Queue with service time: {service_time:.2f} seconds")
            arrival_time = time.time()  # Record arrival time
            queue.put((f"Customer{customer_id}", arrival_time, service_time))
            customer_id += 1
        time.sleep(random.uniform(0.5, 2)) 

def teller_worker(queue, teller_id, waiting_times, turnaround_times, response_times):
    while True:
        if not queue.empty():
            customer, arrival_time, service_time = queue.get()
            print(f"{customer} is in Teller{teller_id} with service time: {service_time:.2f} seconds")
            
            # Process customer in round-robin manner with fixed quantum time
            start_time = time.time()
            while service_time > 0:
                time.sleep(min(quantum_time, service_time))
                service_time -= quantum_time
                service_time = max(service_time, 0)  # Ensure service time is non-negative
                print(f"{customer} remaining service time: {service_time:.2f} seconds")
                # Check if the customer has been interrupted by another customer
                if not queue.empty() and time.time() - start_time >= quantum_time:
                    queue.put((customer, arrival_time, service_time))  # Put the customer back in the queue
                    print(f"{customer} interrupted in Teller{teller_id}")
                    start_time = time.time()  # Reset the start time
                    break
            else:
                print(f"{customer} leaves the Teller{teller_id}")
                
                response_time = start_time - arrival_time  # Calculate response time
                response_times.append(response_time)
                
                waiting_time = start_time - arrival_time - (len(response_times) - 1) * quantum_time
                waiting_times.append(waiting_time if waiting_time >= 0 else 0)  # Ensure waiting time is non-negative
                
                turnaround_time = start_time - arrival_time  # Calculate turnaround time
                turnaround_times.append(turnaround_time)

def main():
    queue = Queue(maxsize=maxQueueSize)
    waiting_times = []
    turnaround_times = []
    response_times = []
    
    threading.Thread(target=customer_generator, args=(queue,), daemon=True).start()
    
    for teller_id in range(1, numTellers + 1):
        threading.Thread(target=teller_worker, args=(queue, teller_id, waiting_times, turnaround_times, response_times), daemon=True).start()
    
    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        avg_waiting_time = sum(waiting_times) / len(waiting_times) if waiting_times else 0
        avg_turnaround_time = sum(turnaround_times) / len(turnaround_times) if turnaround_times else 0
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
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
        plt.title('Average Times for Round-Robin Scheduling')
        plt.show()

if __name__ == "__main__":
    main()
