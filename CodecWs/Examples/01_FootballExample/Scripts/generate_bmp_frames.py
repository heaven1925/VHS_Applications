#!/usr/bin/env python3
"""
Generate BMP Frame Comparisons for Football Example

Extracts specific frames from YUV files and converts them to BMP format
for visual comparison across different codec settings and QP levels.
"""
import os
import struct
from pathlib import Path

# Setup paths
example_dir = Path(r"C:\Users\atakan\Desktop\CodecWs\Examples\01_FootballExample")
h264_codec_dir = example_dir / "H264_Codec"
h265_codec_dir = example_dir / "H265_Codec"
yuv_video_dir = example_dir / "YUV_Video"
frame_comp_dir = h264_codec_dir / "frame_comparison"

# Video parameters (CIF 352x288)
WIDTH = 352
HEIGHT = 288
FRAME_NUM = 50  # Extract frame 50
FRAME_SIZE = WIDTH * HEIGHT * 3 // 2  # YUV420

def yuv420_to_rgb(y, u, v):
    """Convert YUV420 to RGB."""
    r = int(y + 1.402*(v-128))
    g = int(y - 0.344136*(u-128) - 0.714136*(v-128))
    b = int(y + 1.772*(u-128))
    return (max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)))

def extract_frame_yuv420(yuv_file, frame_index, width, height):
    """Extract a single frame from YUV420 file as RGB."""
    frame_size = width * height * 3 // 2
    
    with open(yuv_file, 'rb') as f:
        f.seek(frame_index * frame_size)
        frame_data = f.read(frame_size)
    
    if len(frame_data) < frame_size:
        return None
    
    # Parse YUV420
    y_size = width * height
    u_size = width * height // 4
    
    y_data = frame_data[:y_size]
    u_data = frame_data[y_size:y_size + u_size]
    v_data = frame_data[y_size + u_size:y_size + u_size + u_size]
    
    # Convert to RGB
    rgb = []
    for i in range(height):
        for j in range(width):
            y_idx = i * width + j
            uv_idx = (i // 2) * (width // 2) + (j // 2)
            
            y = y_data[y_idx]
            u = u_data[uv_idx]
            v = v_data[uv_idx]
            
            r, g, b = yuv420_to_rgb(y, u, v)
            rgb.append((b, g, r))  # BGR for BMP
    
    return rgb

def write_bmp(filename, rgb_data, width, height):
    """Write RGB data to BMP file."""
    # BMP Header
    file_size = 54 + width * height * 3
    
    with open(filename, 'wb') as f:
        # File header
        f.write(b'BM')
        f.write(struct.pack('<I', file_size))
        f.write(struct.pack('<I', 0))
        f.write(struct.pack('<I', 54))
        
        # Info header
        f.write(struct.pack('<I', 40))
        f.write(struct.pack('<i', width))
        f.write(struct.pack('<i', height))
        f.write(struct.pack('<H', 1))
        f.write(struct.pack('<H', 24))
        f.write(struct.pack('<I', 0))
        f.write(struct.pack('<I', width * height * 3))
        f.write(struct.pack('<i', 0))
        f.write(struct.pack('<i', 0))
        f.write(struct.pack('<I', 0))
        f.write(struct.pack('<I', 0))
        
        # Image data (bottom-up)
        for row in range(height - 1, -1, -1):
            for col in range(width):
                idx = row * width + col
                pixel = rgb_data[idx]
                f.write(bytes(pixel))

def generate_frames():
    """Generate BMP files for all QP levels."""
    os.makedirs(frame_comp_dir, exist_ok=True)
    
    # Original frame
    print(f"Extracting original frame {FRAME_NUM}...")
    input_yuv = yuv_video_dir / "input.yuv"
    if input_yuv.exists():
        rgb_data = extract_frame_yuv420(input_yuv, FRAME_NUM, WIDTH, HEIGHT)
        if rgb_data:
            out_file = frame_comp_dir / "h264_original_frame.bmp"
            write_bmp(out_file, rgb_data, WIDTH, HEIGHT)
            print(f"✓ Created: {out_file.name}")
    
    # H.264 frames for different QP levels
    qp_values = [7, 15, 22, 28, 35, 45, 55]
    
    for qp in qp_values:
        recon_yuv = h264_codec_dir / f"QP{qp}_matched" / "reconstructed.yuv"
        
        if recon_yuv.exists():
            print(f"Extracting H.264 QP{qp} reconstructed frame {FRAME_NUM}...")
            rgb_data = extract_frame_yuv420(recon_yuv, FRAME_NUM, WIDTH, HEIGHT)
            if rgb_data:
                out_file = frame_comp_dir / f"h264_QP{qp:02d}_frame{FRAME_NUM}.bmp"
                write_bmp(out_file, rgb_data, WIDTH, HEIGHT)
                print(f"✓ Created: {out_file.name}")
        else:
            print(f"⚠ File not found: {recon_yuv}")
    
    # H.265 frames for different QP levels
    h265_frame_comp_dir = h265_codec_dir / "frame_comparison"
    os.makedirs(h265_frame_comp_dir, exist_ok=True)
    
    # H.265 frames for different QP levels
    h265_qp_values = [7, 15, 22, 28, 35, 45, 51]
    
    for qp in h265_qp_values:
        recon_yuv = h265_codec_dir / f"QP{qp}_matched" / "reconstructed.yuv"
        
        if recon_yuv.exists():
            print(f"Extracting H.265 QP{qp} reconstructed frame {FRAME_NUM}...")
            rgb_data = extract_frame_yuv420(recon_yuv, FRAME_NUM, WIDTH, HEIGHT)
            if rgb_data:
                out_file = h265_frame_comp_dir / f"h265_QP{qp:02d}_frame{FRAME_NUM}.bmp"
                write_bmp(out_file, rgb_data, WIDTH, HEIGHT)
                print(f"✓ Created: {out_file.name}")
        else:
            print(f"⚠ File not found: {recon_yuv}")
    
    print(f"\n✓ All H.264 frames in: {frame_comp_dir}")
    print(f"✓ All H.265 frames in: {h265_frame_comp_dir}")

if __name__ == "__main__":
    print("="*70)
    print("Generate BMP Frame Comparisons - Football Example")
    print("="*70)
    generate_frames()
    print("="*70)
