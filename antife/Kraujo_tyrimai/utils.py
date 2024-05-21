import matplotlib.pyplot as plt
import base64
from io import BytesIO
import numpy as np

def get_graph():
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    graph = base64.b64encode(image_png)
    graph = graph.decode('utf-8')
    buffer.close()
    return graph

import mplcursors

import matplotlib.pyplot as plt
import base64
from io import BytesIO
import numpy as np
import mplcursors

def get_plot(x, y, dates):
    plt.switch_backend('AGG')
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.set_title('Kraujo tyrimai')

    # Plot the line
    line, = ax.plot(x, y, marker='o', linestyle='-')

    ax.set_xlabel('Data')
    ax.set_ylabel('Fenilalaninas µmol/l')

    ax.set_xticks(np.linspace(0, len(x) - 1, len(dates)))
    ax.set_xticklabels(dates, rotation=45, ha='right')

    ax.set_yticks(np.arange(0, 900, 100))

    ax.axhspan(120, 600, color='green', alpha=0.3)

    ax.set_ylim(0, 900)

    mplcursors.cursor(line, hover=True).connect("add", lambda sel: sel.annotation.set_text(
        f"Date: {dates[int(sel.target[0])]}, Fenilalaninas: {y[int(sel.target[0])]}"))

    # Save the plot to a buffer
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    graph = base64.b64encode(image_png)
    graph = graph.decode('utf-8')
    buffer.close()

    return graph




