
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# figure
species = 'Bpa'
fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(20, 20))
df = pd.read_csv('../Results/ensemble_px_UMB_Bpa.csv')
ax.plot(df['date'], df['qt=0.5'], color='k')
ax.plot(df['date'], df['ps'], color='lightcoral')
ax.fill_between(df['date'], df['qt=0.05'], df['qt=0.95'],
                color='b', alpha=0.2)
ax.tick_params(labelsize=20)
ax.xaxis.set_major_locator(ticker.MultipleLocator(20))
ax.xaxis.set_tick_params(rotation=20)
ax.set_ylabel('Xylem water potential', fontsize=30)
ax.legend(['px', 'ps'], loc='upper right', fontsize=20, framealpha=0)
