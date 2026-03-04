#!/usr/bin/env python3
"""
Run JSVM Encoder and Decoder - Crew CIF Example
Converts Y4M to YUV, encodes, and decodes
"""
import subprocess
import os
import sys
import time
from config import *

def convert_y4m_to_yuv():
    """Convert Y4M file to raw YUV"""
    print("=" * 60)
    print("STEP 1: Converting Y4M to YUV")
    print("=" * 60)
    
    if not os.path.exists(Y4M_SOURCE):
        print(f"ERROR: Y4M file not found: {Y4M_SOURCE}")
        return False
    
    print(f"Source: {os.path.basename(Y4M_SOURCE)}")
    print(f"Output: {os.path.basename(INPUT_VIDEO)}")
    print(f"Frames to extract: {VIDEO_FRAMES}")
    print()
    
    import y4m_to_yuv
    
    try:
        info = y4m_to_yuv.convert_y4m_to_yuv(Y4M_SOURCE, INPUT_VIDEO, max_frames=VIDEO_FRAMES)
        print()
        return True
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def run_encoder():
    """Run H.264/AVC encoder"""
    print("=" * 60)
    print("STEP 2: Encoding Video")
    print("=" * 60)
    
    if not os.path.exists(INPUT_VIDEO):
        print(f"ERROR: Input video not found: {INPUT_VIDEO}")
        return False
    
    if not os.path.exists(ENCODER_EXE):
        print(f"ERROR: Encoder not found: {ENCODER_EXE}")
        return False
    
    input_size = os.path.getsize(INPUT_VIDEO)
    print(f"Input: {os.path.basename(INPUT_VIDEO)} ({input_size/1024/1024:.1f} MB)")
    print(f"Config: {os.path.basename(ENCODER_CONFIG)}")
    print()
    
    cmd = [ENCODER_EXE, '-pf', ENCODER_CONFIG]
    
    start_time = time.time()
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=CODEC_DIR)
    encode_time = time.time() - start_time
    
    print("Encoder Output:")
    print("-" * 40)
    if result.stdout:
        # Print first and last 20 lines
        lines = result.stdout.strip().split('\n')
        for line in lines[:5]:
            print(line)
        if len(lines) > 10:
            print("...")
        for line in lines[-5:]:
            print(line)
    
    if os.path.exists(BITSTREAM_FILE):
        bitstream_size = os.path.getsize(BITSTREAM_FILE)
        compression = (1 - bitstream_size / input_size) * 100
        bitrate = (bitstream_size * 8 * VIDEO_FRAMERATE) / (VIDEO_FRAMES * 1000)
        
        print("-" * 40)
        print(f"Encoding completed in {encode_time:.2f} seconds")
        print(f"Bitstream: {os.path.basename(BITSTREAM_FILE)} ({bitstream_size/1024:.1f} KB)")
        print(f"Compression ratio: {compression:.1f}%")
        print(f"Bitrate: {bitrate:.2f} kbps")
        return True
    else:
        print("ERROR: Bitstream file not created!")
        return False

def run_decoder():
    """Run H.264/AVC decoder"""
    print()
    print("=" * 60)
    print("STEP 3: Decoding Video")
    print("=" * 60)
    
    if not os.path.exists(BITSTREAM_FILE):
        print(f"ERROR: Bitstream not found: {BITSTREAM_FILE}")
        return False
    
    if not os.path.exists(DECODER_EXE):
        print(f"ERROR: Decoder not found: {DECODER_EXE}")
        return False
    
    bitstream_size = os.path.getsize(BITSTREAM_FILE)
    print(f"Input: {os.path.basename(BITSTREAM_FILE)} ({bitstream_size/1024:.1f} KB)")
    print()
    
    cmd = [DECODER_EXE, BITSTREAM_FILE, DECODED_VIDEO]
    
    start_time = time.time()
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=CODEC_DIR)
    decode_time = time.time() - start_time
    
    print("Decoder Output:")
    print("-" * 40)
    if result.stdout:
        # Print summary (find "frames decoded" line)
        lines = result.stdout.strip().split('\n')
        for line in lines[-10:]:
            if line.strip():
                print(line)
    
    if os.path.exists(DECODED_VIDEO):
        decoded_size = os.path.getsize(DECODED_VIDEO)
        print("-" * 40)
        print(f"Decoding completed in {decode_time:.2f} seconds")
        print(f"Decoded: {os.path.basename(DECODED_VIDEO)} ({decoded_size/1024/1024:.1f} MB)")
        return True
    else:
        print("ERROR: Decoded file not created!")
        return False

def main():
    print()
    print("JSVM H.264/AVC - Crew CIF Example")
    print("=" * 60)
    print(f"Example: 02_CrewExample")
    print(f"Video: CIF ({VIDEO_WIDTH}x{VIDEO_HEIGHT}) @ {VIDEO_FRAMERATE} fps")
    print(f"Frames: {VIDEO_FRAMES}")
    print(f"QP: {QP}")
    print()
    
    # Step 1: Convert Y4M to YUV
    if not os.path.exists(INPUT_VIDEO):
        if not convert_y4m_to_yuv():
            return 1
    else:
        print(f"YUV file already exists, skipping conversion")
        print()
    
    # Step 2: Run encoder
    if not run_encoder():
        return 1
    
    # Step 3: Run decoder
    if not run_decoder():
        return 1
    
    print()
    print("=" * 60)
    print("COMPLETED SUCCESSFULLY")
    print("=" * 60)
    print(f"Now run 'python analyze.py' to view detailed results.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
