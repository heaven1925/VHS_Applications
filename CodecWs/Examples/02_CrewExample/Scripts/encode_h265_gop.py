#!/usr/bin/env python3
"""
H.265 GOP Structure Encoding for Crew Example

Encodes the 4 GOP structures for H.265 at QP=35 to compare with H.264 results.
"""
import os
import sys
import subprocess
import time
from pathlib import Path

# Add Scripts to path for config import
scripts_dir = Path(__file__).parent
sys.path.insert(0, str(scripts_dir))
from config import *

def run_h265_gop_encoding():
    """Run all H.265 GOP encodings."""
    
    gop_configs = {
        'QP35_GOP1_IPP': 'IPP (Fast)',
        'QP35_GOP2_IBBP': 'IBBP (B-frames)',
        'QP35_GOP3_HierB': 'HierB (Hierarchical)',
        'QP35_GOP4_IRefresh': 'IRefresh (I-refresh)'
    }
    
    results = []
    
    for gop_dir, gop_desc in gop_configs.items():
        gop_path = os.path.join(H265_CODEC_DIR, gop_dir)
        cfg_path = os.path.join(gop_path, "encoder.cfg")
        bitstream_path = os.path.join(gop_path, "encoded.265")
        
        if not os.path.exists(cfg_path):
            print(f"ERROR: Config not found: {cfg_path}")
            continue
            
        print(f"\n{'='*70}")
        print(f"Encoding: {gop_desc}")
        print(f"Directory: {gop_path}")
        print(f"Config: {cfg_path}")
        print(f"{'='*70}")
        
        # Run H.265 encoder
        t0 = time.time()
        try:
            result = subprocess.run(
                [H265_ENCODER_EXE, "-c", cfg_path],
                cwd=gop_path,
                capture_output=True,
                text=True,
                timeout=7200
            )
            elapsed = time.time() - t0
            
            print(f"Encoding completed in {elapsed:.1f} seconds")
            
            if result.returncode == 0 and os.path.exists(bitstream_path):
                bitstream_size = os.path.getsize(bitstream_path) / 1024  # KB
                print(f"Bitstream size: {bitstream_size:.1f} KB")
                print(f"Output saved to: {bitstream_path}")
                
                # Parse encoder output for PSNR
                psnr = extract_psnr(result.stderr or result.stdout)
                results.append({
                    'gop': gop_dir,
                    'desc': gop_desc,
                    'bitstream_kb': bitstream_size,
                    'psnr': psnr,
                    'time_sec': elapsed
                })
                
            else:
                print(f"ERROR: Encoding failed!")
                print("STDOUT:", result.stdout[:500])
                print("STDERR:", result.stderr[:500])
                
        except subprocess.TimeoutExpired:
            print(f"ERROR: Encoding timeout after 2 hours!")
        except Exception as e:
            print(f"ERROR: {str(e)}")
    
    print(f"\n{'='*70}")
    print("H.265 GOP Encoding Summary:")
    print(f"{'='*70}")
    for r in results:
        print(f"{r['gop']}: {r['time_sec']:.1f}s, {r['bitstream_kb']:.1f} KB")
    
    return results

def extract_psnr(output_text):
    """Extract PSNR from encoder output."""
    if not output_text:
        return None
    for line in output_text.split('\n'):
        if 'PSNR' in line.upper() and 'Y' in line:
            try:
                parts = line.split()
                for i, p in enumerate(parts):
                    if p.upper() == 'Y:' and i+1 < len(parts):
                        return float(parts[i+1])
            except:
                pass
    return None

if __name__ == "__main__":
    print(f"H.265 Encoder: {H265_ENCODER_EXE}")
    if not os.path.exists(H265_ENCODER_EXE):
        print(f"ERROR: H.265 encoder not found at {H265_ENCODER_EXE}")
        sys.exit(1)
    
    run_h265_gop_encoding()
