import threading
import time
import random
from queue import Queue
import matplotlib.pyplot as plt

numTellers = 3
maxQueueSize = 10

service_completion_times = [0] * numTellers
stop_simulation = threading.Event()

def customer_generator(queue, num_customers):
    for customer_id in range(1, num_customers + 1):
        while not stop_simulation.is_set():
            if queue.qsize() < maxQueueSize:
                service_time = random.uniform(1, 5)  # Generate service time between 1 and 5 seconds
                print(f"Customer{customer_id} enters the Queue with service time: {service_time:.2f} seconds")
                arrival_time = time.time()  # Record arrival time
                queue.put((f"Customer{customer_id}", arrival_time, service_time))
                time.sleep(random.uniform(0.5, 2))  # Random arrival time between 0.5 and 2 seconds
                break
            else:
                print("Queue is FULL.")
                time.sleep(1)

def teller_worker(queue, teller_id, waiting_times, turnaround_times, response_times):
    current_customer = None
    while not stop_simulation.is_set():
        if not queue.empty():
            customer, arrival_time, service_time = queue.get()
            if current_customer is None or service_time < current_customer[2]:
                if current_customer:
                    queue.put(current_customer)  # Put back the currently serviced customer with remaining service time
                current_customer = (customer, arrival_time, service_time)
                start_service_time = time.time()  # Start service time

                waiting_time = start_service_time - arrival_time  # Calculate waiting time
                print(f"{customer} is in Teller{teller_id} with service time: {service_time:.2f} seconds")
                print(f"Have waited for: {waiting_time:.2f} seconds")

                service_completion_times[teller_id - 1] = start_service_time + service_time

                time.sleep(service_time)

                end_time = time.time()  # Customer leaves
                print(f"{customer} leaves the Teller{teller_id}")

                turnaround_time = end_time - arrival_time  # Calculate turnaround time
                response_time = start_service_time - arrival_time  # Calculate response time

                waiting_times.append(waiting_time)
                turnaround_times.append(turnaround_time)
                response_times.append(response_time)

                current_customer = None
            else:
                queue.put((customer, arrival_time, service_time))  # Put back the customer into the queue
                time.sleep(0.1)  # Wait if the queue is empty
        else:
            time.sleep(0.1)  # Wait if the queue is empty

def main():
    global stop_simulation
    queue = Queue(maxsize=maxQueueSize)
    waiting_times = []
    turnaround_times = []
    response_times = []

    num_customers = 10  # Number of customers to be generated
    customer_thread = threading.Thread(target=customer_generator, args=(queue, num_customers), daemon=True)
    customer_thread.start()

    teller_threads = []
    for teller_id in range(1, numTellers + 1):
        thread = threading.Thread(target=teller_worker, args=(queue, teller_id, waiting_times, turnaround_times, response_times), daemon=True)
        thread.start()
        teller_threads.append(thread)

    try:
        while not queue.empty() or threading.active_count() > 1:
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
            plt.title('Average Times for SRTF Scheduling')
            plt.show()
        else:
            print("No customers were processed.")

if __name__ == "__main__":
    main()
