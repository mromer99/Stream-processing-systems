# Benchmarking Tool Dashboard

This project is an interactive benchmarking tool built with [Dash](https://dash.plotly.com/) and [Dash Bootstrap Components](https://dash-bootstrap-components.opensource.faculty.ai/) for running experiments, visualizing results, and managing network topology configurations. It provides two main panels: an **Experiment Panel** for setting up and starting benchmarks, and a **Results Panel** for uploading CSV files and viewing plotted data.

## Features

- **Interactive Web Interface:**  
  A responsive dashboard with a sidebar for navigating between experiment configuration and results visualization.

- **Experiment Configuration:**  
  Configure experiments by specifying the data set, query, hardware heterogeneity, network topology, and number of nodes.

- **Benchmark Execution:**  
  Simulated benchmark execution via a separate command-line script that generates CSV results.

- **Results Visualization:**  
  Upload CSV files and visualize data with multiple plot styles (default line plot, box plot, bar chart).

- **Network Topology Display:**  
  Visual representation of a binary tree network topology with lazy node expansion and tooltips for node/edge information.

- **Configuration Management:**  
  Save and load experiment configurations using YAML files.

## Project Structure

- **app.py:**  
  The main entry point of the application. Initializes the Dash app, sets up the sidebar navigation, and registers callbacks for the Experiment and Results panels.

- **runBenchmark.py:**  
  A command-line script to simulate benchmark experiments. It accepts parameters for the dataset, query, hardware heterogeneity, network topology, and number of nodes. Results are saved to a uniquely named CSV file in the `results/` directory.

- **components/experiment_panel.py:**  
  Contains the layout and callback functions for the Experiment Panel. This panel allows users to configure and start experiments, view terminal logs, and interact with a network topology visualization using Dash Cytoscape.

- **components/results_panel.py:**  
  Contains the layout and callback functions for the Results Panel. Users can upload CSV files, and the app generates plots with various styles.

- **utils/file_operations.py:**  
  (Not shown here) Contains helper functions for saving and loading configurations (e.g., saving to or reading from YAML files).

## Requirements

- Python 3.7 or above
- [Dash](https://pypi.org/project/dash/)
- [Dash Bootstrap Components](https://pypi.org/project/dash-bootstrap-components/)
- [Dash Cytoscape](https://pypi.org/project/dash-cytoscape/)
- [Pandas](https://pypi.org/project/pandas/)
- [Matplotlib](https://pypi.org/project/matplotlib/)
- [PyYAML](https://pypi.org/project/pyyaml/)

You can install the required packages using pip:

```bash
pip install dash dash-bootstrap-components dash-cytoscape pandas matplotlib pyyaml
```

## Setup & Usage

1. **Clone the repository:**

 ```bash
 git clone <repository_url>
 cd <repository_directory>
  ```
2. **Install dependencies:**

 ```bash
pip install -r requirements.txt
  ```
3. **Run the Dashboard Application::**

 ```bash
python app.py
```
4. **Running Benchmarks from the Command Line:**

 ```bash
python runBenchmark.py --dataset <dataset_name> --query <query_string> --heterogeneity <homogeneous|heterogeneous> --topology <star|mesh|tree> --nodes <number_of_nodes>
  ```

## Contributing
Contributions are welcome! Feel free to open issues or submit pull requests for improvements and bug fixes.

## License

This project is licensed under the MIT License.

