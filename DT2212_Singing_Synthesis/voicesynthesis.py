import numpy as np                  #math library
import matplotlib.pyplot as plt     #for plotting
from pydub import AudioSegment       #for working with audio
import scipy.signal                 #signal processing library
import simpleaudio as sa            #to play sound
from scipy.io.wavfile import write #to write wav files

# --- Parameters ---
fsamp = 44100       #sampling frequency (Hz)
#f_0 = 110           #fundamental frequency (Hz) 
n_partials = 50     
#total_duration = 13  #duration of the sound (seconds) (not needed if making an array of note duration)

A = -0.8

def construct_source(f0_note, duration, volume_db, spec_slope, vibrato_freq, vibrato_amplitude): #options to change note, duration, volume, spectral slope, vibrato frequency and amplitude
    t = np.linspace(0.001, duration, int(fsamp * duration), endpoint=False)  #time vector
    f0 = 440 * 2 ** ((f0_note - 69) / 12)  #convert MIDI note to frequency

    f0_vibrato = f0 * (1 + (vibrato_amplitude / t) * np.sin(2 * np.pi * vibrato_freq * t))  #vibrato effect 

    p = np.zeros_like(t)
    for n in range(1, n_partials + 1):
        p += A*(n**(-spec_slope)) * np.sin(2*np.pi * n * f0_vibrato * t)

    p = p / np.max(np.abs(p))  #normalize to -1 to 1
    gain = 10 ** (volume_db / 20)  #convert dB to linear gain
    return gain * p

def apply_formants(signal, formant_freqs, formant_bandwidths, q_factors):
    T = 1.0 / fsamp
    output = signal.copy()
    #2 pole lowpass formant resonator from JoLi filters cheat sheet
    for f, bw, q in zip(formant_freqs, formant_bandwidths, q_factors):
        beta = f * 2 * np.pi
        beta0 = beta*np.sqrt(1 + 1/(4*q**2))
        alpha = beta0/(2*q)
        a1 = -2*np.exp(-alpha*T)*np.cos(beta0*T)
        a2 = np.exp(-2*alpha*T)
        G = 1 + a1 + a2  #gain

        output = scipy.signal.lfilter([G], [1, a1, a2], output)  #apply filter
    return output

vowel_formants = {
    # /a/ 
    'a': ([596, 1094, 2637, 3672, 4800],        # formant frequencies (Hz)
          [60, 90, 120, 150, 200],              # formant bandwidths (Hz) estimated 
          [9.93, 12.16, 21.98, 24.48, 24.00]),  # quality factor = formant_freq / bandwidth
    
    # /i/ 
    'i': ([258, 2125, 2859, 3468, 4950], 
          [40, 90, 150, 200, 250], 
          [6.45, 23.61, 19.06, 17.34, 19.80]),

    # /u/ 
    'u': ([309, 790, 2354, 3254, 5000], 
          [40, 80, 100, 120, 150], 
          [7.73, 9.88, 23.54, 27.12, 33.33]),

    # /oe/ 
    'oe': ([494, 1234, 2494, 3534, 5600], 
           [50, 90, 120, 150, 200], 
           [9.88, 13.71, 20.78, 23.56, 28.00]),

    # different take on /a/ (from voice lab) with slightly different formant frequencies and bandwidths
    'a2': ([611, 1046, 2720, 3646, 5950],
           [50, 80, 110, 140, 190],
           [12.22, 13.08, 24.72, 26.04, 31.32])

}

# --- Part of Radiohead "Nude" ending melody ---
#melody_notes = [60, 62, 64, 60, 62, 64, 65, 64, 62, 60, 62, 60, 62, 64, 65, 67, 65, 67, 64]  
#melody_notes = [note + 4 for note in melody_notes]  #transpose to E4 starting note
#vowel_sequence = ['u', 'u', 'u', 'u', 'u', 'u', 'u', 'u', 'u', 'u', 'oe', 'a', 'a', 'a', 'a', 'a', 'oe', 'i', 'u']  #vowel sequence for each note
#note_duration = [0.5, 0.5, 0.8, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.6, 0.3, 0.3, 0.3, 0.6, 1.5, 0.6, 0.5, 0.7]

# --- Twinkle Twinkle Little Star melody ---
#melody_notes = [60, 60, 67, 67, 69, 69, 67, 65, 65, 64, 64, 62, 62, 60]
#vowel_sequence = ['i', 'i', 'a', 'a', 'oe', 'oe', 'u', 'a', 'a', 'i', 'i', 'a', 'a', 'u']  #vowel sequence
#note_duration = [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 1.0, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 1.0]

# --- Short Melody ---
melody_notes = [48, 50, 52, 53, 55]  #C, D, E, F, G
vowel_sequence = ['a', 'oe', 'i', 'u', 'a2']  
note_duration = [1.0, 1.0, 1.0, 1.0, 1.0]  

spec_slope = 1.0            #spectral slope (how quickly partials decrease in amplitude) .... 1 = 6 dB/octave
db = 0                      #initial volume in dB (can also make an array of volume for each note to show dynamic control)
vibrato_freq = 4            #vibrato frequency
vibrato_amplitude = 0.001   #vibrato amplitude (1% pitch modulation)

final_signal = np.array([])
for note, vowel, duration in zip(melody_notes, vowel_sequence, note_duration):
    source = construct_source(note, duration, db, spec_slope, vibrato_freq, vibrato_amplitude)  #construct source signal with our parameters
    formant_freqs, formant_bandwidths, q_factors = vowel_formants[vowel]  #get formant parameters
    vowel_sound = apply_formants(source, formant_freqs, formant_bandwidths, q_factors)  #apply formants
    final_signal = np.concatenate((final_signal, vowel_sound))  #concatenate to final signal    
    db -= 2  #decrease volume for next note to create fading effect (show dynamic control)

full_signal_int16 = np.int16(final_signal / np.max(np.abs(final_signal)) * (np.power(2,16)/2))  #normalise and make 16-bit
play = sa.play_buffer(full_signal_int16, 1, 2, fsamp)  #play sound
play.wait_done()  #wait until sound finishes

# ---- Plotting ----
plt.figure(figsize=(10, 8))

#Synthesized Spectrogram
plt.subplot(2, 1, 1)
#NFFT = number of data points in each block for FFT, noverlap = number of points to overlap between blocks 
#from https://www.geeksforgeeks.org/python/matplotlib-pyplot-specgram-in-python/ (note to self)
plt.specgram(full_signal_int16, Fs=fsamp, NFFT=1024, noverlap=512, cmap='magma')
plt.title("Spectrogram: Synthesized Sequence [a] -> [oe] -> [i] -> [u] -> [a2]")
plt.ylabel("Frequency (Hz)")
plt.ylim(0, 6000) #formants most visible below 6000 Hz
plt.colorbar(label='Intensity (dB)')

#Natural Spectrogram for direct comparison (using a home recording of the melody)
plt.subplot(2, 1, 2)
try:
    fs_nat, natural_signal = scipy.io.wavfile.read('alex_recording_home_cut.wav')
        
    plt.specgram(natural_signal, Fs=fs_nat, NFFT=1024, noverlap=512, cmap='magma')
    plt.title("Spectrogram: Natural Human Voice (Home Recording)")
    plt.xlabel("Time (s)")
    plt.ylabel("Frequency (Hz)")
    plt.ylim(0, 6000)
    plt.colorbar(label='Intensity (dB)')
except FileNotFoundError:
    plt.title("Natural Human Voice (Recording not found - please update)")
    plt.xlabel("Time (s)")
    plt.ylabel("Frequency (Hz)")

plt.tight_layout()
plt.show()