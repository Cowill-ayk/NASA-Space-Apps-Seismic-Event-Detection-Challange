import numpy as np
from obspy import read
from scipy import signal
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import os

# Set the folder containing the miniSEED files
mseed_folder = 'space_apps_2024_seismic_detection/data/lunar/test/data/S16_GradeB/'
output_folder = os.path.join('space_apps_2024_seismic_detection/data/lunar/test/data/S16_GradeBspec/')

# Create the output directory if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

# Set the minimum and maximum frequencies for filtering
minfreq = 0.01
maxfreq = 0.5

# Loop through each miniSEED file in the folder
for filename in os.listdir(mseed_folder):
    if filename.endswith('.mseed'):
        mseed_file = os.path.join(mseed_folder, filename)
        
        # Read the seismic data
        st = read(mseed_file)
        
        # Calculate the mean and standard deviation of the raw data
        for trace in st:
            data = trace.data
            mean = np.mean(data)
            std_dev = np.std(data)
            
            print(f"File: {filename}, Trace ID: {trace.id}")
            print(f"Mean: {mean}")
            print(f"Standard Deviation: {std_dev}\n")
        
        # Create a filtered copy of the trace
        st_filt = st.copy()
        st_filt.filter('bandpass', freqmin=minfreq, freqmax=maxfreq)
        tr_filt = st_filt.traces[0].copy()
        tr_data_filt = tr_filt.data

        # Create spectrogram using scipy
        f, t, sxx = signal.spectrogram(tr_data_filt, tr_filt.stats.sampling_rate)

        # Create a figure with two subplots - one for spectrogram, one for colorbar
        fig, (ax_spec, ax_cbar) = plt.subplots(1, 2, gridspec_kw={'width_ratios': [20, 1]}, figsize=(15, 8))

        # Plot spectrogram
        im = ax_spec.pcolormesh(t, f, sxx, shading='gouraud', cmap='jet')
        ax_spec.set_ylabel('Frequency [Hz]')
        ax_spec.set_xlabel('Time [s]')
        ax_spec.set_title(f'Seismic Spectrogram for {filename}')

        # Add colorbar
        plt.colorbar(im, cax=ax_cbar, label='Power ((m/s)²/sqrt(Hz))')

        # Adjust layout to prevent overlap
        plt.tight_layout()

        # Normalize and save the separate colored image
        normalized = (sxx - sxx.min()) / (sxx.max() - sxx.min())
        colored = (cm.jet(normalized) * 255).astype(np.uint8)
        img = Image.fromarray(colored)
        img = img.resize((2220, 224), Image.Resampling.LANCZOS)
        
        colored_filename = os.path.splitext(filename)[0] + '_colored_spectrogram.png'
        img.save(os.path.join(output_folder, colored_filename))

print("Spectrograms have been generated and saved.")
