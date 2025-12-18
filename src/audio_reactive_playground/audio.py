import librosa
import numpy as np
from scipy.ndimage import gaussian_filter1d

class AudioAnalyzer:
    def __init__(self, audio_path, start_time=0, end_time=None):
        self.audio_path = audio_path
        self.start_time = start_time
        # Load audio using librosa
        self.y, self.sr = librosa.load(audio_path, sr=None, offset=start_time, duration=(end_time - start_time) if end_time else None)
        
        # Compute Spectrogram
        self.n_fft = 2048
        self.hop_length = 512
        self.S = np.abs(librosa.stft(self.y, n_fft=self.n_fft, hop_length=self.hop_length))
        
        # Frequencies
        self.freqs = librosa.fft_frequencies(sr=self.sr, n_fft=self.n_fft)
        
        # Normalize
        self.S_db = librosa.amplitude_to_db(self.S, ref=np.max)
        self.S_norm = (self.S_db + 80) / 80
        self.S_norm = np.clip(self.S_norm, 0, 1)
        
        # Pre-compute energy tracks
        self._compute_energy_tracks()
        
        # Beat Tracking
        self.bpm, self.beat_frames = librosa.beat.beat_track(y=self.y, sr=self.sr, hop_length=self.hop_length)
        # librosa 0.10+ returns bpm as array sometimes
        if isinstance(self.bpm, np.ndarray):
             self.bpm = self.bpm.item() if self.bpm.size > 0 else 120.0
        print(f"  > Detected BPM: {self.bpm:.1f}")

    def _compute_energy_tracks(self):
        # Define masks
        bass_mask = (self.freqs >= 20) & (self.freqs < 250)
        mid_mask = (self.freqs >= 250) & (self.freqs < 2000)
        high_mask = (self.freqs >= 2000) & (self.freqs < 20000)
        
        # Calculate raw energy for each frame
        # Shape: (freqs, frames) -> (frames,)
        
        # 1. Extract bands before normalization to treat them differently?
        # Actually it's better to act on S_db then normalize each band independently.
        # But let's stick to the current flow but normalize more aggressively.
        
        bass_data = self.S_db[bass_mask, :]
        mid_data = self.S_db[mid_mask, :]
        high_data = self.S_db[high_mask, :]
        
        # Helper to normalize a band to 0..1 based on its own running history or static decent stats
        def normalize_band(data, boost=1.0):
             if data.size == 0: return np.zeros(self.S_db.shape[1])
             mean_energy = np.mean(data, axis=0) # Average across freq items in band
             
             # Normalize: Map -80db..0db to 0..1 generally, but let's use percentiles
             # to avoid one loud click crushing everything.
             # Reference Max = 95th percentile of the track
             ref_max = np.percentile(mean_energy, 98) 
             ref_min = np.min(mean_energy)
             
             norm = (mean_energy - ref_min) / (ref_max - ref_min + 1e-6)
             norm = np.clip(norm, 0, 1)
             return norm * boost

        self.raw_bass = normalize_band(bass_data, boost=1.5) # Bass Boost!
        self.raw_mid = normalize_band(mid_data, boost=1.0)
        self.raw_high = normalize_band(high_data, boost=1.2) # Sparkle Boost
        
        # Apply smoothing (sigma=3 frames approx 60ms at 24fps equivalent audio hop)
        self.smooth_bass = gaussian_filter1d(self.raw_bass, sigma=2) # Tighter smoothing for bass (punchier)
        self.smooth_mid = gaussian_filter1d(self.raw_mid, sigma=4)
        self.smooth_high = gaussian_filter1d(self.raw_high, sigma=3)

        # --- NEW: ACCENT DETECTION (Onsets) ---
        # Calculate Onset Strength (transients) using librosa
        onset_env = librosa.onset.onset_strength(y=self.y, sr=self.sr, hop_length=self.hop_length)
        
        # Normalize Onset Envelope
        # We want "Peaks" to stand out.
        ref_onset = np.percentile(onset_env, 99) # Top 1% are hits
        if ref_onset > 0:
            onset_norm = onset_env / ref_onset
            onset_norm = np.clip(onset_norm, 0, 1.2) # Allow slight overdrive but mostly 0-1
        else:
            onset_norm = onset_env
            
        # We don't want too much smoothing here, we want the HIT.
        # Maybe tiny bit to widen the visual window.
        self.accent_track = gaussian_filter1d(onset_norm, sigma=1) 

    def get_energy_at_time(self, time):
        """Returns dictionary of {bass, mid, high} energy at given time"""
        frame_idx = librosa.time_to_frames(time, sr=self.sr, hop_length=self.hop_length, n_fft=self.n_fft)
        
        if frame_idx >= len(self.smooth_bass):
            return {"bass": 0, "mid": 0, "high": 0}
            
        return {
            "bass": self.smooth_bass[frame_idx],
            "mid": self.smooth_mid[frame_idx],
            "high": self.smooth_high[frame_idx],
            "accent": self.accent_track[frame_idx] if frame_idx < len(self.accent_track) else 0.0
        }

    def get_beat_index(self, time):
        """Returns the cumulative beat count at the given time."""
        frame_idx = librosa.time_to_frames(time, sr=self.sr, hop_length=self.hop_length, n_fft=self.n_fft)
        # Count how many beat_frames are <= cur_frame
        # np.searchsorted finds the index where frame_idx would be inserted
        return np.searchsorted(self.beat_frames, frame_idx)
