from dash import html, dcc, Input, Output, State, ctx, no_update
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import os, base64
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO

def generate_default_plot(df):
    x_column = df.columns[0]
    y_column = df.columns[1]
    plt.figure(figsize=(8, 5))
    plt.plot(df[x_column], df[y_column], marker="o", linestyle="-", color="blue")
    plt.title(f"Graph: {x_column} vs {y_column}")
    plt.xlabel(x_column)
    plt.ylabel(y_column)
    plt.grid(True)
    buf = BytesIO()
    plt.savefig(buf, format="png")
    plt.close()
    buf.seek(0)
    encoded_image = base64.b64encode(buf.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{encoded_image}"

# Results Panel Layout: Initially only an "Open CSV File" button is shown.
# The dcc.Upload is wrapped in an html.Div (with id "upload-container") that has an n_clicks property.
results_panel = dbc.Card(
    dbc.CardBody(
        [
            html.Div(
                dcc.Upload(
                    id="upload-csv",
                    children=dbc.Button("Open CSV File", color="primary"),
                    accept=".csv",
                    style={
                        "width": "100%",
                        "textAlign": "center",
                        "padding": "20px"
                    }
                ),
                id="upload-container",
                n_clicks=0,
                style={"cursor": "pointer"}
            ),
            # Hidden store to keep the uploaded CSV content.
            dcc.Store(id="uploaded-csv-store"),
            # Modal for displaying the CSV plot along with style selection buttons.
            dbc.Modal(
                [
                    dbc.ModalHeader(
                        [
                            dbc.ModalTitle("CSV Plot"),
                            dbc.ButtonGroup(
                                [
                                    dbc.Button("Default", id="plot-style-default", color="secondary", n_clicks=0),
                                    dbc.Button("Box Plot", id="plot-style-box", color="secondary", n_clicks=0),
                                    dbc.Button("Bar Chart", id="plot-style-bar", color="secondary", n_clicks=0),
                                ],
                                size="sm",
                                style={"marginLeft": "20px"}
                            )
                        ]
                    ),
                    dbc.ModalBody(html.Img(id="csv-plot-img", style={"width": "100%"})),
                    dbc.ModalFooter(
                        dbc.Button("Close", id="close-plot-modal", className="ms-auto", n_clicks=0)
                    ),
                ],
                id="csv-plot-modal",
                is_open=False,
                centered=True,
                backdrop=True,
                size="lg"
            )
        ]
    ),
    style={"padding": "20px", "box-shadow": "0px 4px 8px rgba(0, 0, 0, 0.1)"}
)

def register_results_callbacks(app):

    # Combined callback to handle new file upload, re-click on the upload container, and modal close.
    @app.callback(
        [Output("csv-plot-modal", "is_open"),
         Output("csv-plot-img", "src"),
         Output("uploaded-csv-store", "data")],
        [Input("upload-csv", "contents"),
         Input("upload-container", "n_clicks"),
         Input("close-plot-modal", "n_clicks")],
        [State("uploaded-csv-store", "data")]
    )
    def open_modal_callback(upload_contents, container_clicks, close_clicks, stored_data):
        triggered = ctx.triggered
        if not triggered:
            raise PreventUpdate
        prop_id = triggered[0]["prop_id"]

        # If the Close button was clicked, close the modal.
        if "close-plot-modal" in prop_id:
            return False, no_update, stored_data

        # If a new file is uploaded:
        if "upload-csv.contents" in prop_id:
            if upload_contents:
                try:
                    content_type, content_string = upload_contents.split(',')
                    decoded = base64.b64decode(content_string)
                    df = pd.read_csv(BytesIO(decoded))
                    if len(df.columns) < 2:
                        print("[ERROR] CSV must have at least two columns for plotting.")
                        return no_update, no_update, no_update
                    image_src = generate_default_plot(df)
                    return True, image_src, upload_contents
                except Exception as e:
                    print(f"[ERROR] Failed to generate plot: {e}")
                    return no_update, no_update, no_update
            else:
                return no_update, no_update, stored_data

        # If the upload container is clicked (re-click) and stored data exists:
        if "upload-container.n_clicks" in prop_id:
            if stored_data:
                try:
                    content_type, content_string = stored_data.split(',')
                    decoded = base64.b64decode(content_string)
                    df = pd.read_csv(BytesIO(decoded))
                    if len(df.columns) < 2:
                        print("[ERROR] CSV must have at least two columns for plotting.")
                        return no_update, no_update, stored_data
                    image_src = generate_default_plot(df)
                    return True, image_src, stored_data
                except Exception as e:
                    print(f"[ERROR] Failed to re-generate plot: {e}")
                    return no_update, no_update, stored_data
            else:
                return no_update, no_update, stored_data

        return no_update, no_update, stored_data

    # Callback for updating plot style from the style buttons.
    @app.callback(
        Output("csv-plot-img", "src", allow_duplicate=True),
        [Input("plot-style-default", "n_clicks"),
         Input("plot-style-box", "n_clicks"),
         Input("plot-style-bar", "n_clicks")],
        [State("uploaded-csv-store", "data")],
        prevent_initial_call='initial_duplicate'
    )
    def update_plot_style(n_default, n_box, n_bar, stored_contents):
        if not stored_contents:
            return no_update
        trigger = ctx.triggered[0]["prop_id"]
        try:
            content_type, content_string = stored_contents.split(',')
            decoded = base64.b64decode(content_string)
            df = pd.read_csv(BytesIO(decoded))
            if len(df.columns) < 2:
                print("[ERROR] CSV must have at least two columns for plotting.")
                return no_update
            x_column = df.columns[0]
            y_column = df.columns[1]
            plt.figure(figsize=(8, 5))
            if "plot-style-default" in trigger:
                plt.plot(df[x_column], df[y_column], marker="o", linestyle="-", color="blue")
                plt.title(f"Graph: {x_column} vs {y_column}")
                plt.xlabel(x_column)
                plt.ylabel(y_column)
            elif "plot-style-box" in trigger:
                plt.boxplot(df[y_column])
                plt.title(f"Box Plot: {y_column}")
                plt.xticks([1], [y_column])
            elif "plot-style-bar" in trigger:
                plt.bar(df[x_column], df[y_column], color="blue")
                plt.title(f"Bar Chart: {x_column} vs {y_column}")
                plt.xlabel(x_column)
                plt.ylabel(y_column)
            plt.grid(True)
            buf = BytesIO()
            plt.savefig(buf, format="png")
            plt.close()
            buf.seek(0)
            encoded_image = base64.b64encode(buf.getvalue()).decode("utf-8")
            return f"data:image/png;base64,{encoded_image}"
        except Exception as e:
            print(f"[ERROR] Failed to update plot style: {e}")
            return no_update
    