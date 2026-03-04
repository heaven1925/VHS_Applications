"""
Encode all GOP structure examples and collect results.
Runs each encoding sequentially, waits for completion, and verifies 300 frames.
"""
import subprocess
import os
import sys
import time

BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'H264_Codec')
ENCODER = r'c:\Users\atakan\Desktop\CodecWs\jsvm\bin\H264AVCEncoderLibTestStatic.exe'
FRAME_SIZE = 352 * 288 * 3 // 2  # YUV420 CIF

GOP_DIRS = [
    'QP35_GOP1_IPP',
    'QP35_GOP2_IBBP', 
    'QP35_GOP3_HierB',
    'QP35_GOP4_IRefresh',
]

results = {}

for gop_dir in GOP_DIRS:
    work_dir = os.path.join(BASE_DIR, gop_dir)
    cfg_file = os.path.join(work_dir, 'encoder.cfg')
    enc_file = os.path.join(work_dir, 'encoded.264')
    rec_file = os.path.join(work_dir, 'reconstructed.yuv')
    log_file = os.path.join(work_dir, 'encode_log.txt')
    
    if not os.path.exists(cfg_file):
        print(f"[SKIP] {gop_dir}: encoder.cfg not found")
        continue
    
    # Clean old outputs
    for f in [enc_file, rec_file, log_file]:
        if os.path.exists(f):
            try:
                os.remove(f)
            except PermissionError:
                print(f"  Warning: Could not remove {os.path.basename(f)}, skipping...")
                time.sleep(1)
                try:
                    os.remove(f)
                except:
                    pass
    
    print(f"\n{'='*60}")
    print(f"[START] Encoding {gop_dir}...")
    print(f"{'='*60}")
    start_time = time.time()
    
    # Run encoder
    with open(log_file, 'w') as log_f:
        proc = subprocess.run(
            [ENCODER, '-pf', 'encoder.cfg'],
            cwd=work_dir,
            stdout=log_f,
            stderr=subprocess.STDOUT,
            timeout=600  # 10 minute timeout
        )
    
    elapsed = time.time() - start_time
    
    # Read last lines of log
    if os.path.exists(log_file):
        with open(log_file, 'r') as f:
            lines = f.readlines()
        last_lines = lines[-8:] if len(lines) >= 8 else lines
        print("".join(last_lines))
    
    # Check frame count
    if os.path.exists(rec_file):
        rec_size = os.path.getsize(rec_file)
        frames = rec_size // FRAME_SIZE
    else:
        frames = 0
    
    if os.path.exists(enc_file):
        enc_size = os.path.getsize(enc_file)
    else:
        enc_size = 0
    
    # Parse PSNR and bitrate from log
    psnr_y = 0.0
    bitrate = 0.0
    for line in reversed(lines):
        if 'frames encoded' in line:
            parts = line.strip().split()
            for i, p in enumerate(parts):
                if p == 'Y':
                    psnr_y = float(parts[i+1])
                    break
        if 'average bit rate' in line:
            parts = line.strip().split()
            for i, p in enumerate(parts):
                try:
                    val = float(p)
                    if val > 10:  # bitrate value
                        bitrate = val
                        break
                except:
                    continue
    
    results[gop_dir] = {
        'frames': frames,
        'enc_kb': enc_size / 1024,
        'psnr_y': psnr_y,
        'bitrate': bitrate,
        'time_sec': elapsed
    }
    
    status = "OK" if frames == 300 else f"FAIL ({frames} frames)"
    print(f"[{status}] {gop_dir}: {frames} frames, {enc_size/1024:.1f} KB, "
          f"PSNR-Y={psnr_y:.4f} dB, Bitrate={bitrate:.4f} kbps, Time={elapsed:.1f}s")

# Summary
print(f"\n{'='*60}")
print("SUMMARY")
print(f"{'='*60}")
print(f"{'GOP Structure':<25} {'Frames':>6} {'Size(KB)':>10} {'PSNR-Y(dB)':>12} {'Bitrate(kbps)':>14} {'Time(s)':>8}")
print("-" * 80)
for name, r in results.items():
    print(f"{name:<25} {r['frames']:>6} {r['enc_kb']:>10.1f} {r['psnr_y']:>12.4f} {r['bitrate']:>14.4f} {r['time_sec']:>8.1f}")

# Save results to file
results_file = os.path.join(BASE_DIR, 'gop_results.txt')
with open(results_file, 'w') as f:
    f.write("GOP_DIR,FRAMES,ENC_KB,PSNR_Y,BITRATE_KBPS,TIME_SEC\n")
    for name, r in results.items():
        f.write(f"{name},{r['frames']},{r['enc_kb']:.1f},{r['psnr_y']:.4f},{r['bitrate']:.4f},{r['time_sec']:.1f}\n")

print(f"\nResults saved to: {results_file}")
