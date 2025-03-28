import pandas as pd
import matplotlib.pyplot as plt

def create_plot(file_path):
    try:
        file_path = "test.csv"
        print(f"Reading file: {file_path}")
        df = pd.read_csv(file_path)
        print(f"File loaded successfully: {file_path}")
        print(f"Columns: {df.columns.tolist()}")

        if len(df.columns) < 2:
            raise ValueError("CSV must contain at least two columns for plotting.")

        x_column = df.columns[0]
        y_column = df.columns[1]

        # Generate the scatter plot
        plt.figure(figsize=(10, 6))
        plt.scatter(df[x_column], df[y_column], color="blue", alpha=0.7)
        plt.title(f"Scatter Plot: {x_column} vs {y_column}")
        plt.xlabel(x_column)
        plt.ylabel(y_column)
        plt.grid(True)

        # Save the plot to a file
        output_path = "scatter_plot.png"
        plt.savefig(output_path)
        print(f"Plot saved to {output_path}")
        plt.close()
    except Exception as e:
        print(f"Error: {e}")

# Test the function
if __name__ == "__main__":
    test_file = "results/test.csv"  # Replace with the path to your CSV file
    create_plot(test_file)
