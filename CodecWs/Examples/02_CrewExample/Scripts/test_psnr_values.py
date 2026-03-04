#!/usr/bin/env python3
import sys
sys.path.insert(0, '.')
from config import *
from psnr_bitrate_graph import analyze_qp

print("="*70)
print("H.264 Analysis Results:")
print("="*70)
h264_results = []
for qp in [7, 15, 22, 28, 35, 45, 51]:
    result = analyze_qp(qp, 'h264')
    if result:
        h264_results.append(result)
        print(f"QP {qp:2d}: PSNR={result['psnr']:6.2f} dB, Bitrate={result['bitrate']:8.2f} kbps")
    else:
        print(f"QP {qp:2d}: FAILED")

print("\n" + "="*70)
print("H.265 Analysis Results:")
print("="*70)
h265_results = []
for qp in [7, 15, 22, 28, 35, 45, 51]:
    result = analyze_qp(qp, 'h265')
    if result:
        h265_results.append(result)
        print(f"QP {qp:2d}: PSNR={result['psnr']:6.2f} dB, Bitrate={result['bitrate']:8.2f} kbps")
    else:
        print(f"QP {qp:2d}: FAILED")

print("\n" + "="*70)
print("COMPARISON:")
print("="*70)
if h264_results and h265_results:
    for h264, h265 in zip(h264_results, h265_results):
        diff = h265['psnr'] - h264['psnr']
        print(f"QP {h264['qp']:2d}: H.264={h264['psnr']:6.2f} dB | H.265={h265['psnr']:6.2f} dB | Diff={diff:+6.2f} dB")
