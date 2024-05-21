import matplotlib.pyplot as plt
import numpy as np
import mplcursors

# Generate some sample data
x = np.linspace(0, 10, 100)
y = np.sin(x)

# Plot the data
plt.plot(x, y, marker='o', linestyle='-')
plt.title('Hover Test')
plt.xlabel('X')
plt.ylabel('Y')

# Add annotations for hover effect
mplcursors.cursor(hover=True).connect("add", lambda sel: sel.annotation.set_text(f'X: {sel.target[0]}, Y: {sel.target[1]}'))

# Show the plot
plt.show()
