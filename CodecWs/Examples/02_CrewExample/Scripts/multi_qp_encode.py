#!/usr/bin/env python3
"""
Multi-QP Encoder
Encode same video with different QP values for comparison
"""
import subprocess
import os
import sys
import time
from config import *

def encode_qp(qp):
    """Encode video with specific QP value"""
    codec_dir = get_codec_dir(qp)
    config_file = get_encoder_config(qp)
    bitstream = get_bitstream_file(qp)
    
    if not os.path.exists(config_file):
        print(f"ERROR: Config file not found: {config_file}")
        return False
    
    print("=" * 60)
    print(f"ENCODING with QP={qp}")
    print("=" * 60)
    print(f"Config: {os.path.basename(config_file)}")
    print(f"Output: {os.path.basename(bitstream)}")
    print()
    
    cmd = [ENCODER_EXE, '-pf', config_file]
    
    start_time = time.time()
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=codec_dir)
    encode_time = time.time() - start_time
    
    # Print last few lines of output
    if result.stdout:
        lines = result.stdout.strip().split('\n')
        for line in lines[-5:]:
            if line.strip():
                print(line)
    
    if result.stderr and 'error' in result.stderr.lower():
        print(f"ERROR: {result.stderr}")
        return False
    
    if os.path.exists(bitstream):
        bitstream_size = os.path.getsize(bitstream)
        input_size = os.path.getsize(INPUT_VIDEO)
        compression = (1 - bitstream_size / input_size) * 100
        bitrate = (bitstream_size * 8 * VIDEO_FRAMERATE) / (VIDEO_FRAMES * 1000)
        
        print()
        print(f"Encoding completed in {encode_time:.2f} seconds")
        print(f"Bitstream: {bitstream_size/1024:.1f} KB")
        print(f"Compression: {compression:.1f}%")
        print(f"Bitrate: {bitrate:.2f} kbps")
        return True
    else:
        print(f"ERROR: Bitstream not created!")
        return False

def decode_qp(qp):
    """Decode bitstream for QP"""
    bitstream = get_bitstream_file(qp)
    decoded = DECODED_VIDEO.replace('.yuv', f'_qp{qp}.yuv')
    
    if not os.path.exists(bitstream):
        print(f"ERROR: Bitstream not found: {bitstream}")
        return False
    
    print()
    print(f"Decoding QP={qp}...")
    cmd = [DECODER_EXE, bitstream, decoded]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if os.path.exists(decoded):
        decoded_size = os.path.getsize(decoded)
        print(f"Decoded: {decoded_size/1024/1024:.1f} MB")
        return True
    else:
        print(f"ERROR: Decoded file not created!")
        return False

def main():
    ensure_dirs()
    
    qp_values = [22, 28, 35, 45]  # Quality range: high to low
    
    print()
    print("=" * 60)
    print("JSVM Multi-QP Encoder - Crew CIF")
    print("=" * 60)
    print(f"Video: {VIDEO_WIDTH}x{VIDEO_HEIGHT} @ {VIDEO_FRAMERATE} fps")
    print(f"Frames: {VIDEO_FRAMES}")
    print(f"QP Values: {qp_values}")
    print()
    
    # Check input
    if not os.path.exists(INPUT_VIDEO):
        print(f"ERROR: Input video not found: {INPUT_VIDEO}")
        return 1
    
    # Encode with each QP
    results = {}
    for qp in qp_values:
        if not encode_qp(qp):
            print(f"ERROR: Encoding QP={qp} failed")
            return 1
        results[qp] = get_bitstream_file(qp)
    
    # Decode each
    print()
    print("=" * 60)
    print("DECODING ALL BITSTREAMS")
    print("=" * 60)
    for qp in qp_values:
        if not decode_qp(qp):
            print(f"ERROR: Decoding QP={qp} failed")
            return 1
    
    # Summary
    print()
    print("=" * 60)
    print("COMPRESSION SUMMARY")
    print("=" * 60)
    input_size = os.path.getsize(INPUT_VIDEO)
    
    print(f"{'QP':<5} {'Size (KB)':<12} {'Ratio':<10} {'Bitrate':<12}")
    print("-" * 40)
    
    for qp in qp_values:
        bitstream = get_bitstream_file(qp)
        if os.path.exists(bitstream):
            bitstream_size = os.path.getsize(bitstream)
            ratio = input_size / bitstream_size
            bitrate = (bitstream_size * 8 * VIDEO_FRAMERATE) / (VIDEO_FRAMES * 1000)
            print(f"{qp:<5} {bitstream_size/1024:<11.1f} {ratio:<9.1f}x {bitrate:<11.1f} kbps")
    
    print()
    print("=" * 60)
    print("Encoding complete! Run 'python multi_qp_analyze.py' to analyze results.")
    print("=" * 60)
    return 0

if __name__ == "__main__":
    sys.exit(main())
