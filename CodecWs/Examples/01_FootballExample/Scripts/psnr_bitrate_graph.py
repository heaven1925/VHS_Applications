#!/usr/bin/env python3
"""
PSNR vs Bitrate Graph Generator - Generic version
Generates Rate-Distortion curve for H.264 vs H.265 comparison.

Usage:
    python psnr_bitrate_graph.py
"""
import os
import sys
import math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from config import *

QP_VALUES_H264 = [7, 15, 22, 28, 35, 45, 55]
QP_VALUES_H265 = [7, 15, 22, 28, 35, 45, 51]


def calculate_psnr(original, reconstructed, bit_depth=8):
    """Calculate PSNR in dB."""
    I_max = (2 ** bit_depth) - 1
    diff = original.astype(np.float64) - reconstructed.astype(np.float64)
    mse = np.mean(diff ** 2)
    if mse == 0:
        return float('inf')
    return 10 * math.log10((I_max ** 2) / mse)


def read_yuv420(filepath, width, height, num_frames=None):
    """Read YUV420 file and return (Y, Cb, Cr) numpy arrays."""
    frame_y = width * height
    frame_uv = (width // 2) * (height // 2)
    frame_total = frame_y + 2 * frame_uv
    
    file_size = os.path.getsize(filepath)
    total_frames = file_size // frame_total
    if num_frames is None:
        num_frames = total_frames
    else:
        num_frames = min(num_frames, total_frames)
    
    y_all, cb_all, cr_all = [], [], []
    with open(filepath, 'rb') as f:
        for _ in range(num_frames):
            y_all.append(np.frombuffer(f.read(frame_y), dtype=np.uint8))
            cb_all.append(np.frombuffer(f.read(frame_uv), dtype=np.uint8))
            cr_all.append(np.frombuffer(f.read(frame_uv), dtype=np.uint8))
    
    return np.concatenate(y_all), np.concatenate(cb_all), np.concatenate(cr_all)


def analyze_qp(qp, codec):
    """Calculate PSNR and bitrate for a matched encoding."""
    ext = "264" if codec == 'h264' else "265"
    codec_dir = get_matched_dir(qp, codec)
    bitstream = os.path.join(codec_dir, f"encoded.{ext}")
    reconstructed = os.path.join(codec_dir, "reconstructed.yuv")
    
    if not os.path.exists(bitstream):
        return None
    if not os.path.exists(reconstructed):
        return None
    
    # Bitrate
    bs_bits = os.path.getsize(bitstream) * 8
    duration = VIDEO_FRAMES / VIDEO_FRAMERATE
    bitrate = bs_bits / duration / 1000  # kbps
    
    try:
        orig_y, orig_cb, orig_cr = read_yuv420(INPUT_VIDEO, VIDEO_WIDTH, VIDEO_HEIGHT, VIDEO_FRAMES)
        rec_y, rec_cb, rec_cr = read_yuv420(reconstructed, VIDEO_WIDTH, VIDEO_HEIGHT, VIDEO_FRAMES)
        
        psnr_y = calculate_psnr(orig_y, rec_y)
        psnr_cb = calculate_psnr(orig_cb, rec_cb)
        psnr_cr = calculate_psnr(orig_cr, rec_cr)
        psnr_avg = (6 * psnr_y + psnr_cb + psnr_cr) / 8
    except Exception as e:
        print(f"  [SKIP] {codec.upper()} QP{qp}: {type(e).__name__}")
        return None
    
    return {
        'qp': qp, 'psnr': psnr_avg, 'psnr_y': psnr_y,
        'psnr_cb': psnr_cb, 'psnr_cr': psnr_cr, 'bitrate': bitrate
    }


def plot_rd_curve(h264_results, h265_results, output_file="psnr_vs_bitrate_matched.png"):
    """Plot PSNR vs Bitrate RD curve."""
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # H.264
    if h264_results:
        br = [r['bitrate'] for r in h264_results]
        ps = [r['psnr'] for r in h264_results]
        ax.plot(br, ps, 'b-o', linewidth=2, markersize=10, label='H.264/AVC (JSVM)')
        for r in h264_results:
            ax.annotate(f'QP{r["qp"]}', (r['bitrate'], r['psnr']),
                        textcoords="offset points", xytext=(10, 5),
                        fontsize=9, fontweight='bold', color='blue')
    
    # H.265
    if h265_results:
        br = [r['bitrate'] for r in h265_results]
        ps = [r['psnr'] for r in h265_results]
        ax.plot(br, ps, 'r-s', linewidth=2, markersize=10, label='H.265/HEVC (HM)')
        for r in h265_results:
            ax.annotate(f'QP{r["qp"]}', (r['bitrate'], r['psnr']),
                        textcoords="offset points", xytext=(10, -12),
                        fontsize=9, fontweight='bold', color='red')
    
    ax.set_xlabel('Bitrate (kbps)', fontsize=14)
    ax.set_ylabel('PSNR (dB) — YCbCr Weighted Avg = (6Y+Cb+Cr)/8', fontsize=13)
    ax.set_title(f'Rate-Distortion: H.264/AVC vs H.265/HEVC\n'
                 f'{EXAMPLE_NAME} ({VIDEO_WIDTH}×{VIDEO_HEIGHT}, {VIDEO_FRAMES} frames)\n'
                 f'Hierarchical B, IntraPeriod=32, Ref=4',
                 fontsize=14)
    ax.grid(True, linestyle='--', alpha=0.7)
    ax.legend(loc='lower right', fontsize=12)
    
    # Axis limits
    all_br = [r['bitrate'] for r in (h264_results or []) + (h265_results or [])]
    all_ps = [r['psnr'] for r in (h264_results or []) + (h265_results or [])]
    if all_br and all_ps:
        pad_br = (max(all_br) - min(all_br)) * 0.1
        ax.set_xlim(min(all_br) - pad_br, max(all_br) + pad_br)
        ax.set_ylim(min(all_ps) - 2, max(all_ps) + 2)
    
    output_path = os.path.join(EXAMPLE_DIR, output_file)
    fig.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"\nGraph saved: {output_path}")
    return output_path


def main():
    print("=" * 60)
    print(f"Rate-Distortion Analysis — {EXAMPLE_NAME}")
    print("=" * 60)
    print(f"  Video : {INPUT_VIDEO}")
    print(f"  Size  : {VIDEO_WIDTH}x{VIDEO_HEIGHT}, {VIDEO_FRAMES} frames")
    print(f"  H.264 QPs : {QP_VALUES_H264}")
    print(f"  H.265 QPs : {QP_VALUES_H265}")
    print()
    
    if not os.path.exists(INPUT_VIDEO):
        print(f"ERROR: Input video not found: {INPUT_VIDEO}")
        return 1
    
    # Analyze H.264
    print("--- H.264/AVC ---")
    h264_results = []
    for qp in QP_VALUES_H264:
        r = analyze_qp(qp, 'h264')
        if r:
            h264_results.append(r)
            print(f"  QP{qp:>2}: PSNR={r['psnr']:.2f} dB  Bitrate={r['bitrate']:.1f} kbps")
        else:
            print(f"  QP{qp:>2}: SKIP")
    
    # Analyze H.265
    print("\n--- H.265/HEVC ---")
    h265_results = []
    for qp in QP_VALUES_H265:
        r = analyze_qp(qp, 'h265')
        if r:
            h265_results.append(r)
            print(f"  QP{qp:>2}: PSNR={r['psnr']:.2f} dB  Bitrate={r['bitrate']:.1f} kbps")
        else:
            print(f"  QP{qp:>2}: SKIP")
    
    if not h264_results and not h265_results:
        print("\nERROR: No results. Run matched_encode.py first.")
        return 1
    
    # Summary table
    print("\n" + "=" * 70)
    print(f"{'QP':<5} {'H.264 PSNR':>12} {'H.264 Rate':>12} {'H.265 PSNR':>12} {'H.265 Rate':>12} {'Saving':>10}")
    print("-" * 70)
    
    h264_map = {r['qp']: r for r in h264_results}
    h265_map = {r['qp']: r for r in h265_results}
    
    all_qps = sorted(set(QP_VALUES_H264 + QP_VALUES_H265))
    for qp in all_qps:
        r4 = h264_map.get(qp)
        r5 = h265_map.get(qp)
        p4 = f"{r4['psnr']:.2f} dB" if r4 else "—"
        b4 = f"{r4['bitrate']:.1f} kbps" if r4 else "—"
        p5 = f"{r5['psnr']:.2f} dB" if r5 else "—"
        b5 = f"{r5['bitrate']:.1f} kbps" if r5 else "—"
        saving = f"{(1 - r5['bitrate']/r4['bitrate'])*100:.1f}%" if r4 and r5 and r4['bitrate'] > 0 else ""
        print(f"QP{qp:<3} {p4:>12} {b4:>12} {p5:>12} {b5:>12} {saving:>10}")
    
    print("=" * 70)
    
    # Plot
    h264_results.sort(key=lambda x: x['qp'])
    h265_results.sort(key=lambda x: x['qp'])
    plot_rd_curve(h264_results, h265_results)
    
    return 0


if __name__ == "__main__":
    exit(main())
