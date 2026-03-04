#!/usr/bin/env python3
"""
JSVM H.264/AVC Crew CIF Example
Run complete pipeline: extract Y4M, encode, decode, analyze

Usage:
    python run_all.py          - Run complete pipeline
    python y4m_to_yuv.py       - Extract Y4M to YUV only
    python run_codec.py        - Run encoder and decoder
    python analyze.py          - Analyze results
    python view_video.py       - View frames as images
"""
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import *

def main():
    print()
    print("=" * 60)
    print("JSVM H.264/AVC - Crew CIF Example")
    print("=" * 60)
    print()
    print(f"Video: CIF ({VIDEO_WIDTH}x{VIDEO_HEIGHT}) @ {VIDEO_FRAMERATE} fps")
    print(f"Frames: {VIDEO_FRAMES} ({VIDEO_FRAMES/VIDEO_FRAMERATE:.1f} seconds)")
    print(f"QP: {QP}")
    print()
    
    # Step 1: Convert Y4M to YUV and encode/decode
    print("Running codec pipeline...")
    print("-" * 40)
    import run_codec
    if run_codec.main() != 0:
        print("Codec failed!")
        return 1
    print()
    
    # Step 2: Analyze results
    print("Analyzing results...")
    print("-" * 40)
    import analyze
    analyze.main()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
