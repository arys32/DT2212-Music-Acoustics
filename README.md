# DT2212 Music Acoustics

This repository contains my coursework and technical reports for the DT2212 Music Acoustics course. The projects focus on the programmatic analysis, modeling, and synthesis of acoustic instruments and the human voice using Python.

## Technologies & Libraries Used
* **Python** (Core logic and synthesis)
* **NumPy** (Array manipulation and mathematical modeling)
* **SciPy** (Signal filtering and I/O)
* **Matplotlib** (Spectrogram and waveform visualization)
* **pydub / simpleaudio** (Audio processing and playback)

---

## Assignment 1: Modal Synthesis of a Glockenspiel
This project explores whether a complex percussion instrument can be realistically reconstructed using purely additive synthesis. It analyzes a raw audio recording of a Glockenspiel (note F#5) and rebuilds it from the ground up.

### Key Concepts Explored:
* **Spectral Analysis:** Performed Fast Fourier Transform (FFT) utilizing a 100ms rectangular window with zero padding to identify modal frequencies during the attack (0.0s) and decay (0.7s) phases.
* **Envelope Estimation:** Modeled the amplitude envelope of the partials based on a simple exponential decay law ($A(t)=A_{0}e^{-\gamma t}$). The algorithm specifically handles negative gamma values to prevent modes from artificially growing louder over time.
* **Synthesis & Critique:** Constructed a playback implementation mapping the decaying sinusoids to generate a synthetic melody using Equal Temperament pitch shifting. [cite_start]The report includes a deep critique of the limitations of simple additive synthesis, detailing issues like spectral leakage from rectangular windowing, the instability of two-point decay estimation, and the lack of non-linear damping.

* **[Read the Full Modal Synthesis Report (PDF)](DT2212_Modal_Synthesis/DT2212_Modal_Synthesis_2026.pdf)**

---

## Assignment 2: Voice Synthesis Using Source-Filter Method
This project constructs a digital model of the human voice by generating an idealized glottal source and processing it through a simulated vocal tract to create a singing synthesizer.

### Key Concepts Explored:
* **The Glottal Source:** Utilized additive synthesis (50 sinusoidal partials) to replicate the human glottal flow. This behaves as a sawtooth waveform with a -6 dB/octave slope, incorporating adjustable frequency modulation to simulate natural vibrato (e.g., 4 Hz frequency at 1% amplitude).
* **The Vocal Tract Filter:** Shaped the raw source into specific recognizable vowels using five cascaded two-pole resonators acting as formant filters, calculated via JoLi filter equations.
* **Dynamic Control:** Implemented programmatic control over sound level (dB) and spectral slope to mimic natural vocal dynamics (where a lower slope simulates a louder, brighter voice).
* **Evaluation:** Synthesized a melodic sequence of "Twinkle Twinkle Little Star" transitioning through the vowels `[a] -> [oe] -> [i] -> [u] -> [a2]`. The results were evaluated against a natural human voice recording using spectrogram comparisons. 
* **Critique:** The report details why basic synthesis sounds "robotic", analyzing the drawbacks of perfectly locked phase relationships, static filter coefficients, and the lack of turbulent noise (breathiness).

* **[Read the Full Singing Synthesis Report (PDF)](DT2212_Singing_Synthesis/DT2212_Singing_Synthesis.pdf)**
