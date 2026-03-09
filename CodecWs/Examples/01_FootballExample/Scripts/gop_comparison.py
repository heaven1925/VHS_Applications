#!/usr/bin/env python3
"""
GOP Comparison Analysis — Rate-Distortion & Encoding Time
Generates comparison graphs for different GOP structures at QP 35
"""

import os
import sys
import csv
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from pathlib import Path

# Get the script directory
SCRIPT_DIR = Path(__file__).parent
EXAMPLE_DIR = SCRIPT_DIR.parent
CODEC_DIR = EXAMPLE_DIR / "H264_Codec"

# Read gop_results.txt
GOP_RESULTS = CODEC_DIR / "gop_results.txt"

def read_gop_results():
    """Read GOP comparison results from CSV"""
    if not GOP_RESULTS.exists():
        print(f"ERROR: {GOP_RESULTS} not found")
        print("Run encodings first to generate GOP results")
        sys.exit(1)
    
    data = []
    with open(GOP_RESULTS, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append({
                'gop': row['GOP_DIR'].replace('QP35_', ''),
                'frames': int(row['FRAMES']),
                'enc_kb': float(row['ENC_KB']),
                'psnr': float(row['PSNR_Y']),
                'bitrate': float(row['BITRATE_KBPS']),
                'time_sec': float(row['TIME_SEC'])
            })
    return data

def get_video_info():
    """Load video info from video_info.json"""
    import json
    video_info_file = EXAMPLE_DIR / "video_info.json"
    if video_info_file.exists():
        with open(video_info_file) as f:
            return json.load(f)
    return {"name": "Video", "width": 352, "height": 288, "frames": 360}

def create_gop_comparison():
    """Create GOP structure comparison graphs"""
    
    data = read_gop_results()
    video_info = get_video_info()
    
    print("=" * 70)
    print(f"GOP Structure Comparison — {video_info.get('name', '01_FootballExample')}")
    print("=" * 70)
    print(f"Video: {video_info['width']}x{video_info['height']}, {video_info['frames']} frames, QP=35")
    print()
    
    # Create figure with subplots
    fig = plt.figure(figsize=(16, 5.5))
    
    colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D']
    # Format GOP names for display
    gop_display = {
        'GOP1_IPP': 'IPP\n(Fast)',
        'GOP2_IBBP': 'IBBP\n(B-frames)',
        'GOP3_HierB': 'HierB\n(Hierarchical)',
        'GOP4_IRefresh': 'I-Refresh'
    }
    gop_names = [d['gop'] for d in data]
    gop_labels = [gop_display.get(g, g) for g in gop_names]
    bitrates = [d['bitrate'] for d in data]
    times = [d['time_sec'] for d in data]
    
    # =========== Plot 1: Bitrate Comparison (Bar Chart) ===========
    ax1 = plt.subplot(1, 3, 1)
    
    bars1 = ax1.bar(range(len(gop_names)), bitrates, color=colors, edgecolor='black', linewidth=2, alpha=0.85, width=0.6)
    ax1.set_xticks(range(len(gop_names)))
    ax1.set_xticklabels(gop_labels, fontsize=11, fontweight='bold')
    
    # Add value labels on bars
    for bar, bitrate in zip(bars1, bitrates):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{bitrate:.0f}\nkbps', ha='center', va='bottom', 
                fontsize=11, fontweight='bold')
    
    # Highlight minimum
    min_idx = np.argmin(bitrates)
    bars1[min_idx].set_edgecolor('gold')
    bars1[min_idx].set_linewidth(3)
    
    ax1.set_ylabel('Bitrate (kbps)', fontsize=13, fontweight='bold')
    ax1.set_title('Compression Efficiency', fontsize=13, fontweight='bold')
    ax1.set_ylim(0, max(bitrates) * 1.25)
    ax1.grid(True, alpha=0.3, axis='y', linestyle='--')
    ax1.set_axisbelow(True)
    
    # =========== Plot 2: Encoding Time Comparison (Bar Chart) ===========
    ax2 = plt.subplot(1, 3, 2)
    
    bars2 = ax2.bar(range(len(gop_names)), times, color=colors, edgecolor='black', linewidth=2, alpha=0.85, width=0.6)
    ax2.set_xticks(range(len(gop_names)))
    ax2.set_xticklabels(gop_labels, fontsize=11, fontweight='bold')
    
    # Add value labels on bars
    for bar, time_val in zip(bars2, times):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{time_val:.0f}\nsec', ha='center', va='bottom', 
                fontsize=11, fontweight='bold')
    
    # Highlight minimum
    min_idx_time = np.argmin(times)
    bars2[min_idx_time].set_edgecolor('gold')
    bars2[min_idx_time].set_linewidth(3)
    
    ax2.set_ylabel('Encoding Time (seconds)', fontsize=13, fontweight='bold')
    ax2.set_title('Encoding Speed', fontsize=13, fontweight='bold')
    ax2.set_ylim(0, max(times) * 1.25)
    ax2.grid(True, alpha=0.3, axis='y', linestyle='--')
    ax2.set_axisbelow(True)
    
    # =========== Plot 3: Summary Table ===========
    ax3 = plt.subplot(1, 3, 3)
    ax3.axis('off')
    
    # Create summary table
    ref_bitrate = bitrates[0]  # GOP1_IPP as reference
    
    table_data = [['GOP', 'Bitrate', 'Vs GOP1', 'Time']]
    
    for i, gop in enumerate(gop_names):
        bitrate_vs = ((bitrates[i] - ref_bitrate) / ref_bitrate) * 100
        time_str = f"{times[i]:.0f}s"
        
        bitrate_vs_str = f"{bitrate_vs:+.1f}%" if bitrate_vs != 0 else "—"
        
        table_data.append([
            gop,
            f"{bitrates[i]:.0f} kbps",
            bitrate_vs_str,
            time_str
        ])
    
    # Add summary rows
    table_data.append(['', '', '', ''])
    table_data.append(['■ Best', 'Compression:', gop_names[np.argmin(bitrates)], 'Bitrate'])
    table_data.append(['■ Best', 'Speed:', gop_names[np.argmin(times)], 'Encode time'])
    
    # Create table
    table = ax3.table(cellText=table_data, cellLoc='center', loc='center',
                     colWidths=[0.25, 0.35, 0.25, 0.25])
    
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 2.2)
    
    # Style header row
    for i in range(4):
        table[(0, i)].set_facecolor('#2E86AB')
        table[(0, i)].set_text_props(weight='bold', color='white')
    
    # Style data rows
    for i in range(1, len(table_data) - 1):
        for j in range(4):
            if i % 2 == 0:
                table[(i, j)].set_facecolor('#F0F0F0')
            table[(i, j)].set_text_props(weight='bold' if i < 5 else 'normal')
    
    # Style summary rows
    for j in range(4):
        table[(len(table_data) - 2, j)].set_facecolor('#FFE082')
        table[(len(table_data) - 1, j)].set_facecolor('#FFE082')
        table[(len(table_data) - 2, j)].set_text_props(weight='bold')
        table[(len(table_data) - 1, j)].set_text_props(weight='bold')
    
    # Overall title
    fig.suptitle(f"GOP Yapı Karşılaştırması — {video_info.get('name', 'Video')} (QP=35)", 
                 fontsize=15, fontweight='bold', y=0.98)
    
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    
    # Save graph
    output_file = EXAMPLE_DIR / "gop_comparison.png"
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"Graph saved: {output_file}")
    
    # Print summary
    print("\nGOP Comparison Results:")
    print("-" * 70)
    print(f"{'GOP':<15} {'PSNR':<10} {'Bitrate':<15} {'Time':<10} {'Encoder CPU':<10}")
    print("-" * 70)
    
    for d in data:
        print(f"{d['gop']:<15} {d['psnr']:<10.4f} {d['bitrate']:<14.2f} {d['time_sec']:<10.1f} {d['time_sec']/d['frames']*1000:>8.2f}ms")
    
    best_bitrate_idx = np.argmin(bitrates)
    baseline_bitrate = bitrates[0]
    savings = ((baseline_bitrate - bitrates[best_bitrate_idx]) / baseline_bitrate) * 100
    
    print("-" * 70)
    print(f"\nBest compression: {gop_names[best_bitrate_idx]} with {savings:.1f}% bitrate reduction")
    print(f"Fastest: {gop_names[np.argmin(times)]} with {min(times):.1f}s encoding time")
    print("=" * 70)

if __name__ == "__main__":
    create_gop_comparison()
