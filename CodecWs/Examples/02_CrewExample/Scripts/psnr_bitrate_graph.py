#!/usr/bin/env python3
"""
PSNR vs Bitrate Graph Generator
Calculates PSNR for each QP value and plots PSNR(y) vs Bitrate(x) graph
"""
import os
import glob
import math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from config import *

def calculate_mse(original_data, reconstructed_data):
    """
    Calculate Mean Squared Error (MSE)
    MSE = (1/N) * Σ_{i=1..N} ( I_i - I~_i )^2
    
    Args:
        original_data: Original pixel values (numpy array)
        reconstructed_data: Reconstructed pixel values (numpy array)
    
    Returns:
        MSE value
    """
    if len(original_data) != len(reconstructed_data):
        raise ValueError("Original and reconstructed data sizes do not match!")
    
    N = len(original_data)
    diff = original_data.astype(np.float64) - reconstructed_data.astype(np.float64)
    mse = np.sum(diff ** 2) / N
    
    return mse

def calculate_psnr(original_data, reconstructed_data, bit_depth=8):
    """
    Calculate Peak Signal-to-Noise Ratio (PSNR) in dB
    PSNR = 10 * log10( (I_max^2) / MSE )
    
    Alternative equivalent:
    PSNR = 20 * log10( I_max / sqrt(MSE) )
    
    Args:
        original_data: Original pixel values (numpy array)
        reconstructed_data: Reconstructed pixel values (numpy array)
        bit_depth: Bit depth (8, 10, or 12)
    
    Returns:
        PSNR value in dB
    """
    # I_max: maximum pixel value based on bit depth
    if bit_depth == 8:
        I_max = 255
    elif bit_depth == 10:
        I_max = 1023
    elif bit_depth == 12:
        I_max = 4095
    else:
        I_max = (2 ** bit_depth) - 1
    
    mse = calculate_mse(original_data, reconstructed_data)
    
    if mse == 0:
        return float('inf')  # Perfect match
    
    # PSNR = 10 * log10( (I_max^2) / MSE )
    psnr = 10 * math.log10((I_max ** 2) / mse)
    
    return psnr

def read_yuv_y_component(filepath, width, height, num_frames=None):
    """
    Read Y component from YUV420 file
    
    Args:
        filepath: Path to YUV file
        width: Video width
        height: Video height
        num_frames: Number of frames to read (None for all)
    
    Returns:
        Y component data as numpy array
    """
    frame_size_y = width * height
    frame_size_uv = (width // 2) * (height // 2)
    frame_size_yuv = frame_size_y + 2 * frame_size_uv  # YUV420
    
    file_size = os.path.getsize(filepath)
    total_frames = file_size // frame_size_yuv
    
    if num_frames is None:
        num_frames = total_frames
    else:
        num_frames = min(num_frames, total_frames)
    
    y_data = []
    
    with open(filepath, 'rb') as f:
        for i in range(num_frames):
            # Read Y component
            y_frame = np.frombuffer(f.read(frame_size_y), dtype=np.uint8)
            y_data.append(y_frame)
            # Skip U and V components
            f.seek(2 * frame_size_uv, 1)
    
    return np.concatenate(y_data)

def analyze_qp(qp, codec='h264'):
    """
    Analyze PSNR and bitrate for specific QP value
    
    Args:
        qp: QP value
        codec: 'h264' or 'h265'
    
    Returns:
        Dictionary with psnr and bitrate
    """
    if codec == 'h264':
        codec_dir = get_codec_dir(qp)
        bitstream = get_bitstream_file(qp)
    else:  # h265
        codec_dir = get_h265_codec_dir(qp)
        bitstream = get_h265_bitstream_file(qp)
    
    reconstructed = os.path.join(codec_dir, "reconstructed.yuv")
    
    if not os.path.exists(bitstream):
        print(f"WARNING: Bitstream not found for {codec.upper()} QP{qp}")
        return None
    
    if not os.path.exists(reconstructed):
        print(f"WARNING: Reconstructed file not found for {codec.upper()} QP{qp}")
        return None
    
    # Calculate bitrate: Bitrate = bitstream_size_bits / duration_seconds
    bitstream_size_bits = os.path.getsize(bitstream) * 8
    duration_seconds = VIDEO_FRAMES / VIDEO_FRAMERATE
    bitrate = bitstream_size_bits / duration_seconds / 1000  # kbps
    
    # Read Y components
    print(f"  Reading original Y component...")
    original_y = read_yuv_y_component(INPUT_VIDEO, VIDEO_WIDTH, VIDEO_HEIGHT, VIDEO_FRAMES)
    
    print(f"  Reading reconstructed Y component...")
    reconstructed_y = read_yuv_y_component(reconstructed, VIDEO_WIDTH, VIDEO_HEIGHT, VIDEO_FRAMES)
    
    # Calculate PSNR
    print(f"  Calculating PSNR...")
    psnr = calculate_psnr(original_y, reconstructed_y, bit_depth=8)
    
    return {
        'qp': qp,
        'psnr': psnr,
        'bitrate': bitrate
    }

def load_gop_results():
    """
    Load GOP structure comparison results from gop_results.txt
    
    Returns:
        List of dicts with name, psnr, bitrate, time keys (or empty list)
    """
    results_file = os.path.join(H264_CODEC_DIR, "gop_results.txt")
    if not os.path.exists(results_file):
        return []
    
    gop_results = []
    with open(results_file, 'r') as f:
        header = f.readline()  # skip header
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split(',')
            if len(parts) >= 5:
                name = parts[0].replace("QP35_", "")  # e.g. "GOP1_IPP"
                gop_results.append({
                    'name': name,
                    'psnr': float(parts[3]),
                    'bitrate': float(parts[4]),
                    'time': float(parts[5]) if len(parts) > 5 else 0
                })
    return gop_results


def plot_psnr_vs_bitrate(h264_results, h265_results=None, output_file="psnr_vs_bitrate.png"):
    """
    Plot PSNR vs Bitrate graph for QP comparison (H.264 vs H.265 only)
    
    Args:
        h264_results: List of H.264 analysis results
        h265_results: List of H.265 analysis results (optional)
        output_file: Output image filename
    """
    fig, ax = plt.subplots(figsize=(14, 10))
    
    # Plot H.264 results
    if h264_results:
        qp_values_h264 = [r['qp'] for r in h264_results]
        psnr_values_h264 = [r['psnr'] for r in h264_results]
        bitrate_values_h264 = [r['bitrate'] for r in h264_results]
        
        ax.plot(bitrate_values_h264, psnr_values_h264, 'b-o', linewidth=2, markersize=10, label='H.264/AVC (JSVM)')
        
        for i, qp in enumerate(qp_values_h264):
            ax.annotate(f'QP{qp}', 
                        (bitrate_values_h264[i], psnr_values_h264[i]),
                        textcoords="offset points",
                        xytext=(10, 5),
                        fontsize=9,
                        fontweight='bold',
                        color='blue')
    
    # Plot H.265 results
    if h265_results:
        qp_values_h265 = [r['qp'] for r in h265_results]
        psnr_values_h265 = [r['psnr'] for r in h265_results]
        bitrate_values_h265 = [r['bitrate'] for r in h265_results]
        
        ax.plot(bitrate_values_h265, psnr_values_h265, 'r-s', linewidth=2, markersize=10, label='H.265/HEVC (HM)')
        
        for i, qp in enumerate(qp_values_h265):
            ax.annotate(f'QP{qp}', 
                        (bitrate_values_h265[i], psnr_values_h265[i]),
                        textcoords="offset points",
                        xytext=(10, -10),
                        fontsize=9,
                        fontweight='bold',
                        color='red')
    
    ax.set_xlabel('Bitrate (kbps)', fontsize=14)
    ax.set_ylabel('PSNR (dB)', fontsize=14)
    ax.set_title('Rate-Distortion Curve: PSNR vs Bitrate\nCrew CIF (352x288) - H.264/AVC vs H.265/HEVC', fontsize=16)
    ax.grid(True, linestyle='--', alpha=0.7)
    
    all_psnr = []
    all_bitrate = []
    if h264_results:
        all_psnr.extend([r['psnr'] for r in h264_results])
        all_bitrate.extend([r['bitrate'] for r in h264_results])
    if h265_results:
        all_psnr.extend([r['psnr'] for r in h265_results])
        all_bitrate.extend([r['bitrate'] for r in h265_results])
    
    # Set proper axis limits with padding
    bitrate_min = min(all_bitrate)
    bitrate_max = max(all_bitrate)
    bitrate_padding = (bitrate_max - bitrate_min) * 0.1
    
    ax.set_xlim(bitrate_min - bitrate_padding, bitrate_max + bitrate_padding)
    ax.set_ylim(min(all_psnr) - 2, max(all_psnr) + 2)
    ax.legend(loc='lower right', fontsize=12)
    
    output_path = os.path.join(EXAMPLE_DIR, output_file)
    fig.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"\nQP graph saved to: {output_path}")
    return output_path


def plot_gop_comparison(gop_results, output_file="gop_comparison.png"):
    """
    Plot GOP structure comparison as a dedicated graph.
    Shows PSNR vs Bitrate for different GOP structures at QP35,
    plus a secondary bar chart for encoding time.
    
    Args:
        gop_results: List of dicts with name, psnr, bitrate, time
        output_file: Output image filename
    """
    if not gop_results:
        return None
    
    names = [g['name'].replace('GOP', 'GOP ').replace('_', '\n') for g in gop_results]
    short_names = [g['name'] for g in gop_results]
    bitrates = [g['bitrate'] for g in gop_results]
    psnrs = [g['psnr'] for g in gop_results]
    times = [g['time'] for g in gop_results]
    
    colors = ['#1f77b4', '#2ca02c', '#9467bd', '#ff7f0e']
    markers = ['o', 's', 'D', '^']
    
    fig, axes = plt.subplots(1, 2, figsize=(18, 8), gridspec_kw={'width_ratios': [3, 2]})
    
    # ---- Left: PSNR vs Bitrate scatter ----
    ax1 = axes[0]
    for i, gop in enumerate(gop_results):
        ax1.scatter(gop['bitrate'], gop['psnr'],
                    s=220, marker=markers[i], color=colors[i],
                    edgecolors='black', linewidths=1.2, zorder=5,
                    label=short_names[i])
        ax1.annotate(f"{gop['psnr']:.2f} dB\n{gop['bitrate']:.1f} kbps",
                     (gop['bitrate'], gop['psnr']),
                     textcoords="offset points",
                     xytext=(15, (-1)**i * 12),
                     fontsize=9, fontweight='bold', color=colors[i],
                     bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                               edgecolor=colors[i], alpha=0.8))
    
    ax1.set_xlabel('Bitrate (kbps)', fontsize=13)
    ax1.set_ylabel('Y-PSNR (dB)', fontsize=13)
    ax1.set_title('GOP Structure Comparison — PSNR vs Bitrate\n(H.264/AVC, QP 35, Crew CIF 352x288, 300 frames)', fontsize=14)
    ax1.grid(True, linestyle='--', alpha=0.6)
    
    pad_br = (max(bitrates) - min(bitrates)) * 0.25 or 20
    ax1.set_xlim(min(bitrates) - pad_br, max(bitrates) + pad_br)
    pad_ps = (max(psnrs) - min(psnrs)) * 0.5 or 0.5
    ax1.set_ylim(min(psnrs) - pad_ps, max(psnrs) + pad_ps)
    ax1.legend(loc='lower right', fontsize=10, framealpha=0.9)
    
    # ---- Right: Bar chart (bitrate, PSNR, time) ----
    ax2 = axes[1]
    x = np.arange(len(gop_results))
    bar_w = 0.35
    
    bars1 = ax2.bar(x - bar_w/2, bitrates, bar_w, color=colors, edgecolor='black',
                    alpha=0.85, label='Bitrate (kbps)')
    ax2.set_ylabel('Bitrate (kbps)', fontsize=12, color='#333')
    ax2.set_xlabel('GOP Structure', fontsize=12)
    ax2.set_xticks(x)
    ax2.set_xticklabels([g['name'].replace('_', '\n') for g in gop_results], fontsize=9)
    
    # Add bitrate value labels on bars
    for bar, br in zip(bars1, bitrates):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2,
                 f'{br:.1f}', ha='center', va='bottom', fontsize=8, fontweight='bold')
    
    # Secondary y-axis for encoding time
    ax2b = ax2.twinx()
    bars2 = ax2b.bar(x + bar_w/2, times, bar_w, color='#d62728', edgecolor='black',
                     alpha=0.5, label='Enc Time (s)')
    ax2b.set_ylabel('Encoding Time (s)', fontsize=12, color='#d62728')
    
    for bar, t in zip(bars2, times):
        ax2b.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2,
                  f'{t:.0f}s', ha='center', va='bottom', fontsize=8,
                  fontweight='bold', color='#d62728')
    
    ax2.set_title('Bitrate & Encoding Time by GOP Structure', fontsize=13)
    
    # Combined legend
    lines1, labels1 = ax2.get_legend_handles_labels()
    lines2, labels2 = ax2b.get_legend_handles_labels()
    ax2.legend(lines1 + lines2, labels1 + labels2, loc='upper left', fontsize=9)
    
    fig.tight_layout()
    output_path = os.path.join(EXAMPLE_DIR, output_file)
    fig.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"GOP graph saved to: {output_path}")
    return output_path

def main():
    """Main function"""
    print()
    print("=" * 70)
    print("PSNR vs Bitrate Analysis - H.264 vs H.265")
    print("=" * 70)
    print()
    
    # Check input video exists
    if not os.path.exists(INPUT_VIDEO):
        print(f"ERROR: Input video not found: {INPUT_VIDEO}")
        return 1
    
    print(f"Input video: {INPUT_VIDEO}")
    print(f"Resolution: {VIDEO_WIDTH}x{VIDEO_HEIGHT}")
    print(f"Frames: {VIDEO_FRAMES}")
    print()
    
    # ==================== H.264 Analysis ====================
    print("=" * 70)
    print("H.264/AVC Analysis")
    print("=" * 70)
    
    # Find H.264 QP directories
    h264_qp_dirs = sorted(glob.glob(os.path.join(H264_CODEC_DIR, "QP*")))
    h264_qp_values = []
    for qp_dir in h264_qp_dirs:
        qp_name = os.path.basename(qp_dir)
        if qp_name.startswith("QP"):
            try:
                qp = int(qp_name[2:])
                h264_qp_values.append(qp)
            except ValueError:
                pass
    
    h264_qp_values.sort()
    print(f"Found H.264 QP values: {h264_qp_values}")
    print()
    
    h264_results = []
    for qp in h264_qp_values:
        print(f"Analyzing H.264 QP{qp}...")
        result = analyze_qp(qp, codec='h264')
        if result:
            h264_results.append(result)
            print(f"  PSNR: {result['psnr']:.2f} dB")
            print(f"  Bitrate: {result['bitrate']:.2f} kbps")
        print()
    
    # ==================== H.265 Analysis ====================
    print("=" * 70)
    print("H.265/HEVC Analysis")
    print("=" * 70)
    
    # Find H.265 QP directories
    h265_qp_dirs = sorted(glob.glob(os.path.join(H265_CODEC_DIR, "QP*")))
    h265_qp_values = []
    for qp_dir in h265_qp_dirs:
        qp_name = os.path.basename(qp_dir)
        if qp_name.startswith("QP"):
            try:
                qp = int(qp_name[2:])
                h265_qp_values.append(qp)
            except ValueError:
                pass
    
    h265_qp_values.sort()
    print(f"Found H.265 QP values: {h265_qp_values}")
    print()
    
    h265_results = []
    for qp in h265_qp_values:
        print(f"Analyzing H.265 QP{qp}...")
        result = analyze_qp(qp, codec='h265')
        if result:
            h265_results.append(result)
            print(f"  PSNR: {result['psnr']:.2f} dB")
            print(f"  Bitrate: {result['bitrate']:.2f} kbps")
        print()
    
    if not h264_results and not h265_results:
        print("ERROR: No valid results to plot!")
        return 1
    
    # Sort results by QP (ascending) for line plot
    h264_results.sort(key=lambda x: x['qp'])
    h265_results.sort(key=lambda x: x['qp'])
    
    # Print summary tables
    print("=" * 70)
    print("H.264/AVC SUMMARY TABLE")
    print("=" * 70)
    print(f"{'QP':<6} {'PSNR (dB)':<15} {'Bitrate (kbps)':<15}")
    print("-" * 70)
    for r in h264_results:
        print(f"{r['qp']:<6} {r['psnr']:<15.2f} {r['bitrate']:<15.2f}")
    print()
    
    print("=" * 70)
    print("H.265/HEVC SUMMARY TABLE")
    print("=" * 70)
    print(f"{'QP':<6} {'PSNR (dB)':<15} {'Bitrate (kbps)':<15}")
    print("-" * 70)
    for r in h265_results:
        print(f"{r['qp']:<6} {r['psnr']:<15.2f} {r['bitrate']:<15.2f}")
    print("=" * 70)
    print()
    
    # Plot QP comparison graph (H.264 vs H.265 only)
    print("Generating QP comparison graph (H.264 vs H.265)...")
    plot_psnr_vs_bitrate(h264_results, h265_results)
    
    # Load and plot GOP structure results as a separate graph
    gop_results = load_gop_results()
    if gop_results:
        print("=" * 70)
        print("GOP STRUCTURE COMPARISON (QP35)")
        print("=" * 70)
        print(f"{'GOP':<20} {'PSNR (dB)':<15} {'Bitrate (kbps)':<15} {'Enc Time (s)':<15}")
        print("-" * 70)
        for r in gop_results:
            print(f"{r['name']:<20} {r['psnr']:<15.4f} {r['bitrate']:<15.4f} {r['time']:<15.1f}")
        print("=" * 70)
        print()
        
        print("Generating GOP comparison graph...")
        plot_gop_comparison(gop_results)
    
    return 0

if __name__ == "__main__":
    exit(main())
