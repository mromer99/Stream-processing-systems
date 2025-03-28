from dash import Dash, html, dcc, Input, Output
import dash_bootstrap_components as dbc
from components.experiment_panel import experiment_panel, register_callbacks
from components.results_panel import results_panel, register_results_callbacks

# Initialize the Dash app
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Benchmarking Tool"
app.config.suppress_callback_exceptions = True  # Suppress callback exceptions for dynamic layout

# Sidebar
sidebar = dbc.Nav(
    [
        dbc.NavLink("Experiment", href="/", active="exact", id="experiment-link"),
        dbc.NavLink("Results", href="/results", active="exact", id="results-link"),
    ],
    vertical=True,
    pills=True,
    className="bg-dark text-light",
    style={"height": "150vh", "padding": "15px"}
)

# Main Layout
app.layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(sidebar, width=2, className="bg-dark"),
                dbc.Col(html.Div(id="page-content"), width=10),
            ],
            className="g-0",
        ),
        dcc.Location(id="url", refresh=False),  # Location for managing URLs
    ],
    fluid=True,
)

# Callback to render pages
@app.callback(
    Output("page-content", "children"),
    [Input("url", "pathname")]
)
def render_page(pathname):
    if pathname == "/" or pathname == "/experiment":
        return experiment_panel
    elif pathname == "/results":
        return results_panel
    return html.Div("404: Page not found", className="text-danger")




# Register Callbacks for experiment_panel
register_callbacks(app)

# Register Callbacks for results_panel
register_results_callbacks(app)



if __name__ == "__main__":
    app.run_server(debug=True)
    