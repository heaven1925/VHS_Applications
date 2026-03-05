#!/usr/bin/env python3
"""
Matched Encoder - Generic version
Fair H.264 vs H.265 Rate-Distortion Comparison

Usage:
    python matched_encode.py                  # Create configs + encode all QPs
    python matched_encode.py --configs-only   # Only create config files
    python matched_encode.py 22 35            # Encode specific QP values
"""
import os
import sys
import subprocess
import time
from config import *

QP_VALUES = [7, 15, 22, 28, 35, 45, 55]


def get_h264_config(qp):
    """Generate H.264 encoder config content."""
    return f"""# JSVM Configuration - Matched RD Comparison
# {EXAMPLE_NAME} - Hierarchical B (GOP=4), IntraPeriod=32

#====================== GENERAL ================================================
AVCMode                 1
InputFile               ..\\..\\YUV_Video\\input.yuv
OutputFile              encoded.264
ReconFile               reconstructed.yuv
SourceWidth             {VIDEO_WIDTH}
SourceHeight            {VIDEO_HEIGHT}
FrameRate               {VIDEO_FRAMERATE}
FramesToBeEncoded       {VIDEO_FRAMES}

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

# GOP=4 Hierarchical B with I-refresh every 32 frames
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


def get_h265_config(qp):
    """Generate H.265 encoder config content."""
    return f"""#======== File I/O =====================
InputFile                     : ..\\..\\YUV_Video\\input.yuv
BitstreamFile                 : encoded.265
ReconFile                     : reconstructed.yuv

#======== Profile ================
Profile                       : main

#======== Input ================
InputBitDepth                 : 8
InputChromaFormat             : 420
FrameRate                     : {int(VIDEO_FRAMERATE)}
FrameSkip                     : 0
SourceWidth                   : {VIDEO_WIDTH}
SourceHeight                  : {VIDEO_HEIGHT}
FramesToBeEncoded             : {VIDEO_FRAMES}

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


def create_config(qp, codec):
    """Create encoder config file."""
    output_dir = get_matched_dir(qp, codec)
    os.makedirs(output_dir, exist_ok=True)
    cfg_path = os.path.join(output_dir, "encoder.cfg")
    
    content = get_h264_config(qp) if codec == 'h264' else get_h265_config(qp)
    with open(cfg_path, 'w') as f:
        f.write(content)
    return output_dir


def bitstream_exists(qp, codec):
    """Check if bitstream exists."""
    ext = "264" if codec == 'h264' else "265"
    path = os.path.join(get_matched_dir(qp, codec), f"encoded.{ext}")
    return os.path.exists(path) and os.path.getsize(path) > 100


def encode(qp, codec):
    """Run encoding."""
    output_dir = create_config(qp, codec)
    cfg_path = os.path.join(output_dir, "encoder.cfg")
    
    if codec == 'h264':
        cmd = [ENCODER_EXE, "-pf", cfg_path]
        ext = "264"
    else:
        cmd = [H265_ENCODER_EXE, "-c", cfg_path]
        ext = "265"
    
    print(f"  [{codec.upper()} QP{qp}] Encoding...")
    t0 = time.time()
    
    try:
        result = subprocess.run(cmd, cwd=output_dir, capture_output=True, text=True, timeout=3600)
        dt = time.time() - t0
        
        bs = os.path.join(output_dir, f"encoded.{ext}")
        if os.path.exists(bs) and os.path.getsize(bs) > 100:
            print(f"  [{codec.upper()} QP{qp}] OK ({os.path.getsize(bs)//1024} KB, {dt:.0f}s)")
            return True
        else:
            print(f"  [{codec.upper()} QP{qp}] FAILED ({dt:.0f}s)")
            return False
    except Exception as e:
        print(f"  [{codec.upper()} QP{qp}] ERROR: {e}")
        return False


def main():
    configs_only = "--configs-only" in sys.argv
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    qp_list = [int(a) for a in args] if args else QP_VALUES
    
    print("=" * 60)
    print(f"Matched Encoding - {EXAMPLE_NAME}")
    print("=" * 60)
    print(f"  QP values : {qp_list}")
    print(f"  Video     : {VIDEO_WIDTH}x{VIDEO_HEIGHT}, {VIDEO_FRAMES} frames, {VIDEO_FRAMERATE} fps")
    print(f"  H.264     : GOP=4 HierB, IntraPeriod=32, Ref=4, CABAC")
    print(f"  H.265     : GOP=8 RA, IntraPeriod=32, Ref=4, SAO+AMP")
    print()
    
    # Create configs
    for qp in qp_list:
        create_config(qp, 'h264')
        create_config(qp, 'h265')
    print(f"Config files created for QP: {qp_list}")
    
    if configs_only:
        print("\n--configs-only: Skipping encoding.")
        print("\nTo encode manually:")
        for qp in qp_list:
            d264 = get_matched_dir(qp, 'h264')
            d265 = get_matched_dir(qp, 'h265')
            print(f"\n  # QP {qp}")
            print(f"  cd \"{d264}\"; & \"{ENCODER_EXE}\" -pf encoder.cfg")
            print(f"  cd \"{d265}\"; & \"{H265_ENCODER_EXE}\" -c encoder.cfg")
        return 0
    
    # Encode
    print("\n--- H.264/AVC Encoding ---")
    for qp in qp_list:
        if bitstream_exists(qp, 'h264'):
            print(f"  [H264 QP{qp}] Already exists, skip")
        else:
            encode(qp, 'h264')
    
    print("\n--- H.265/HEVC Encoding ---")
    for qp in qp_list:
        if bitstream_exists(qp, 'h265'):
            print(f"  [H265 QP{qp}] Already exists, skip")
        else:
            encode(qp, 'h265')
    
    # Summary
    print("\n" + "=" * 60)
    print("STATUS")
    print("=" * 60)
    for qp in qp_list:
        h264_ok = "OK" if bitstream_exists(qp, 'h264') else "MISSING"
        h265_ok = "OK" if bitstream_exists(qp, 'h265') else "MISSING"
        print(f"  QP{qp:>2}  H.264: {h264_ok:<8} H.265: {h265_ok}")
    
    all_done = all(bitstream_exists(q, c) for q in qp_list for c in ['h264', 'h265'])
    if all_done:
        print("\nAll encodings complete! Run: python psnr_bitrate_graph.py")
    
    return 0


if __name__ == "__main__":
    exit(main())
