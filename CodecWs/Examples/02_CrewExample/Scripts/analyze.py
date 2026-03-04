#!/usr/bin/env python3
"""
Analyze Codec Results - Crew CIF Example
Detailed analysis of encoding results
"""
import os
import sys
import math
from config import *

def calculate_psnr(original_bytes, decoded_bytes):
    """Calculate Peak Signal-to-Noise Ratio"""
    if len(original_bytes) != len(decoded_bytes):
        return None
    
    mse = 0.0
    for i in range(len(original_bytes)):
        diff = original_bytes[i] - decoded_bytes[i]
        mse += diff * diff
    
    mse /= len(original_bytes)
    
    if mse == 0:
        return float('inf')
    
    max_pixel = 255.0
    psnr = 10 * math.log10((max_pixel ** 2) / mse)
    return psnr

def analyze_quality_metrics():
    """Analyze quality metrics per frame"""
    print("=" * 60)
    print("QUALITY METRICS")
    print("=" * 60)
    
    if not os.path.exists(INPUT_VIDEO) or not os.path.exists(DECODED_VIDEO):
        print("Required files not found")
        return
    
    frame_size = VIDEO_WIDTH * VIDEO_HEIGHT * 3 // 2
    y_size = VIDEO_WIDTH * VIDEO_HEIGHT
    uv_size = VIDEO_WIDTH * VIDEO_HEIGHT // 4
    
    with open(INPUT_VIDEO, 'rb') as f:
        original = f.read()
    
    with open(DECODED_VIDEO, 'rb') as f:
        decoded = f.read()
    
    original_frames = len(original) // frame_size
    decoded_frames = len(decoded) // frame_size
    
    print(f"Original: {original_frames} frames")
    print(f"Decoded:  {decoded_frames} frames")
    print()
    
    frames_to_compare = min(original_frames, decoded_frames)
    
    # Calculate PSNR for sample frames
    sample_frames = [0, 10, 50, 100, 200, 299]
    sample_frames = [f for f in sample_frames if f < frames_to_compare]
    
    print("Sample Frame PSNR Analysis:")
    print("-" * 50)
    print(f"{'Frame':>6} {'Y PSNR':>10} {'U PSNR':>10} {'V PSNR':>10} {'Avg':>10}")
    print("-" * 50)
    
    total_y = 0
    total_u = 0
    total_v = 0
    count = 0
    
    for frame_idx in range(frames_to_compare):
        orig_offset = frame_idx * frame_size
        dec_offset = frame_idx * frame_size
        
        orig_y = original[orig_offset:orig_offset + y_size]
        dec_y = decoded[dec_offset:dec_offset + y_size]
        y_psnr = calculate_psnr(orig_y, dec_y)
        
        orig_u = original[orig_offset + y_size:orig_offset + y_size + uv_size]
        dec_u = decoded[dec_offset + y_size:dec_offset + y_size + uv_size]
        u_psnr = calculate_psnr(orig_u, dec_u)
        
        orig_v = original[orig_offset + y_size + uv_size:orig_offset + frame_size]
        dec_v = decoded[dec_offset + y_size + uv_size:dec_offset + frame_size]
        v_psnr = calculate_psnr(orig_v, dec_v)
        
        if y_psnr: total_y += y_psnr
        if u_psnr: total_u += u_psnr
        if v_psnr: total_v += v_psnr
        count += 1
        
        if frame_idx in sample_frames:
            avg = (y_psnr + u_psnr + v_psnr) / 3 if y_psnr and u_psnr and v_psnr else 0
            y_str = f"{y_psnr:.2f}" if y_psnr and y_psnr != float('inf') else "inf"
            u_str = f"{u_psnr:.2f}" if u_psnr and u_psnr != float('inf') else "inf"
            v_str = f"{v_psnr:.2f}" if v_psnr and v_psnr != float('inf') else "inf"
            avg_str = f"{avg:.2f}" if avg > 0 else "-"
            print(f"{frame_idx:>6} {y_str:>10} {u_str:>10} {v_str:>10} {avg_str:>10}")
    
    print("-" * 50)
    
    avg_y = total_y / count if count > 0 else 0
    avg_u = total_u / count if count > 0 else 0
    avg_v = total_v / count if count > 0 else 0
    overall_avg = (avg_y + avg_u + avg_v) / 3
    
    print(f"{'AVG':>6} {avg_y:>9.2f}  {avg_u:>9.2f}  {avg_v:>9.2f}  {overall_avg:>9.2f}")
    print()

def show_file_summary():
    """Show summary of all generated files"""
    print("=" * 60)
    print("FILE SUMMARY")
    print("=" * 60)
    
    files = [
        ("Source Y4M", Y4M_SOURCE),
        ("Extracted YUV", INPUT_VIDEO),
        ("Bitstream", BITSTREAM_FILE),
        ("Decoded YUV", DECODED_VIDEO),
        ("Reconstructed", os.path.join(YUV_VIDEO_DIR, "reconstructed.yuv")),
    ]
    
    print(f"{'File':<25} {'Size':>15} {'Status':<10}")
    print("-" * 50)
    
    for name, path in files:
        if os.path.exists(path):
            size = os.path.getsize(path)
            if size > 1024*1024:
                size_str = f"{size/1024/1024:.1f} MB"
            else:
                size_str = f"{size/1024:.1f} KB"
            print(f"{name:<25} {size_str:>15} {'OK':<10}")
        else:
            print(f"{name:<25} {'--':>15} {'Missing':<10}")

def calculate_compression_stats():
    """Calculate compression statistics"""
    print()
    print("=" * 60)
    print("COMPRESSION STATISTICS")
    print("=" * 60)
    
    if not os.path.exists(INPUT_VIDEO) or not os.path.exists(BITSTREAM_FILE):
        print("Required files not found.")
        return
    
    input_size = os.path.getsize(INPUT_VIDEO)
    bitstream_size = os.path.getsize(BITSTREAM_FILE)
    
    compression_ratio = input_size / bitstream_size if bitstream_size > 0 else 0
    compression_percent = (1 - bitstream_size / input_size) * 100
    bitrate = (bitstream_size * 8 * VIDEO_FRAMERATE) / (VIDEO_FRAMES * 1000)
    bits_per_pixel = (bitstream_size * 8) / (VIDEO_WIDTH * VIDEO_HEIGHT * VIDEO_FRAMES)
    
    print(f"Original size:       {input_size:>15,} bytes ({input_size/1024/1024:.1f} MB)")
    print(f"Compressed size:     {bitstream_size:>15,} bytes ({bitstream_size/1024:.1f} KB)")
    print(f"Compression ratio:   {compression_ratio:>15.1f}:1")
    print(f"Space saved:         {compression_percent:>14.1f}%")
    print(f"Bitrate:             {bitrate:>15.2f} kbps")
    print(f"Bits per pixel:      {bits_per_pixel:>15.4f}")

def save_results():
    """Save analysis results to file"""
    print()
    print("=" * 60)
    print(f"Saving results to: {os.path.basename(RESULTS_FILE)}")
    
    with open(RESULTS_FILE, 'w') as f:
        f.write("JSVM H.264/AVC - Crew CIF Example Results\n")
        f.write("=" * 60 + "\n\n")
        
        f.write("Video Settings:\n")
        f.write(f"  Resolution: {VIDEO_WIDTH}x{VIDEO_HEIGHT} (CIF)\n")
        f.write(f"  Frame rate: {VIDEO_FRAMERATE} fps\n")
        f.write(f"  Frames: {VIDEO_FRAMES}\n")
        f.write(f"  Duration: {VIDEO_FRAMES / VIDEO_FRAMERATE:.1f} seconds\n")
        f.write(f"  QP: {QP}\n\n")
        
        if os.path.exists(INPUT_VIDEO) and os.path.exists(BITSTREAM_FILE):
            input_size = os.path.getsize(INPUT_VIDEO)
            bitstream_size = os.path.getsize(BITSTREAM_FILE)
            
            f.write("Compression Results:\n")
            f.write(f"  Original: {input_size/1024/1024:.1f} MB\n")
            f.write(f"  Compressed: {bitstream_size/1024:.1f} KB\n")
            f.write(f"  Ratio: {input_size/bitstream_size:.1f}:1\n")
            f.write(f"  Saved: {(1-bitstream_size/input_size)*100:.1f}%\n")
            f.write(f"  Bitrate: {(bitstream_size*8*VIDEO_FRAMERATE)/(VIDEO_FRAMES*1000):.2f} kbps\n")
    
    print("Results saved.")

def main():
    print()
    print("JSVM Codec Results Analyzer - Crew CIF")
    print("=" * 60)
    print(f"Example: 02_CrewExample")
    print(f"Resolution: CIF ({VIDEO_WIDTH}x{VIDEO_HEIGHT})")
    print()
    
    show_file_summary()
    calculate_compression_stats()
    analyze_quality_metrics()
    save_results()
    
    print()
    print("=" * 60)
    print("Analysis complete!")
    print("=" * 60)

if __name__ == "__main__":
    main()
