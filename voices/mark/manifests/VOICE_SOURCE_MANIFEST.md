# Voice Source Manifest — Mark

## Current status

- **Smoke test:** PASSED (contaminated YouTube reference)
- **Production voice profile:** PASSED (clean dry source found)
- **Source quality:** A / original dry mic recordings

## Source discovery

**Date:** 2026-04-27
**Location:** `/Volumes/WD 4/LaCie Fall/Novaxe Control Center Collected folder/(Footage)/Novaxe Introduction April 10 sod.aep/`
**Method:** After Effects bundle footage search

Found 61 original dry voice recordings inside After Effects project bundles, named verbatim after the phrases spoken in the video.

## Known files

### Contaminated (deprecated)
- `assets/voice/mark/raw/mark_youtube_sample.wav` — mixed with music, DO NOT USE
- `assets/voice/mark/processed/mark_reference_24k_mono.wav` — derived from mixed source

### Clean source (production)
- **54 phrase MP3s + narration files** in `voices/mark/raw/ae_phrase_takes/`
  - Examples: `a place for teachers.mp3`, `I remember.mp3`, `when you want to learn a song.mp3`
- **Narration 130pm.mp3** — 1:10 full narration take
- **Narration Final.mp3** — 5:48 extended narration
- **Concatenated reference:** `voices/mark/processed/datasets/mark_phrases_concat_24k_mono.wav` (10:27)
- **30s production reference:** `voices/mark/processed/references/mark_narration_30s_24k_mono.wav`

### Generated output
- `artifacts/voice/mark/rockyai_tutor_voice_smoke_test.wav` — contaminated smoke test
- `artifacts/voice/mark/rockyai_tutor_voice_clean_production.wav` — **PRODUCTION CLONE**

## Production gate

✅ **CLOSED.** Clean dry mic recordings found in After Effects source bundles.
F5-TTS zero-shot inference successful using `mark_narration_30s_24k_mono.wav`.

## Disclosure

All generated voice outputs using this profile must be labeled AI-generated when published externally.
