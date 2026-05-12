import numpy as np                  #math library
import matplotlib.pyplot as plt     #for plotting
from pydub import AudioSegment       #for working with audio
import scipy.signal                 #signal processing library
import simpleaudio as sa            #to play sound
from scipy.io.wavfile import write #to write wav files

gsp_soft = AudioSegment.from_wav('Gsp_ME_p_L-sus_F#5.wav')          #soft f#5 import 
softdata = gsp_soft.get_array_of_samples()/(np.power(2, 16)/2)

gsp_hard = AudioSegment.from_wav('Gsp_ME_f_L-sus_F#5.wav')          #hard f#5 import 
harddata = gsp_hard.get_array_of_samples()/(np.power(2, 16)/2)

# ===================== Global Plot Parameters =======================
params = {'legend.fontsize': 'x-large','figure.figsize': (15, 6),  
         'axes.labelsize': 'x-large','axes.titlesize':'x-large',
         'xtick.labelsize':'x-large','ytick.labelsize':'x-large'}
plt.rcParams.update(params)

#choose where to start and length of snapshot to see difference in waveform clearer (in seconds)
window_start = 0.0
window_length = 1.0

# ======================== Time Domain Plot ==========================

fig, (ax1, ax2) = plt.subplots(1, 2)

# --- Plot 1: Soft Hit ---
times_soft = np.arange(len(softdata)) / gsp_soft.frame_rate
ax1.plot(times_soft, softdata, color='blue', linewidth=1.5)
ax1.set_title('Soft Hit')
ax1.set_xlabel('Time (s)'); ax1.set_ylabel('Amplitude')
ax1.set_xlim((window_start, window_start + window_length))
ax1.set_ylim((-1, 1))
ax1.grid(True, alpha=0.3)

# --- Plot 2: Hard Hit ---
times_hard = np.arange(len(harddata)) / gsp_hard.frame_rate
ax2.plot(times_hard, harddata, color='red', linewidth=1.5)
ax2.set_title('Hard Hit')
ax2.set_xlabel('Time (s)'); ax2.set_ylabel('Amplitude')
ax2.set_xlim((window_start, window_start + window_length))
ax2.set_ylim((-1, 1))
ax2.grid(True, alpha=0.3)

plt.tight_layout()      #brings them closer together
plt.show()

# ======================== Frequency Domain Plot ==========================

win_size_sec = 0.1  #100ms window
t_attack = 0.0      #time of attack
t_decay = 0.7       #time where we want to see the decay spectrum

win_size_samples_soft = int(win_size_sec * gsp_soft.frame_rate)  #num of samples in the window
t_attack_sample_soft = int(t_attack * gsp_soft.frame_rate)     #starting sample for attack
t_decay_sample_soft = int(t_decay * gsp_soft.frame_rate)       #starting sample for decay

win_size_samples_hard = int(win_size_sec * gsp_hard.frame_rate)  
t_attack_samples_hard = int(t_attack * gsp_hard.frame_rate)    
t_decay_samples_hard = int(t_decay * gsp_hard.frame_rate)    

SOFTDATA_ATK = np.fft.fft(softdata[t_attack_sample_soft:t_attack_sample_soft + win_size_samples_soft], n=16384) #fourier transform with rectangular window and zero padding
SOFTDATA_DEC = np.fft.fft(softdata[t_decay_sample_soft:t_decay_sample_soft + win_size_samples_soft], n=16384)
HARDDATA_ATK = np.fft.fft(harddata[t_attack_samples_hard:t_attack_samples_hard + win_size_samples_hard], n=16384)
HARDDATA_DEC = np.fft.fft(harddata[t_decay_samples_hard:t_decay_samples_hard + win_size_samples_hard], n=16384)

freqs_atk_soft = gsp_soft.frame_rate*np.arange(len(SOFTDATA_ATK))/len(SOFTDATA_ATK) #frequency (Hz) of each Fourier sample index
freqs_dec_soft = gsp_soft.frame_rate*np.arange(len(SOFTDATA_DEC))/len(SOFTDATA_DEC)
freqs_atk_hard = gsp_hard.frame_rate*np.arange(len(HARDDATA_ATK))/len(HARDDATA_ATK)
freqs_dec_hard = gsp_hard.frame_rate*np.arange(len(HARDDATA_DEC))/len(HARDDATA_DEC) 

MAG_ATK_SOFT = np.abs(SOFTDATA_ATK) #magnitude of each Fourier sample index
MAG_DEC_SOFT = np.abs(SOFTDATA_DEC)
MAG_ATK_HARD = np.abs(HARDDATA_ATK)
MAG_DEC_HARD = np.abs(HARDDATA_DEC)

fig, (ax1, ax2) = plt.subplots(1, 2)

# --- Spectrum 1: Soft Hit (Attack vs Decay) ---
ax1.plot(freqs_atk_soft, MAG_ATK_SOFT, '--', label=f'Attack ({t_attack}s)', color='skyblue')
ax1.plot(freqs_dec_soft, MAG_DEC_SOFT, '-', label=f'Decay ({t_decay}s)', color='blue', alpha=0.9)
ax1.set_title('Soft Strike Spectra')
ax1.set_xlabel('Frequency (Hz)'); ax1.set_ylabel('Magnitude')
ax1.set_xlim((0, 15000))
ax1.legend(loc = 'upper right')
ax1.grid(True)

# --- Spectrum 2: Hard Hit (Attack vs Decay) ---
ax2.plot(freqs_atk_hard, MAG_ATK_HARD, '--', label=f'Attack ({t_attack}s)', color='sandybrown')
ax2.plot(freqs_dec_hard, MAG_DEC_HARD, '-', label=f'Decay ({t_decay}s)', color='darkred', alpha=0.9)
ax2.set_title('Hard Strike Spectra')
ax2.set_xlabel('Frequency (Hz)'); ax2.set_ylabel('Magnitude')
ax2.set_xlim((0, 15000))
ax2.legend(loc = 'upper right')
ax2.grid(True)

plt.tight_layout()
plt.show()

# ==================== dB Magnitude Spectrum ===================

# Compute dB magnitude spectrum with reference to the max absolute value in each specific segment
# This normalizes the peak to 0 dB
MAG_ATK_SOFT_DB = 20 * np.log10(np.abs(SOFTDATA_ATK) / np.max(np.abs(SOFTDATA_ATK)))
MAG_DEC_SOFT_DB = 20 * np.log10(np.abs(SOFTDATA_DEC) / np.max(np.abs(SOFTDATA_DEC)))
MAG_ATK_HARD_DB = 20 * np.log10(np.abs(HARDDATA_ATK) / np.max(np.abs(HARDDATA_ATK)))
MAG_DEC_HARD_DB = 20 * np.log10(np.abs(HARDDATA_DEC) / np.max(np.abs(HARDDATA_DEC)))

fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2)

# --- Spectrum 1: Soft Attack in dB ---
ax1.plot(freqs_atk_soft, MAG_ATK_SOFT_DB, color='skyblue')
ax1.set_title(f'Soft Strike: Attack ({t_attack}s)')
ax1.set_xlim(0, 15000); ax1.set_ylim(-60, 1); ax1.grid(True, alpha=0.3)
ax1.set_xlabel('Frequency (Hz)'); ax1.set_ylabel('Magnitude (dB)')
peaks_atk_soft, _ = scipy.signal.find_peaks(MAG_ATK_SOFT_DB[0:int(len(MAG_ATK_SOFT_DB)/2)], height=-22, distance=100) #detect peaks above -22 dB and at least 100 Hz apart
peaks_atk_soft = peaks_atk_soft[freqs_atk_soft[peaks_atk_soft] < 15000]     #filter peaks to only those below 15 kHz
for p in peaks_atk_soft:
   ax1.plot([freqs_atk_soft[p],freqs_atk_soft[p]],[-60,0],'k--',alpha=0.6)

# --- Spectrum 2: Soft Decay in dB ---
ax2.plot(freqs_dec_soft, MAG_DEC_SOFT_DB, color='blue')
ax2.set_title(f'Soft Strike: Decay ({t_decay}s)')
ax2.set_xlim(0, 15000); ax2.set_ylim(-60, 1); ax2.grid(True, alpha=0.3)
ax2.set_xlabel('Frequency (Hz)'); ax2.set_ylabel('Magnitude (dB)')
peaks_dec_soft, _ = scipy.signal.find_peaks(MAG_DEC_SOFT_DB[0:int(len(MAG_DEC_SOFT_DB)/2)], height=-22, distance=100)
peaks_dec_soft = peaks_dec_soft[freqs_dec_soft[peaks_dec_soft] < 15000]                                               
for p in peaks_dec_soft:
   ax2.plot([freqs_dec_soft[p],freqs_dec_soft[p]],[-60,0],'k--',alpha=0.6)

# --- Spectrum 3: Hard Attack in dB ---
ax3.plot(freqs_atk_hard, MAG_ATK_HARD_DB, color='sandybrown')
ax3.set_title(f'Hard Strike: Attack ({t_attack}s)')
ax3.set_xlim(0, 15000); ax3.set_ylim(-60, 1); ax3.grid(True, alpha=0.3)
ax3.set_xlabel('Frequency (Hz)'); ax3.set_ylabel('Magnitude (dB)')
peaks_atk_hard, _ = scipy.signal.find_peaks(MAG_ATK_HARD_DB[0:int(len(MAG_ATK_HARD_DB)/2)], height=-22, distance=100)
peaks_atk_hard = peaks_atk_hard[freqs_atk_hard[peaks_atk_hard] < 15000]  
for p in peaks_atk_hard:
   ax3.plot([freqs_atk_hard[p],freqs_atk_hard[p]],[-60,0],'k--',alpha=0.6)

# --- Spectrum 4: Hard Decay in dB ---
ax4.plot(freqs_dec_hard, MAG_DEC_HARD_DB, color='darkred')
ax4.set_title(f'Hard Strike: Decay ({t_decay}s)')
ax4.set_xlim(0, 15000); ax4.set_ylim(-60, 1); ax4.grid(True, alpha=0.3)
ax4.set_xlabel('Frequency (Hz)'); ax4.set_ylabel('Magnitude (dB)')
peaks_dec_hard, _ = scipy.signal.find_peaks(MAG_DEC_HARD_DB[0:int(len(MAG_DEC_HARD_DB)/2)], height=-22, distance=100)
peaks_dec_hard = peaks_dec_hard[freqs_dec_hard[peaks_dec_hard] < 15000]                                               
for p in peaks_dec_hard:
   ax4.plot([freqs_dec_hard[p],freqs_dec_hard[p]],[-60,0],'k--',alpha=0.6)

plt.tight_layout()
plt.show()

# ==================== EXPONENTIAL ENVELOPE AND SYNTHESIS ESTIMATION FOR HARD STRIKE ====================

# --- Plotting Envelopes ---
fig, ax = plt.subplots()
ax.set_title(f'Estimated Modal Envelopes (Hard Strike) - {len(peaks_atk_hard)} modes')
counter = 0
dt = t_decay - t_attack #time difference

for ii in peaks_atk_hard:
   amp1 = MAG_ATK_HARD_DB[ii] 
   amp2 = MAG_DEC_HARD_DB[ii]
   
   gamma = (np.log(10)/20) * (amp1 - amp2) / dt

   if gamma <= 0: gamma = 0.05 #handle non positive gamma values to remove over sustained modes
   A = np.power(10, amp1/20) * np.power(10, gamma * t_attack/np.log10(np.exp(1)))
   
   et = np.arange(0, 5 * gsp_hard.frame_rate) / gsp_hard.frame_rate
   envelope = A * np.exp(-gamma * et)

   ax.plot(et, envelope, color='k', alpha=1)
   counter += 1

plt.xlabel('Time (s)'); plt.ylabel('Amplitude')
plt.xlim((0, 5)); ax.grid(True, alpha=0.3)
plt.show()

# --- Synthesis ---
tonedur = 5
N = int(tonedur * gsp_hard.frame_rate)
n = np.arange(N)
ysum_hard = np.zeros((N,))

for ii in peaks_atk_hard:
   amp1 = MAG_ATK_HARD_DB[ii]
   amp2 = MAG_DEC_HARD_DB[ii]
   
   gamma = (np.log(10)/20) * (amp1 - amp2) / dt

   if gamma <= 0: gamma = 0.05 #handle non positive gamma values to remove over sustained modes
   
   A = np.power(10, amp1/20) * np.power(10,gamma * t_attack/np.log10(np.exp(1))) 
   t = np.arange(0,tonedur*gsp_hard.frame_rate)
   
   #synthesize sinusoid: A * exp(-gamma*t) * cos(2pi*f*t + phase)
   envelope = A*np.exp(-gamma*t/gsp_hard.frame_rate)
   ysum_hard += envelope*np.cos(2*np.pi*freqs_atk_hard[ii]*n/gsp_hard.frame_rate 
                  + np.angle(HARDDATA_ATK[ii])) 
   

# ==================== EXPONENTIAL ENVELOPE AND SYNTHESIS ESTIMATION FOR SOFT STRIKE ====================

# --- Plotting Envelopes ---
fig, ax = plt.subplots()
ax.set_title(f'Estimated Modal Envelopes (Soft Strike) - {len(peaks_atk_soft)} modes')
counter = 0
dt = t_decay - t_attack

for ii in peaks_atk_soft:
   amp1 = MAG_ATK_SOFT_DB[ii] 
   amp2 = MAG_DEC_SOFT_DB[ii]
   
   gamma = (np.log(10)/20) * (amp1 - amp2) / dt

   if gamma <= 0: gamma = 0.05 #handle non positive gamma values to remove over sustained modes
   A = np.power(10, amp1/20) * np.power(10, gamma * t_attack/np.log10(np.exp(1)))
   
   et = np.arange(0, 5 * gsp_hard.frame_rate) / gsp_hard.frame_rate
   envelope = A * np.exp(-gamma * et)

   ax.plot(et, envelope, color='k', alpha=1)
   counter += 1

plt.xlabel('Time (s)'); plt.ylabel('Amplitude')
plt.xlim((0, 5)); ax.grid(True, alpha=0.3)
plt.show()

# --- Synthesis ---
tonedur = 5
N = int(tonedur * gsp_soft.frame_rate)
n = np.arange(N)
ysum_soft = np.zeros((N,))

for ii in peaks_atk_soft:
   amp1 = MAG_ATK_SOFT_DB[ii]
   amp2 = MAG_DEC_SOFT_DB[ii]
   
   gamma = (np.log(10)/20) * (amp1 - amp2) / dt

   if gamma <= 0: gamma = 0.05 #handle non positive gamma values to remove over sustained modes
   
   A = np.power(10, amp1/20) * np.power(10,gamma * t_attack/np.log10(np.exp(1))) 
   t = np.arange(0,tonedur*gsp_soft.frame_rate)
   
   #synthesize sinusoid: A * exp(-gamma*t) * cos(2pi*f*t + phase)
   envelope = A*np.exp(-gamma*t/gsp_soft.frame_rate)
   ysum_soft += envelope*np.cos(2*np.pi*freqs_atk_soft[ii]*n/gsp_soft.frame_rate 
                  + np.angle(SOFTDATA_ATK[ii])) 

# ==================== PLAYBACK OF SYNTHESIS RESULTS ====================

ysum_hard /= np.max(np.abs(ysum_hard)) #normalize
ysum_hard = np.concatenate((harddata[0:len(ysum_hard)],ysum_hard))
ysum_scaled_hard = np.int16(ysum_hard / np.max(np.abs(ysum_hard)) * (np.power(2,16)/2)) #make 16-bit
#write("gsp_hardstrikef#5_synthesis_concatenated.wav", gsp_hard.frame_rate, ysum_scaled_hard)
play_obj = sa.play_buffer(ysum_scaled_hard, 1, 2, gsp_hard.frame_rate)
#doesnt seem to sound like a big difference between the real imported sound and the synthesis 
#but the imported sound is different to the original recording for some reason
play_obj.wait_done()

input("Press Enter to play the soft strike synthesis...")

ysum_soft /= np.max(np.abs(ysum_soft)) #normalize
ysum_soft = np.concatenate((softdata[0:len(ysum_soft)],ysum_soft))
ysum_scaled_soft = np.int16(ysum_soft / np.max(np.abs(ysum_soft)) * (np.power(2,16)/2)) #make 16-bit
#write("gsp_softstrikef#5_synthesis_concatenated.wav", gsp_soft.frame_rate, ysum_scaled_soft) 
play_obj = sa.play_buffer(ysum_scaled_soft, 1, 2, gsp_soft.frame_rate)
play_obj.wait_done()

# ======= MELODY =========
def synthesize_note(semitone_shift, duration_sec):

   #calculate pitch ratio (Equal Temperament)
   #0 = same pitch, 12 = octave up, -12 = octave down
   pitch_ratio = 2 ** (semitone_shift / 12.0)
   
   N_note = int(duration_sec * gsp_soft.frame_rate)
   n_l = np.arange(N_note)
   ysum_note = np.zeros((N_note,))

   for ii in peaks_atk_soft:
      amp1 = MAG_ATK_SOFT_DB[ii]
      amp2 = MAG_DEC_SOFT_DB[ii]

      gamma = (np.log(10)/20) * (amp1 - amp2) / dt

      if gamma <= 0: gamma = 0.05

      A = np.power(10, amp1/20) * np.power(10,gamma * t_attack/np.log10(np.exp(1))) 
      t = np.arange(0,duration_sec*gsp_soft.frame_rate)

      freq_shifted = freqs_atk_hard[ii] * pitch_ratio

      envelope = A*np.exp(-gamma*t/gsp_soft.frame_rate)
      ysum_note += envelope*np.cos(2*np.pi*freq_shifted*n_l/gsp_soft.frame_rate 
                     + np.angle(HARDDATA_ATK[ii])) 
        
   return ysum_note

# format: (Semitone Shift, Duration)
# 0 is original pitch. 2 is whole step up, etc.
melody_notes = [
   (2, 0.4),
   (0,  0.5),  
   (2, 0.4),
   (-2, 0.6),  
   (2,  0.3),  
   (-2,  0.3),  
   (0,  0.3),  
   (2,  0.3),  #here comes the sun..
]

full_melody_audio = np.array([])

for note in melody_notes:
   semitone, dur = note
   
   #generate the note
   note_audio = synthesize_note(semitone, dur)
      
   #append to track
   full_melody_audio = np.concatenate((full_melody_audio, note_audio))

full_melody_audio /= np.max(np.abs(full_melody_audio))
melody_pcm = np.int16(full_melody_audio / np.max(np.abs(full_melody_audio)) * (np.power(2,16)/2)) #make 16-bit
play_obj = sa.play_buffer(melody_pcm, 1, 2, gsp_hard.frame_rate)
play_obj.wait_done()
   
#write("synthesised_melody.wav", gsp_hard.frame_rate, melody_pcm)