#!/usr/bin/env python3
"""
Matched Encoder Configuration - Fair H.264 vs H.265 Rate-Distortion Comparison

Creates encoder configs and runs encoding for both codecs with matched parameters:
  - Hierarchical B-frames (GOP=4 for H.264, GOP=8 for H.265)
  - IntraPeriod: 32
  - RefFrames: 4
  - SearchRange: 64
  - Deblocking: On
  - CABAC (H.264) / SAO+AMP (H.265)

Usage:
    python matched_encode.py                  # Create configs + encode ALL missing QPs
    python matched_encode.py --configs-only   # Only create config files (no encoding)
    python matched_encode.py 22 35            # Encode only specified QP values
"""
import os
import sys
import subprocess
import time
from config import *

# ============================================================
# Target QP values for RD comparison
# ============================================================
QP_VALUES = [7, 15, 22, 28, 35, 45]

# ============================================================
# H.264 (JSVM) Config Template
# GOP=4 Hierarchical B, I-refresh every 32 frames
# ============================================================
H264_CONFIG_TEMPLATE = """# JSVM Configuration - Matched RD Comparison
# Hierarchical B (GOP=4), IntraPeriod=32, RefFrames=4

#====================== GENERAL ================================================
AVCMode                 1
InputFile               ..\\..\\YUV_Video\\input.yuv
OutputFile              encoded.264
ReconFile               reconstructed.yuv
SourceWidth             352
SourceHeight            288
FrameRate               30.0
FramesToBeEncoded       300

#====================== CODING =================================================
SymbolMode              1          # CABAC
Enable8x8Transform      1
ConstrainedIntraPred    0
ScalingMatricesPresent  1
BiPred8x8Disable        0
MCBlocksLT8x8Disable    0
BasisQP                 {qp}

#====================== STRUCTURE ==============================================
DPBSize                 4
NumRefFrames            4
Log2MaxFrameNum         11
Log2MaxPocLsb           10

# GOP=4 Hierarchical B with I-refresh every 32 frames (8 GOPs of 4)
SequenceFormatString    A0L0*n{{*8{{P3L0B1L1b0L2b2L2}}*1{{I3L0B1L1b0L2b2L2}}}}

DeltaLayer0Quant        0
DeltaLayer1Quant        1
DeltaLayer2Quant        2
MaxRefIdxActiveBL0      2
MaxRefIdxActiveBL1      2
MaxRefIdxActiveP        2

#============================== MOTION SEARCH ==================================
SearchMode              4
SearchFuncFullPel       0
SearchFuncSubPel        2
SearchRange             64
BiPredIter              4
IterSearchRange         8

#============================== LOOP FILTER ====================================
LoopFilterDisable       0
LoopFilterAlphaC0Offset 0
LoopFilterBetaOffset    0
"""

# ============================================================
# H.265 (HM) Config Template
# GOP=8 Random Access, IntraPeriod=32, RefFrames=4
# ============================================================
H265_CONFIG_TEMPLATE = """#======== File I/O =====================
InputFile                     : ..\\..\\YUV_Video\\input.yuv
BitstreamFile                 : encoded.265
ReconFile                     : reconstructed.yuv

#======== Profile ================
Profile                       : main

#======== Input ================
InputBitDepth                 : 8
InputChromaFormat             : 420
FrameRate                     : 30
FrameSkip                     : 0
SourceWidth                   : 352
SourceHeight                  : 288
FramesToBeEncoded             : 300

#======== Unit definition ================
MaxCUWidth                    : 64
MaxCUHeight                   : 64
MaxPartitionDepth             : 4
QuadtreeTULog2MaxSize         : 5
QuadtreeTULog2MinSize         : 2
QuadtreeTUMaxDepthInter       : 3
QuadtreeTUMaxDepthIntra       : 3

#======== Coding Structure =============
IntraPeriod                   : 32
DecodingRefreshType           : 1
GOPSize                       : 8
ReWriteParamSetsFlag          : 1

IntraQPOffset                 : -1
LambdaFromQpEnable            : 1

#        Type POC QPoffset QPOffsetModelOff QPOffsetModelScale CbQPoffset CrQPoffset QPfactor tcOffsetDiv2 betaOffsetDiv2 temporal_id #ref_pics_active #ref_pics reference pictures     predict deltaRPS #ref_idcs reference idcs
Frame1:  B    8   1        0.0                      0.0            0          0          1.0      0            0              0           2                2        -8 -16                    0
Frame2:  B    4   4       -5.7476                   0.2286         0          0          1.0      0            0              1           2                3         -4 -12   4                1      4    3    1 1 1
Frame3:  B    2   5       -5.90                     0.2333         0          0          1.0      0            0              2           2                4         -2 -10   2   6            1      2    4    1 1 1 1
Frame4:  B    1   6       -7.1444                   0.3            0          0          1.0      0            0              3           2                4         -1   1   3   7            1      1    5    1 0 1 1 1
Frame5:  B    3   6       -7.1444                   0.3            0          0          1.0      0            0              3           2                4         -1  -3   1   5            1     -2    5    1 1 1 1 0
Frame6:  B    6   5       -5.90                     0.2333         0          0          1.0      0            0              2           2                3         -2  -6   2                1     -3    5    0 1 1 1 0
Frame7:  B    5   6       -7.1444                   0.3            0          0          1.0      0            0              3           2                4         -1  -5   1   3            1      1    4    1 1 1 1
Frame8:  B    7   6       -7.1444                   0.3            0          0          1.0      0            0              3           2                3         -1  -7   1                1     -2    5    0 1 1 1 0

#=========== Motion Search =============
FastSearch                    : 1
SearchRange                   : 64
ASR                           : 1
MinSearchWindow               : 8
BipredSearchRange             : 4
HadamardME                    : 1
FEN                           : 1
FDM                           : 1

#======== Quantization =============
QP                            : {qp}
MaxDeltaQP                    : 0
MaxCuDQPDepth                 : 0
DeltaQpRD                     : 0
RDOQ                          : 1
RDOQTS                        : 1

#=========== Deblock Filter ============
LoopFilterOffsetInPPS         : 1
LoopFilterDisable             : 0
LoopFilterBetaOffset_div2     : 0
LoopFilterTcOffset_div2       : 0

#=========== Misc. ============
InternalBitDepth              : 8

#=========== Coding Tools =================
SAO                           : 1
AMP                           : 1
TransformSkip                 : 1
TransformSkipFast             : 1
SAOLcuBoundary                : 0

#============ Slices ================
SliceMode                     : 0
SliceArgument                 : 1500
LFCrossSliceBoundaryFlag      : 1

#============ PCM ================
PCMEnabledFlag                : 0
PCMLog2MaxSize                : 5
PCMLog2MinSize                : 3
PCMInputBitDepthFlag          : 1
PCMFilterDisableFlag          : 0

#============ Tiles ================
TileUniformSpacing            : 0
NumTileColumnsMinus1          : 0
TileColumnWidthArray          : 2 3
NumTileRowsMinus1             : 0
TileRowHeightArray            : 2
LFCrossTileBoundaryFlag       : 1

#============ WaveFront ================
WaveFrontSynchro              : 0

#=========== Quantization Matrix =================
ScalingList                   : 0
ScalingListFile               : scaling_list.txt

#============ Lossless ================
TransquantBypassEnable        : 0
CUTransquantBypassFlagForce   : 0

### DO NOT ADD ANYTHING BELOW THIS LINE ###
"""


# ============================================================
# Helper functions
# ============================================================

def create_h264_config(qp):
    """Create H.264 encoder config file. Returns output directory path."""
    output_dir = os.path.join(H264_CODEC_DIR, f"QP{qp}_matched")
    os.makedirs(output_dir, exist_ok=True)
    cfg_path = os.path.join(output_dir, "encoder.cfg")
    with open(cfg_path, 'w') as f:
        f.write(H264_CONFIG_TEMPLATE.format(qp=qp))
    return output_dir


def create_h265_config(qp):
    """Create H.265 encoder config file. Returns output directory path."""
    output_dir = os.path.join(H265_CODEC_DIR, f"QP{qp}_matched")
    os.makedirs(output_dir, exist_ok=True)
    cfg_path = os.path.join(output_dir, "encoder.cfg")
    with open(cfg_path, 'w') as f:
        f.write(H265_CONFIG_TEMPLATE.format(qp=qp))
    return output_dir


def bitstream_exists(codec, qp):
    """Check if a valid bitstream already exists."""
    if codec == "h264":
        path = os.path.join(H264_CODEC_DIR, f"QP{qp}_matched", "encoded.264")
    else:
        path = os.path.join(H265_CODEC_DIR, f"QP{qp}_matched", "encoded.265")
    return os.path.exists(path) and os.path.getsize(path) > 100


def encode_h264(qp):
    """Encode H.264 for given QP. Returns True on success."""
    output_dir = create_h264_config(qp)
    cfg_path = os.path.join(output_dir, "encoder.cfg")

    print(f"  [H.264 QP{qp}] Encoding...")
    t0 = time.time()
    result = subprocess.run(
        [ENCODER_EXE, "-pf", cfg_path],
        cwd=output_dir,
        capture_output=True, text=True, timeout=3600
    )
    dt = time.time() - t0

    bs = os.path.join(output_dir, "encoded.264")
    if os.path.exists(bs) and os.path.getsize(bs) > 100:
        print(f"  [H.264 QP{qp}] OK  ({os.path.getsize(bs)//1024} KB, {dt:.0f}s)")
        return True
    else:
        print(f"  [H.264 QP{qp}] FAILED ({dt:.0f}s)")
        if result.stderr:
            print(f"    stderr: {result.stderr[:300]}")
        return False


def encode_h265(qp):
    """Encode H.265 for given QP. Returns True on success."""
    output_dir = create_h265_config(qp)
    cfg_path = os.path.join(output_dir, "encoder.cfg")

    print(f"  [H.265 QP{qp}] Encoding...")
    t0 = time.time()
    result = subprocess.run(
        [H265_ENCODER_EXE, "-c", cfg_path],
        cwd=output_dir,
        capture_output=True, text=True, timeout=3600
    )
    dt = time.time() - t0

    bs = os.path.join(output_dir, "encoded.265")
    if os.path.exists(bs) and os.path.getsize(bs) > 100:
        print(f"  [H.265 QP{qp}] OK  ({os.path.getsize(bs)//1024} KB, {dt:.0f}s)")
        return True
    else:
        print(f"  [H.265 QP{qp}] FAILED ({dt:.0f}s)")
        if result.stderr:
            print(f"    stderr: {result.stderr[:300]}")
        return False


# ============================================================
# Main
# ============================================================
def main():
    configs_only = "--configs-only" in sys.argv
    args = [a for a in sys.argv[1:] if not a.startswith("-")]

    # Determine which QP values to process
    if args:
        qp_list = [int(a) for a in args]
    else:
        qp_list = QP_VALUES

    print("=" * 60)
    print("Matched Encoding - Fair H.264 vs H.265 RD Comparison")
    print("=" * 60)
    print(f"  QP values : {qp_list}")
    print(f"  Video     : crew CIF 352x288, 300 frames, 30fps")
    print(f"  H.264     : GOP=4 HierB, IntraPeriod=32, Ref=4, CABAC")
    print(f"  H.265     : GOP=8 RA,     IntraPeriod=32, Ref=4, SAO+AMP")
    print()

    # Create all configs
    for qp in qp_list:
        create_h264_config(qp)
        create_h265_config(qp)
    print(f"Config files created for QP: {qp_list}")

    if configs_only:
        print("\n--configs-only: Skipping encoding.")
        print("\nTo encode manually:")
        for qp in qp_list:
            d264 = os.path.join(H264_CODEC_DIR, f"QP{qp}_matched")
            d265 = os.path.join(H265_CODEC_DIR, f"QP{qp}_matched")
            print(f"\n  # QP {qp}")
            print(f"  cd \"{d264}\" && \"{ENCODER_EXE}\" -pf encoder.cfg")
            print(f"  cd \"{d265}\" && \"{H265_ENCODER_EXE}\" -c encoder.cfg")
        return 0

    # Encode missing bitstreams
    print("\n--- H.264/AVC Encoding ---")
    for qp in qp_list:
        if bitstream_exists("h264", qp):
            print(f"  [H.264 QP{qp}] Already exists, skip")
        else:
            encode_h264(qp)

    print("\n--- H.265/HEVC Encoding ---")
    for qp in qp_list:
        if bitstream_exists("h265", qp):
            print(f"  [H.265 QP{qp}] Already exists, skip")
        else:
            encode_h265(qp)

    # Summary
    print("\n" + "=" * 60)
    print("STATUS")
    print("=" * 60)
    for qp in qp_list:
        h264_ok = "OK" if bitstream_exists("h264", qp) else "MISSING"
        h265_ok = "OK" if bitstream_exists("h265", qp) else "MISSING"
        print(f"  QP{qp:>2}  H.264: {h264_ok:<8} H.265: {h265_ok}")

    all_done = all(bitstream_exists("h264", q) and bitstream_exists("h265", q) for q in qp_list)
    if all_done:
        print("\nAll encodings complete! Run: python psnr_bitrate_graph.py")
    else:
        print("\nSome encodings missing. Re-run or encode manually.")
    return 0


if __name__ == "__main__":
    exit(main())
