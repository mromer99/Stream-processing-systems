from dash import html, dcc, Input, Output, State, callback_context
import dash
import dash_bootstrap_components as dbc
import dash_cytoscape as cyto
from utils.file_operations import save_to_yaml, load_yaml_from_content
import subprocess, threading, time

# Global variables for terminal logging (unchanged)
import threading
terminal_lock = threading.Lock()
terminal_logs = ""  # Accumulates log messages

def count_descendants(i, num):
    """
    Recursively count the number of descendant nodes for node i in a binary tree
    represented as an array of length num.
    """
    count = 0
    left = 2 * i + 1
    right = 2 * i + 2
    if left < num:
        count += 1 + count_descendants(left, num)
    if right < num:
        count += 1 + count_descendants(right, num)
    return count

# Helper function to build tree elements with lazy expansion and child count
def build_tree_elements(num, expanded):
    """
    Recursively builds the Cytoscape elements for a binary tree.
    Only nodes that are in the expanded list will have their children shown.
    If a node has children but is not expanded, a "[+<child_count>]" indicator is appended.
    """
    elements = []

    def add_node(i):
        if i >= num:
            return
        left = 2 * i + 1
        right = 2 * i + 2
        has_children = left < num  # if there is at least a left child, assume children exist
        if has_children and i not in expanded:
            descendant_count = count_descendants(i, num)
            label = f"Node {i} [+{descendant_count}]"
        else:
            label = f"Node {i}"
        # Add static CPU and Memory info to the node
        elements.append({'data': {'id': str(i), 'label': label, 'cpu': "2.5 GHz", 'memory': "8GB"}})
        # If the node is expanded, add its children and connecting edges with bandwidth info
        if i in expanded:
            if left < num:
                add_node(left)
                elements.append({'data': {'source': str(i), 'target': str(left), 'bandwidth': 100}})
            if right < num:
                add_node(right)
                elements.append({'data': {'source': str(i), 'target': str(right), 'bandwidth': 100}})
    add_node(0)
    return elements

# Experiment Panel Layout (includes terminal and network topology)
experiment_panel = dbc.Card(
    dbc.CardBody(
        [
            html.H5("Experiment Configuration", className="card-title"),
            dbc.InputGroup(
                [dbc.InputGroupText("Data Set"),
                 dbc.Input(id="data-set", placeholder="Enter data set", type="text")],
                className="mb-3",
            ),
            dbc.InputGroup(
                [dbc.InputGroupText("Query"),
                 dbc.Input(id="query", placeholder="Enter query", type="text")],
                className="mb-3",
            ),
            dbc.InputGroup(
                [dbc.InputGroupText("Hardware Heterogeneity"),
                 dcc.Dropdown(
                     id="hardware-heterogeneity",
                     options=[
                         {"label": "Homogeneous", "value": "homogeneous"},
                         {"label": "Heterogeneous", "value": "heterogeneous"},
                     ],
                     placeholder="Select hardware heterogeneity",
                     style={"width": "300px"},
                 )],
                className="mb-3",
            ),
            dbc.InputGroup(
                [dbc.InputGroupText("Network Topology"),
                 dcc.Dropdown(
                     id="network-topology",
                     options=[
                         {"label": "Star Topology", "value": "star"},
                         {"label": "Mesh Topology", "value": "mesh"},
                         {"label": "Tree Topology", "value": "tree"},
                     ],
                     placeholder="Select network topology",
                     style={"width": "300px"},
                 )],
                className="mb-3",
            ),
            dbc.InputGroup(
                [dbc.InputGroupText("Number of Nodes"),
                 dbc.Input(id="num-of-nodes", placeholder="Enter number of nodes", type="number")],
                className="mb-3",
            ),
            html.Div(
                [
                    dbc.Button("Save Configuration", id="save-btn", color="success", className="me-2"),
                    dcc.Upload(
                        id="upload-config",
                        children=dbc.Button("Load Configuration", color="secondary", className="me-2"),
                        accept=".yaml",
                    ),
                    dbc.Button("Start Experiment", id="start-btn", color="danger"),
                ],
                className="d-flex justify-content-between",
            ),
            html.Hr(),
            # Terminal Output Section with Expand/Collapse Button
            html.Div([
                html.H5("Terminal Output", className="card-title", style={"display": "inline-block"}),
                dbc.Button("Expand/Collapse", id="toggle-terminal-btn", color="primary", size="sm", style={"marginLeft": "10px"})
            ]),
            dbc.Collapse(
                dbc.Card(
                    dbc.CardBody(
                        [
                            html.Div(
                                id="terminal-output",
                                style={
                                    "backgroundColor": "#1e1e1e",
                                    "color": "#d4d4d4",
                                    "height": "400px",
                                    "overflowY": "scroll",
                                    "padding": "10px",
                                    "fontFamily": "monospace",
                                    "whiteSpace": "pre-wrap",
                                    "borderRadius": "5px",
                                },
                            )
                        ]
                    ),
                    style={"height": "420px"},
                ),
                id="terminal-collapse",
                is_open=True  # Initially expanded
            ),
            # Interval to trigger terminal update every second
            dcc.Interval(id="terminal-interval", interval=1000, n_intervals=0),
            html.Hr(),
            # Network Topology Section with Expand/Collapse Button and interactive tooltip
            html.Div([
                html.H5("Network Topology", className="card-title", style={"display": "inline-block"}),
                dbc.Button("Expand/Collapse", id="toggle-network-btn", color="primary", size="sm", style={"marginLeft": "10px"})
            ]),
            dbc.Collapse(
                dbc.Card(
                    dbc.CardBody(
                        [
                        # Wrap Cytoscape and tooltip in a relative container
                        html.Div(
                            [
                                cyto.Cytoscape(
                                    id='network-topology-graph',
                                    layout={'name': 'breadthfirst', 'directed': True, 'padding': 10},
                                    style={'width': '100%', 'height': '400px'},
                                    elements=[],
                                ),
                                # Tooltip Div for nodes and edges; initially hidden
                                html.Div(
                                    id="cyto-tooltip",
                                    style={
                                        "position": "absolute",
                                        "display": "none",
                                        "backgroundColor": "white",
                                        "padding": "5px",
                                        "border": "1px solid #ccc",
                                        "borderRadius": "3px",
                                        "zIndex": 1000,
                                        "fontSize": "12px"
                                    }
                                )
                            ],
                            style={"position": "relative", "width": "100%", "height": "400px"}
                        )
                        ])
                ),
                id="network-collapse",
                is_open=True
            ),
            # Hidden store to track expanded nodes in the network view
            dcc.Store(id="expanded-nodes", data=[]),
        ]
    ),
    style={"padding": "20px", "box-shadow": "0px 4px 8px rgba(0, 0, 0, 0.1)"},
)

def run_benchmark(params):
    """Runs runBenchmark.py with unbuffered output and appends output to terminal_logs."""
    global terminal_logs
    try:
        msg = "Starting experiment...\n"
        with terminal_lock:
            terminal_logs += msg
        print(msg, end="")  # Local terminal output
        process = subprocess.Popen(
            [
                "python", "-u", "runBenchmark.py",
                "--dataset", params['data_set'],
                "--query", params['query'],
                "--heterogeneity", params['hardware_heterogeneity'],
                "--topology", params['network_topology'],
                "--nodes", str(params['num_of_nodes'])
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        for stdout_line in iter(process.stdout.readline, ""):
            with terminal_lock:
                terminal_logs += stdout_line
            print(stdout_line, end="")
        process.stdout.close()
        stderr = process.stderr.read()
        if stderr:
            with terminal_lock:
                terminal_logs += stderr
            print(stderr, end="")
        process.stderr.close()
        return_code = process.wait()
        if return_code == 0:
            msg = "Experiment completed successfully.\n"
        else:
            msg = f"Experiment failed with return code {return_code}.\n"
        with terminal_lock:
            terminal_logs += msg
        print(msg, end="")
    except Exception as e:
        msg = f"Error running experiment: {e}\n"
        with terminal_lock:
            terminal_logs += msg
        print(msg, end="")

def register_callbacks(app):
    # Callback to save configuration (unchanged)
    @app.callback(
        Output("save-btn", "n_clicks"),
        [Input("save-btn", "n_clicks")],
        [State("data-set", "value"),
         State("query", "value"),
         State("hardware-heterogeneity", "value"),
         State("network-topology", "value"),
         State("num-of-nodes", "value")]
    )
    def save_configuration(n_clicks, data_set, query, hardware_heterogeneity, network_topology, num_of_nodes):
        global terminal_logs
        if n_clicks:
            config = {
                "Data Set": data_set,
                "Query": query,
                "Hardware Heterogeneity": hardware_heterogeneity,
                "Network Topology": network_topology,
                "Number of Nodes": num_of_nodes,
            }
            try:
                filename = save_to_yaml(config)
                msg = f"Configuration saved to {filename}\n"
            except Exception as e:
                msg = f"Error saving configuration: {e}\n"
            with terminal_lock:
                terminal_logs += msg
            print(msg, end="")
            return 0  # Reset n_clicks
        return dash.no_update

    # Callback to load configuration (unchanged)
    @app.callback(
        [Output("data-set", "value"),
         Output("query", "value"),
         Output("hardware-heterogeneity", "value"),
         Output("network-topology", "value"),
         Output("num-of-nodes", "value")],
        [Input("upload-config", "contents")]
    )
    def load_configuration(contents):
        global terminal_logs
        if contents:
            try:
                config = load_yaml_from_content(contents)
                msg = "Configuration loaded successfully.\n"
                with terminal_lock:
                    terminal_logs += msg
                print(msg, end="")
                return (
                    config.get("Data Set", ""),
                    config.get("Query", ""),
                    config.get("Hardware Heterogeneity", ""),
                    config.get("Network Topology", ""),
                    config.get("Number of Nodes", None)
                )
            except Exception as e:
                msg = f"Error loading configuration: {e}\n"
                with terminal_lock:
                    terminal_logs += msg
                print(msg, end="")
        return "", "", "", "", None

    # Callback to start experiment (unchanged except for terminal logging)
    @app.callback(
        Output("start-btn", "n_clicks"),
        [Input("start-btn", "n_clicks")],
        [State("data-set", "value"),
         State("query", "value"),
         State("hardware-heterogeneity", "value"),
         State("network-topology", "value"),
         State("num-of-nodes", "value")]
    )
    def start_experiment(n_clicks, data_set, query, hardware_heterogeneity, network_topology, num_of_nodes):
        global terminal_logs
        if n_clicks:
            if not all([data_set, query, hardware_heterogeneity, network_topology, num_of_nodes]):
                msg = "All fields are required to start an experiment.\n"
                with terminal_lock:
                    terminal_logs += msg
                print(msg, end="")
                return 0
            params = {
                "data_set": data_set,
                "query": query,
                "hardware_heterogeneity": hardware_heterogeneity,
                "network_topology": network_topology,
                "num_of_nodes": num_of_nodes,
            }
            with terminal_lock:
                terminal_logs += "--------------------------------------------------\n"
            threading.Thread(target=run_benchmark, args=(params,)).start()
        return 0

    # Callback to update the terminal output periodically
    @app.callback(
        Output("terminal-output", "children"),
        [Input("terminal-interval", "n_intervals")]
    )
    def update_terminal(n):
        global terminal_logs
        with terminal_lock:
            current_logs = terminal_logs
        return current_logs

    # Callback to update the network topology graph elements using lazy expansion
    @app.callback(
        Output("network-topology-graph", "elements"),
        [Input("num-of-nodes", "value"),
         Input("network-topology", "value"),
         Input("expanded-nodes", "data")]
    )
    def update_network_topology(num_nodes, topology_type, expanded):
        try:
            num = int(num_nodes) if num_nodes is not None else 3
        except:
            num = 3
        # For 3 or fewer nodes, build elements without lazy expansion but add extra info
        if num <= 3:
            elements = []
            for i in range(num):
                elements.append({'data': {'id': str(i), 'label': f'Node {i}', 'cpu': "2.5 GHz", 'memory': "8GB"}})
            for i in range(num):
                left = 2 * i + 1
                right = 2 * i + 2
                if left < num:
                    elements.append({'data': {'source': str(i), 'target': str(left), 'bandwidth': 100}})
                if right < num:
                    elements.append({'data': {'source': str(i), 'target': str(right), 'bandwidth': 100}})
            return elements
        # For more than 3 nodes, use lazy expansion.
        if expanded is None:
            expanded = []
        return build_tree_elements(num, expanded)

        # Callback to update (or toggle) the expanded-nodes store when a node is clicked.
    @app.callback(
        Output("expanded-nodes", "data"),
        [Input("network-topology-graph", "tapNodeData")],
        [State("expanded-nodes", "data"),
         State("num-of-nodes", "value")]
    )
    def expand_node(tapData, expanded_data, num_nodes):
        if not tapData:
            raise dash.exceptions.PreventUpdate
        try:
            num = int(num_nodes) if num_nodes is not None else 3
        except:
            num = 3
        node_id = int(tapData["id"])
        # Check if the tapped node has any children in the full binary tree
        if 2 * node_id + 1 >= num:
            # No children exist
            raise dash.exceptions.PreventUpdate
        if expanded_data is None:
            expanded_data = []
        # If the node is not already expanded, add it.
        if node_id not in expanded_data:
            expanded_data.append(node_id)
        return expanded_data


    # --- New callbacks for toggling the collapsible sections ---

    @app.callback(
        Output("terminal-collapse", "is_open"),
        [Input("toggle-terminal-btn", "n_clicks")],
        [State("terminal-collapse", "is_open")]
    )
    def toggle_terminal(n_clicks, is_open):
        if n_clicks:
            return not is_open
        return is_open

    @app.callback(
        Output("network-collapse", "is_open"),
        [Input("toggle-network-btn", "n_clicks")],
        [State("network-collapse", "is_open")]
    )
    def toggle_network(n_clicks, is_open):
        if n_clicks:
            return not is_open
        return is_open
    
    # --- New callback for displaying tooltip on hover over nodes or edges ---
    @app.callback(
        [Output("cyto-tooltip", "children"),
         Output("cyto-tooltip", "style")],
        [Input("network-topology-graph", "mouseoverNodeData"),
         Input("network-topology-graph", "mouseoverEdgeData"),
         Input("network-topology-graph", "mouseoutNodeData"),
         Input("network-topology-graph", "mouseoutEdgeData")]
    )
    def update_tooltip(mouseoverNode, mouseoverEdge, mouseoutNode, mouseoutEdge):
        ctx_trigger = callback_context.triggered
        # Hide tooltip on mouseout events
        if ctx_trigger and any("mouseout" in t["prop_id"] for t in ctx_trigger):
            return "", {"position": "absolute", "display": "none", "backgroundColor": "white",
                        "padding": "5px", "border": "1px solid #ccc", "borderRadius": "3px", "zIndex": 1000, "fontSize": "12px"}
        if ctx_trigger:
            prop_id = ctx_trigger[0]["prop_id"]
            # When hovering over a node, display CPU and Memory info.
            if "mouseoverNodeData" in prop_id and mouseoverNode:
                cpu = mouseoverNode.get("cpu", "N/A")
                memory = mouseoverNode.get("memory", "N/A")
                tooltip_text = f"CPU: {cpu}, Memory: {memory}"
                # Position next to mouse cursor.                 
                style = {"position": "absolute", "top": "10px", "left": "10px", "display": "block",
                         "backgroundColor": "white", "padding": "5px", "border": "1px solid #ccc",
                         "borderRadius": "3px", "zIndex": 1000, "fontSize": "12px"}
                return tooltip_text, style
            # When hovering over an edge, display Bandwidth info.
            elif "mouseoverEdgeData" in prop_id and mouseoverEdge:
                bandwidth = mouseoverEdge.get("bandwidth", 100)
                tooltip_text = f"Bandwidth: {bandwidth}"
                style = {"position": "absolute", "top": "10px", "left": "10px", "display": "block",
                         "backgroundColor": "white", "padding": "5px", "border": "1px solid #ccc",
                         "borderRadius": "3px", "zIndex": 1000, "fontSize": "12px"}
                return tooltip_text, style
        raise dash.exceptions.PreventUpdate