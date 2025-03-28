import argparse
import time
import csv
import os
from datetime import datetime

# generate_unique_filename function
def generate_unique_filename(base_name):
    counter = 1
    unique_filename = base_name
    while os.path.exists(unique_filename):
        unique_filename = base_name.replace(".csv", f"({counter}).csv")
        counter += 1
    return unique_filename

def run_benchmark(data_set, query, heterogeneity, topology, nodes):
    print("Starting Experiment...")
    print("Running Benchmark with the following parameters:")
    print(f"Data Set: {data_set}")
    print(f"Query: {query}")
    print(f"Hardware Heterogeneity: {heterogeneity}")
    print(f"Network Topology: {topology}")
    print(f"Number of Nodes: {nodes}")

    # Simulate experiment execution
    time.sleep(3)
    print("Experiment Completed! Results will be saved to a CSV file.")

    # save the data to a new CSV file with a unique filename
    timestamp = datetime.now().strftime("%d-%m-%y_%H_%M")
    base_filename = f"results/experiment_results_{timestamp}.csv"
    unique_filename = generate_unique_filename(base_filename)   
    
    with open(unique_filename, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["A", "B"])
        writer.writerow([12, 14])
        writer.writerow([13, 16])
        writer.writerow([14, 18])


    print(f"Experiment results appended to {unique_filename}")
    print("-" * 50)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Benchmark Script")
    parser.add_argument("--dataset", required=True, help="Specify the dataset to use")
    parser.add_argument("--query", required=True, help="Specify the query to run")
    parser.add_argument("--heterogeneity", required=True, help="Specify the hardware heterogeneity")
    parser.add_argument("--topology", required=True, help="Specify the network topology")
    parser.add_argument("--nodes", required=True, type=int, help="Specify the number of nodes")

    args = parser.parse_args()

    run_benchmark(args.dataset, args.query, args.heterogeneity, args.topology, args.nodes)
