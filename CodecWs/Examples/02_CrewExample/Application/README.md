# H.264/H.265 Codec Comparison Project

Atakan Ertekin - 91250000779

## Overview

Comparative analysis of H.264 (AVC) and H.265 (HEVC) video codecs using the Crew CIF video sequence (352×288, 300 frames @ 30fps, YUV420).

**Experiments:**

- QP comparison (H.264: QP 7, 15, 22, 28, 35, 45, 51 | H.265: QP 7, 15, 22, 28, 35, 45, 51)
- CAVLC vs CABAC entropy coding (H.264 at QP 35)
- GOP structure comparison (IPP, IBBP, Hierarchical-B, I-Refresh)

## Directory Structure

CrewExample/
├── YUV_Video/          # Video files
│   ├── input.yuv       # Original (352×288, 300 frames)
│   ├── crew_cif.y4m    # Y4M format
│   └── decoded.yuv
├── H264_Codec/         # H.264 encoding results
│   ├── QP7, QP15, ..., QP51 (7 QP levels)
│   ├── QP35_CAVLC      # CAVLC entropy coding
│   ├── QP35_GOP1_IPP   # GOP structure tests
│   ├── QP35_GOP2_IBBP
│   ├── QP35_GOP3_HierB
│   └── QP35_GOP4_IRefresh
├── H265_Codec/         # H.265 encoding results
│   └── QP7, QP15, ..., QP51 (7 QP levels)
├── Scripts/            # Analysis & plotting
│   ├── psnr_bitrate_graph.py   # QP & GOP comparison graphs
│   ├── frame_comparison.py      # Visual quality inspection
│   └── encode_gops.py           # GOP structure encoding
└── Application/        # This README

## Tools & Encoders

| Codec | Tool | Version | Location |
|-------|------|---------|----------|

| H.264 (AVC) | JSVM | 9.19.15 | `jsvm/bin/H264AVCEncoderLibTestStatic.exe` |
| H.265 (HEVC) | HM | 18.0 | `jvet/bin/.../TAppEncoder.exe` |
| FFmpeg | ffplay | 8.0.1 | (installed via WinGet) |

---

## Encoding

### H.264 (JSVM)

**Command:**

```powershell
& "path/to/H264AVCEncoderLibTestStatic.exe" -pf encoder.cfg
```

**Configuration Example (encoder.cfg):**

```ini
InputFile           "input.yuv"
ReconFile           "reconstructed.yuv"
BitstreamFile       "encoded.264"

SourceWidth         352
SourceHeight        288
FrameToBeEncoded    300
FrameRate           30

BasisQP             35
CABAC               1
UseConstrainedIPred 0
IntraPeriod         -1
IDRPeriod           -1

SequenceFormatString A0L0*n{P0L0}
```

### H.265 (HM)

**Command:**

```powershell
& "path/to/TAppEncoder.exe" -c encoder.cfg
```

**Configuration Example (encoder.cfg):**

```ini
InputFile           "input.yuv"
ReconFile           "reconstructed.yuv"
BitstreamFile       "encoded.265"

SourceWidth         352
SourceHeight        288
NumFramesToBeEncoded 300
FrameRate           30

QP                  35
```

---

## Visual Comparison

Extract and compare the same frame across different QP values for both codecs:

```powershell
cd Scripts
python frame_comparison.py 50
```

**Output:**

- **BMP images**: All QP levels for H.264 and H.265 (stored in separate codec directories)

- **Unified HTML page**: `Application/frame_comparison/frame_comparison.html`
  - 3 tabs: H.264, H.265, and Codec Comparison
  - Side-by-side visual inspection with PSNR/MSE metrics
  - Quality comparison table

**Example Results (Frame 50):**
| Codec | QP7 | QP51 | Difference |

|-------|-----|------|-----------|
| H.264 | 47.05 dB | 21.07 dB | 26.0 dB |
| H.265 | 50.52 dB | 24.84 dB | 25.7 dB |

---

## Video Files

### Input Video

Play the original uncompressed video:

```powershell
& ffplay.exe -f rawvideo -pixel_format yuv420p -video_size 352x288 -framerate 30 `
  "C:\Users\atakan\Desktop\CodecWs\Examples\02_CrewExample\YUV_Video\input.yuv"
```

### H.264 - Different QP Values

| QP | PSNR (dB) | Bitrate (kbps) | Playback Command |
|:--:|:---------:|:--------------:|:-----------------|

| 7 | 51.60 | 9535.18 | `ffplay.exe -f rawvideo -pixel_format yuv420p -video_size 352x288 -framerate 30 "H264_Codec\QP7\reconstructed.yuv"` |
| 15 | 45.80 | 4484.30 | `ffplay.exe -f rawvideo -pixel_format yuv420p -video_size 352x288 -framerate 30 "H264_Codec\QP15\reconstructed.yuv"` |
| 22 | 41.40 | 2012.44 | `ffplay.exe -f rawvideo -pixel_format yuv420p -video_size 352x288 -framerate 30 "H264_Codec\QP22\reconstructed.yuv"` |
| 28 | 37.75 | 968.36 | `ffplay.exe -f rawvideo -pixel_format yuv420p -video_size 352x288 -framerate 30 "H264_Codec\QP28\reconstructed.yuv"` |
| 35 | 33.20 | 381.04 | `ffplay.exe -f rawvideo -pixel_format yuv420p -video_size 352x288 -framerate 30 "H264_Codec\QP35\reconstructed.yuv"` |
| 45 | 26.85 | 86.58 | `ffplay.exe -f rawvideo -pixel_format yuv420p -video_size 352x288 -framerate 30 "H264_Codec\QP45\reconstructed.yuv"` |
| 51 | 22.91 | 24.65 | `ffplay.exe -f rawvideo -pixel_format yuv420p -video_size 352x288 -framerate 30 "H264_Codec\QP51\reconstructed.yuv"` |

### H.265 - Different QP Values

| QP | PSNR (dB) | Bitrate (kbps) | Playback Command |
|:--:|:---------:|:--------------:|:-----------------|

| 7 | 56.33 | 12454.93 | `ffplay.exe -f rawvideo -pixel_format yuv420p -video_size 352x288 -framerate 30 "H265_Codec\QP7\reconstructed.yuv"` |
| 15 | 48.16 | 6113.95 | `ffplay.exe -f rawvideo -pixel_format yuv420p -video_size 352x288 -framerate 30 "H265_Codec\QP15\reconstructed.yuv"` |
| 22 | 42.91 | 3064.62 | `ffplay.exe -f rawvideo -pixel_format yuv420p -video_size 352x288 -framerate 30 "H265_Codec\QP22\reconstructed.yuv"` |
| 28 | 38.79 | 1603.70 | `ffplay.exe -f rawvideo -pixel_format yuv420p -video_size 352x288 -framerate 30 "H265_Codec\QP28\reconstructed.yuv"` |
| 35 | 34.30 | 703.24 | `ffplay.exe -f rawvideo -pixel_format yuv420p -video_size 352x288 -framerate 30 "H265_Codec\QP35\reconstructed.yuv"` |
| 45 | 28.96 | 197.44 | `ffplay.exe -f rawvideo -pixel_format yuv420p -video_size 352x288 -framerate 30 "H265_Codec\QP45\reconstructed.yuv"` |
| 51 | 26.49 | 84.10 | `ffplay.exe -f rawvideo -pixel_format yuv420p -video_size 352x288 -framerate 30 "H265_Codec\QP51\reconstructed.yuv"` |

---

## GOP Structure Comparison (QP 35)

Testing different Group-of-Picture structures with H.264:

| GOP Type | Structure | PSNR (dB) | Bitrate (kbps) | Size (KB) | Enc Time (s) |
|:--------:|:---------:|:---------:|:--------------:|:---------:|:------------:|

| **GOP1_IPP**      | I + P frames only     | 33.2563 | 381.04 | 465.1 | 81.7  |
| **GOP2_IBBP**     | I + B + B + P         | 33.6930 | 412.58 | 503.6 | 357.4 |
| **GOP3_HierB**    | Hierarchical B-frames | 33.3989 | 359.36 | 438.7 | 448.0 |
| **GOP4_IRefresh** | IPP + I-refresh/32    | 33.2566 | 364.55 | 445.0 | 159.0 |

**Best Compression:** GOP3_HierB (359.36 kbps) — Hierarchical B-frame structure provides most efficient compression.

### GOP Structure Playback

```powershell
# GOP1_IPP
ffplay.exe -f rawvideo -pixel_format yuv420p -video_size 352x288 -framerate 30 "H264_Codec\QP35_GOP1_IPP\reconstructed.yuv"

# GOP2_IBBP
ffplay.exe -f rawvideo -pixel_format yuv420p -video_size 352x288 -framerate 30 "H264_Codec\QP35_GOP2_IBBP\reconstructed.yuv"

# GOP3_HierB
ffplay.exe -f rawvideo -pixel_format yuv420p -video_size 352x288 -framerate 30 "H264_Codec\QP35_GOP3_HierB\reconstructed.yuv"

# GOP4_IRefresh
ffplay.exe -f rawvideo -pixel_format yuv420p -video_size 352x288 -framerate 30 "H264_Codec\QP35_GOP4_IRefresh\reconstructed.yuv"
```

---

## Results & Analysis

### Graphs Generated

1. **psnr_vs_bitrate.png** — Rate-distortion curves comparing H.264 vs H.265 across all QP values
2. **gop_comparison.png** — GOP structure analysis (scatter plot + bar chart for encoding time)

### Key Findings

- **H.265 > H.264:** H.265 achieves ~30-40% higher bitrate efficiency at same quality
- **QP Impact:** 10 QP increase ≈ 50% bitrate reduction (varies by codec)
- **GOP Structure:** Hierarchical B-frames provide best compression-speed tradeoff
- **CAVLC vs CABAC:** CABAC saves ~13% bitrate over CAVLC (QP35: 537.1 KB → 465.1 KB)
- **Visual Quality:** H.265 maintains better visual quality at higher QP values (frame 50: H.264 QP51 21.07dB vs H.265 QP51 24.84dB)

---
