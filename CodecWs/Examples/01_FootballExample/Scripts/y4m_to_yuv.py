#!/usr/bin/env python3
"""
Y4M to YUV Converter - Generic version
Supports 420 and 422 input, outputs 420 for encoder compatibility.
"""
import os
import sys
import numpy as np
from config import *


def convert_422_to_420(cb_422, cr_422, width, height):
    """Convert 4:2:2 chroma to 4:2:0 by vertical subsampling."""
    cb_422 = cb_422.reshape(height, width // 2)
    cr_422 = cr_422.reshape(height, width // 2)
    
    # Average pairs of rows
    cb_420 = (cb_422[0::2, :].astype(np.uint16) + cb_422[1::2, :].astype(np.uint16)) // 2
    cr_420 = (cr_422[0::2, :].astype(np.uint16) + cr_422[1::2, :].astype(np.uint16)) // 2
    
    return cb_420.astype(np.uint8).flatten(), cr_420.astype(np.uint8).flatten()


def convert_y4m_to_yuv(y4m_path, yuv_path, max_frames=None):
    """
    Convert Y4M to raw YUV420 file.
    
    Args:
        y4m_path: Input Y4M file
        yuv_path: Output YUV file
        max_frames: Maximum frames to convert (None = all)
    """
    print(f"Converting: {os.path.basename(y4m_path)}")
    print(f"Output: {os.path.basename(yuv_path)}")
    
    with open(y4m_path, 'rb') as f_in:
        # Read header
        header = b''
        while True:
            c = f_in.read(1)
            if c == b'\n':
                break
            header += c
        
        header_str = header.decode('ascii')
        print(f"Y4M Header: {header_str}")
        
        # Detect chroma format
        is_422 = '422' in header_str or 'C422' in header_str
        chroma_type = '422' if is_422 else '420'
        print(f"Chroma: {chroma_type}" + (" -> converting to 420" if is_422 else ""))
        
        # Frame sizes
        w, h = VIDEO_WIDTH, VIDEO_HEIGHT
        y_size = w * h
        
        if is_422:
            uv_size_in = (w // 2) * h  # 422: half width, full height
        else:
            uv_size_in = (w // 2) * (h // 2)  # 420: half width, half height
        
        uv_size_out = (w // 2) * (h // 2)  # Always output 420
        
        frame_count = 0
        with open(yuv_path, 'wb') as f_out:
            while True:
                # Check frame limit
                if max_frames and frame_count >= max_frames:
                    break
                
                # Read FRAME header
                frame_header = b''
                while True:
                    c = f_in.read(1)
                    if not c:
                        break
                    if c == b'\n':
                        break
                    frame_header += c
                
                if not frame_header:
                    break
                
                # Read Y
                y_data = f_in.read(y_size)
                if len(y_data) != y_size:
                    break
                
                # Read U (Cb)
                u_data = f_in.read(uv_size_in)
                if len(u_data) != uv_size_in:
                    break
                
                # Read V (Cr)
                v_data = f_in.read(uv_size_in)
                if len(v_data) != uv_size_in:
                    break
                
                # Convert to numpy
                y = np.frombuffer(y_data, dtype=np.uint8)
                u = np.frombuffer(u_data, dtype=np.uint8)
                v = np.frombuffer(v_data, dtype=np.uint8)
                
                # Convert 422 to 420 if needed
                if is_422:
                    u, v = convert_422_to_420(u, v, w, h)
                
                # Write YUV420
                f_out.write(y.tobytes())
                f_out.write(u.tobytes())
                f_out.write(v.tobytes())
                
                frame_count += 1
                if frame_count % 50 == 0:
                    print(f"  Frame {frame_count}...")
        
        print(f"Converted {frame_count} frames")
        return frame_count


def main():
    if not Y4M_SOURCE or not os.path.exists(Y4M_SOURCE):
        print(f"ERROR: Y4M source not found: {Y4M_SOURCE}")
        return 1
    
    os.makedirs(YUV_VIDEO_DIR, exist_ok=True)
    
    # Optional frame limit from command line
    max_frames = int(sys.argv[1]) if len(sys.argv) > 1 else VIDEO_FRAMES
    
    frames = convert_y4m_to_yuv(Y4M_SOURCE, INPUT_VIDEO, max_frames)
    
    # Verify output
    expected_size = frames * VIDEO_WIDTH * VIDEO_HEIGHT * 3 // 2  # YUV420
    actual_size = os.path.getsize(INPUT_VIDEO)
    
    print(f"\nOutput: {INPUT_VIDEO}")
    print(f"Size: {actual_size} bytes ({actual_size // 1024} KB)")
    print(f"Frames: {frames}")
    print(f"Resolution: {VIDEO_WIDTH}x{VIDEO_HEIGHT}")
    
    if actual_size == expected_size:
        print("✓ Conversion successful!")
    else:
        print(f"⚠ Size mismatch: expected {expected_size}, got {actual_size}")
    
    return 0


if __name__ == "__main__":
    exit(main())
