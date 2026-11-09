# Design: sound system (v2, S4 / M4 precursor)

## Goal
Define measurable limits for "professional, not harsh" audio before any sound library is built. Every later music bed, SFX, ambience and final mix must pass these numbers so tests can reject bad assets automatically.

This is a design-only milestone. No generation code is written here.

## Target platforms
Primary delivery is web video (YouTube, short-form vertical, social). Secondary: local MP4 for the owner. Broadcast and theatrical are out of scope.

## Units and measurement
- **Integrated loudness**: ITU-R BS.1770 / EBU R128, reported in LUFS.
- **True peak**: oversampled peak (dBTP), not sample peak.
- **Sample rate**: 48 kHz for all final assets and mixes (matches common video pipelines and faster-whisper).
- **Bit depth for intermediates**: 32-bit float. Delivery: 16-bit or 24-bit PCM inside the MP4.
- Measurement tools expected later: ffmpeg `ebur128` filter, or a pure-Python / scipy equivalent that matches BS.1770 within 0.3 LU on reference files.

## Hard limits (every asset and every final mix)

| Quantity | Limit | Why |
|---|---|---|
| Final mix integrated loudness | −14.0 LUFS ± 1.0 LU | Matches current YouTube / social normalisation reference. Quieter content stays quiet; louder is turned down. |
| True peak (final mix and every stem) | ≤ −1.0 dBTP | Prevents inter-sample clipping after AAC/Opus encoding. |
| Sample peak (any generated buffer before limiting) | ≤ −0.3 dBFS | Safety margin before true-peak limiting. |
| Silence | No continuous silence longer than 400 ms in any SFX or music bed that is meant to be continuous; no absolute zero energy on the master for more than 1 s unless intentional. | Catches broken generators. |
| Clipping | Zero samples at or above 0 dBFS after true-peak limiting. | Hard failure. |

## Relative levels (mix rules)
These are the defaults the mixer must apply. They are measurable as gain offsets relative to the voice stem.

| Layer | Default relative level under full voice | Notes |
|---|---|---|
| Voice / narration | 0 dB (reference) | Always the loudest continuous element. |
| Music bed | −9 dB to −12 dB | Duck further (−15 dB or more) under dense speech; raise only in pure music sections. |
| Ambience / roomtone | −18 dB to −28 dB | Continuous world, never competes with voice. |
| One-shot SFX (UI, pop, tick) | −12 dB to −16 dB | Subtle. |
| One-shot SFX (impact, stinger, reveal) | −6 dB to −10 dB | Can momentarily approach voice level. |
| Maximum simultaneous SFX | 2 non-ambient cues | Prevents pile-up. |

Ducking is side-chain style: when voice energy (short-term LUFS or RMS in the speech band) is high, music and ambience are attenuated by the amounts above. Attack ~50 ms, release ~300–500 ms so the bed does not pump.

## Harshness and spectral limits
Phone speakers and cheap earbuds emphasise 3–8 kHz. Harsh SFX make the whole video feel cheap.

| Rule | Limit | How to test later |
|---|---|---|
| High-frequency energy in any single SFX | Energy above 6 kHz must not exceed −18 dBFS RMS in any 50 ms window of the isolated effect (after the effect's own gain). | Band-pass or FFT energy check. |
| Sibilance / metallic rings | No sustained (>80 ms) narrow peaks above 5 kHz that are more than 12 dB above the surrounding spectrum. | Spectral flatness or peak-to-median ratio in the 5–10 kHz band. |
| Music beds | Prefer soft attacks and limited brightness; no continuous white-noise-like high end. | Same high-band energy check on 2 s sliding windows. |

These numbers are starting points. They will be tightened or relaxed after the first library is auditioned on phone speakers.

## Asset categories (for the future skill library)
1. **Music beds** — loopable or sectioned, keyed by mood + intensity (0–1). Moods carried forward from v1 ideas: mystery, tension, action, wonder, hopeful, sad, triumph, playful, calm, dark, epic.
2. **One-shot SFX** — named, deterministic given seed + parameters (duration, pitch, gain).
3. **Ambience** — long loopable beds with short cross-fades.
4. **Stingers / transitions** — short, high-impact, used at story turns.

Each will become a skill of kind `sound` (or sub-kinds) once the loader is extended. The core never hard-codes the asset list.

## Determinism and reproducibility
- Every generator takes an explicit integer seed.
- Same seed + same parameters → identical PCM samples (bit-exact or within floating-point noise floor).
- No wall-clock time, no global random state.

## Out of scope for S4 / early M4
- Real-time DSP plugins or DAW integration.
- Spatial / binaural audio.
- Automatic music composition from video content (mood is chosen by the story plan).
- Voice processing (EQ, de-ess, compression on the narration stem) — that belongs to a later voice pipeline stage.
- Matching the exact timbre of the original v1 audio modules (DEC-001: originals are not binding).

## Acceptance for this design milestone
- This document exists at `docs/design/sound-system.md`.
- Every limit above is stated as a number or a measurable rule that a future test can assert.
- ROADMAP, CURRENT_STATE and ACHIEVEMENTS are updated to mark S4 done.
- No generation code is required for S4 to be considered complete.

## Next implementation step (M4)
1. Implement measurement helpers (loudness, true peak, high-band energy) that the tests will call.
2. Build the first small set of music beds and SFX against these limits.
3. Every asset must pass the numeric suite before it is accepted into `v2/library/`.
4. Final mix of the example project must hit −14 LUFS ± 1 and ≤ −1 dBTP.
