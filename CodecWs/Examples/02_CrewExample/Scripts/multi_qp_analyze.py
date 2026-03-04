#!/usr/bin/env python3
"""
Multi-QP Analyzer
Analyze and compare encoding results across different QP values
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

def analyze_qp(qp):
    """Analyze specific QP encoding"""
    bitstream = get_bitstream_file(qp)
    decoded = DECODED_VIDEO.replace('.yuv', f'_qp{qp}.yuv')
    
    results = {
        'qp': qp,
        'bitstream_size': 0,
        'y_psnr': 0,
        'u_psnr': 0,
        'v_psnr': 0,
        'bitrate': 0
    }
    
    if not os.path.exists(bitstream):
        return None
    
    bitstream_size = os.path.getsize(bitstream)
    results['bitstream_size'] = bitstream_size
    
    # Calculate bitrate
    bitrate = (bitstream_size * 8 * VIDEO_FRAMERATE) / (VIDEO_FRAMES * 1000)
    results['bitrate'] = bitrate
    
    # Calculate PSNR if decoded file exists
    if os.path.exists(INPUT_VIDEO) and os.path.exists(decoded):
        frame_size = VIDEO_WIDTH * VIDEO_HEIGHT * 3 // 2
        y_size = VIDEO_WIDTH * VIDEO_HEIGHT
        uv_size = VIDEO_WIDTH * VIDEO_HEIGHT // 4
        
        with open(INPUT_VIDEO, 'rb') as f:
            original = f.read()
        
        with open(decoded, 'rb') as f:
            decoded_data = f.read()
        
        # Calculate PSNR for first frame
        orig_y = original[:y_size]
        dec_y = decoded_data[:y_size]
        y_psnr = calculate_psnr(orig_y, dec_y)
        
        orig_u = original[y_size:y_size + uv_size]
        dec_u = decoded_data[y_size:y_size + uv_size]
        u_psnr = calculate_psnr(orig_u, dec_u)
        
        orig_v = original[y_size + uv_size:y_size + 2 * uv_size]
        dec_v = decoded_data[y_size + uv_size:y_size + 2 * uv_size]
        v_psnr = calculate_psnr(orig_v, dec_v)
        
        if y_psnr and y_psnr != float('inf'):
            results['y_psnr'] = y_psnr
        if u_psnr and u_psnr != float('inf'):
            results['u_psnr'] = u_psnr
        if v_psnr and v_psnr != float('inf'):
            results['v_psnr'] = v_psnr
    
    return results

def main():
    print()
    print("=" * 70)
    print("Multi-QP Analysis - Crew CIF Example")
    print("=" * 70)
    print()
    
    qp_values = [22, 28, 35, 45]
    input_size = os.path.getsize(INPUT_VIDEO)
    
    # Analyze each QP
    results = []
    for qp in qp_values:
        result = analyze_qp(qp)
        if result:
            results.append(result)
        else:
            print(f"WARNING: No bitstream found for QP={qp}")
    
    # Display comparison table
    print("COMPRESSION & QUALITY COMPARISON")
    print("=" * 70)
    print(f"{'QP':<5} {'Size (KB)':<12} {'Ratio':<10} {'Bitrate':<12} {'Y PSNR (dB)':<12}")
    print("-" * 70)
    
    for result in results:
        qp = result['qp']
        size_kb = result['bitstream_size'] / 1024
        ratio = input_size / result['bitstream_size']
        bitrate = result['bitrate']
        y_psnr = result['y_psnr']
        
        y_psnr_str = f"{y_psnr:.2f}" if y_psnr > 0 else "N/A"
        print(f"{qp:<5} {size_kb:<11.1f} {ratio:<9.1f}x {bitrate:<11.1f} kbps {y_psnr_str:<11}")
    
    # Analysis
    print()
    print("=" * 70)
    print("QUALITY vs SIZE TRADEOFF")
    print("=" * 70)
    
    if len(results) >= 2:
        qp_low = results[0]  # QP22 (highest quality)
        qp_high = results[-1]  # QP45 (lowest quality)
        
        size_reduction = (1 - qp_high['bitstream_size'] / qp_low['bitstream_size']) * 100
        psnr_loss = qp_low['y_psnr'] - qp_high['y_psnr']
        
        print(f"From QP{qp_low['qp']} to QP{qp_high['qp']}:")
        print(f"  File size reduction:    {size_reduction:.1f}%")
        print(f"  Quality loss (Y PSNR):  {psnr_loss:.2f} dB")
        print(f"  Bitrate reduction:      {qp_high['bitrate']:.0f} → {qp_low['bitrate']:.0f} kbps")
    
    print()
    print("=" * 70)
    print("Decoded files saved as:")
    for qp in qp_values:
        decoded = DECODED_VIDEO.replace('.yuv', f'_qp{qp}.yuv')
        if os.path.exists(decoded):
            print(f"  decoded_qp{qp}.yuv")
    print("=" * 70)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
