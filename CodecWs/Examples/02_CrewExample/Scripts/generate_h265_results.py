#!/usr/bin/env python3
"""
H.265 Results Generator Script
Automatically generate results.txt files for all H.265 QP encodings
"""
import os
import glob
from config import *

def generate_h265_results(qp):
    """Generate results.txt for specific H.265 QP"""
    codec_dir = get_h265_codec_dir(qp)
    bitstream = get_h265_bitstream_file(qp)
    results_file = get_h265_results_file(qp)
    
    # Check if bitstream exists
    if not os.path.exists(bitstream):
        print(f"WARNING: H.265 bitstream not found for QP{qp}")
        return False
    
    # Get file sizes
    bitstream_size = os.path.getsize(bitstream)
    input_size = os.path.getsize(INPUT_VIDEO)
    
    # Calculate compression metrics
    compression_ratio = input_size / bitstream_size
    saved_percent = (1 - bitstream_size / input_size) * 100
    bitrate = (bitstream_size * 8 * VIDEO_FRAMERATE) / (VIDEO_FRAMES * 1000)
    
    # Create results content
    results_content = f"""HM H.265/HEVC - Crew CIF Example Results
============================================================

Video Settings:
  Resolution: {VIDEO_WIDTH}x{VIDEO_HEIGHT} (CIF)
  Frame rate: {VIDEO_FRAMERATE} fps
  Frames: {VIDEO_FRAMES}
  Duration: {VIDEO_FRAMES / VIDEO_FRAMERATE:.1f} seconds
  QP: {qp}

Compression Results:
  Original: {input_size / 1024 / 1024:.1f} MB
  Compressed: {bitstream_size / 1024:.1f} KB
  Ratio: {compression_ratio:.1f}:1
  Saved: {saved_percent:.1f}%
  Bitrate: {bitrate:.2f} kbps

"""
    
    # Write results file
    with open(results_file, 'w') as f:
        f.write(results_content)
    
    print(f"Generated results.txt for H.265 QP{qp}")
    print(f"  Bitstream: {bitstream_size/1024:.1f} KB")
    print(f"  Ratio: {compression_ratio:.1f}:1")
    print(f"  Bitrate: {bitrate:.2f} kbps")
    
    return True

def main():
    """Generate results for all H.265 QP values"""
    print()
    print("=" * 70)
    print("Generating H.265 Results Files for All QP Values")
    print("=" * 70)
    print()
    
    # Find all QP directories
    codec_base = H265_CODEC_DIR
    qp_dirs = sorted(glob.glob(os.path.join(codec_base, "QP*")))
    
    # Extract QP values
    qp_values = []
    for qp_dir in qp_dirs:
        qp_name = os.path.basename(qp_dir)
        if qp_name.startswith("QP"):
            try:
                qp = int(qp_name[2:])
                qp_values.append(qp)
            except ValueError:
                pass
    
    if not qp_values:
        print("No H.265 QP directories found!")
        return 1
    
    # Sort QP values
    qp_values.sort()
    
    print(f"Found H.265 QP values: {qp_values}")
    print()
    
    # Generate results for each QP
    success_count = 0
    for qp in qp_values:
        if generate_h265_results(qp):
            success_count += 1
        print()
    
    # Summary
    print("=" * 70)
    print(f"Successfully generated {success_count}/{len(qp_values)} H.265 results files")
    print("=" * 70)
    
    return 0

if __name__ == "__main__":
    exit(main())
