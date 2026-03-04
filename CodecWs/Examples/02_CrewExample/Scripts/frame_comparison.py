#!/usr/bin/env python3
"""
Frame Comparison Tool
Extract and compare a specific frame across all QP values for H.264/H.265
Outputs BMP images and generates an HTML comparison page
"""
import os
import sys
import numpy as np
from PIL import Image
from config import *

def yuv420_to_rgb(y_data, u_data, v_data, width, height):
    """
    Convert YUV420 frame to RGB
    
    Args:
        y_data: Y channel (width × height bytes)
        u_data: U channel (width/2 × height/2 bytes)
        v_data: V channel (width/2 × height/2 bytes)
        width, height: Frame dimensions
    
    Returns:
        RGB image as numpy array (height × width × 3)
    """
    # Upsample U and V by 2x to match Y dimensions
    u_upsampled = np.repeat(np.repeat(u_data.reshape(height // 2, width // 2), 2, axis=0), 2, axis=1)
    v_upsampled = np.repeat(np.repeat(v_data.reshape(height // 2, width // 2), 2, axis=0), 2, axis=1)
    
    y = y_data.reshape(height, width).astype(np.float32)
    u = u_upsampled.astype(np.float32)
    v = v_upsampled.astype(np.float32)
    
    # BT.601 YUV to RGB conversion
    r = y + 1.402 * (v - 128)
    g = y - 0.34414 * (u - 128) - 0.71414 * (v - 128)
    b = y + 1.772 * (u - 128)
    
    # Clip to [0, 255]
    r = np.clip(r, 0, 255).astype(np.uint8)
    g = np.clip(g, 0, 255).astype(np.uint8)
    b = np.clip(b, 0, 255).astype(np.uint8)
    
    # Combine into RGB image
    rgb = np.stack([r, g, b], axis=2)
    return rgb

def extract_frame_from_yuv(yuv_file, frame_num, width, height):
    """
    Extract a specific frame from YUV420 file
    
    Args:
        yuv_file: Path to YUV420 file
        frame_num: Frame number to extract (0-indexed)
        width, height: Frame dimensions
    
    Returns:
        RGB image as numpy array
    """
    frame_size_y = width * height
    frame_size_uv = (width // 2) * (height // 2)
    frame_size_total = frame_size_y + 2 * frame_size_uv
    
    with open(yuv_file, 'rb') as f:
        f.seek(frame_num * frame_size_total)
        y_data = np.frombuffer(f.read(frame_size_y), dtype=np.uint8)
        u_data = np.frombuffer(f.read(frame_size_uv), dtype=np.uint8)
        v_data = np.frombuffer(f.read(frame_size_uv), dtype=np.uint8)
    
    rgb = yuv420_to_rgb(y_data, u_data, v_data, width, height)
    return rgb

def generate_comparison(frame_num=0, codec='h264'):
    """
    Generate frame comparison BMP images for all QP values
    
    Args:
        frame_num: Frame number to extract
        codec: 'h264' or 'h265'
    
    Returns:
        Dictionary with results and output paths
    """
    print(f"\n{'='*70}")
    print(f"Frame Comparison - {codec.upper()} (Frame {frame_num})")
    print(f"{'='*70}\n")
    
    if codec == 'h264':
        codec_dir = H264_CODEC_DIR
        qp_values = [7, 15, 22, 28, 35, 45, 51]
    else:
        codec_dir = H265_CODEC_DIR
        qp_values = [7, 15, 22, 28, 35, 45, 51]
    
    # Create codec-specific output directory
    output_dir = os.path.join(codec_dir, "frame_comparison")
    os.makedirs(output_dir, exist_ok=True)
    
    # Original frame
    print(f"Extracting original frame...")
    try:
        original_rgb = extract_frame_from_yuv(INPUT_VIDEO, frame_num, VIDEO_WIDTH, VIDEO_HEIGHT)
        original_img = Image.fromarray(original_rgb)
        original_path = os.path.join(output_dir, f"{codec.lower()}_original_frame.bmp")
        original_img.save(original_path)
        print(f"  Original: {original_path}")
    except Exception as e:
        print(f"  ERROR reading original: {e}")
        return None
    
    # Extract frames for each QP
    results = []
    for qp in qp_values:
        reconstructed = os.path.join(codec_dir, f"QP{qp}", "reconstructed.yuv")
        
        if not os.path.exists(reconstructed):
            print(f"  QP{qp}: File not found")
            continue
        
        try:
            rgb = extract_frame_from_yuv(reconstructed, frame_num, VIDEO_WIDTH, VIDEO_HEIGHT)
            img = Image.fromarray(rgb)
            output_path = os.path.join(output_dir, f"{codec.lower()}_QP{qp:02d}_frame{frame_num}.bmp")
            img.save(output_path)
            
            # Calculate MSE and PSNR for this frame
            diff = original_rgb.astype(np.float32) - rgb.astype(np.float32)
            mse = np.mean(diff ** 2)
            if mse > 0:
                psnr = 10 * np.log10(255 ** 2 / mse)
            else:
                psnr = float('inf')
            
            results.append({
                'codec': codec.upper(),
                'qp': qp,
                'psnr': psnr,
                'mse': mse,
                'bmp_h264': f"H264_Codec/frame_comparison/{codec.lower()}_QP{qp:02d}_frame{frame_num}.bmp" if codec == 'h264' else f"H265_Codec/frame_comparison/{codec.lower()}_QP{qp:02d}_frame{frame_num}.bmp"
            })
            print(f"  QP{qp:2d}: PSNR = {psnr:6.2f} dB, MSE = {mse:8.2f}")
        except Exception as e:
            print(f"  QP{qp}: ERROR - {e}")
    
    return {
        'codec': codec,
        'results': results,
        'output_dir': output_dir,
        'original_path': original_path
    }

def generate_html(html_file, h264_data, h265_data, frame_num):
    """Generate unified HTML page for both codec comparison"""
    html = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Frame Comparison - H.264 vs H.265</title>
    <style>
        body {{ font-family: Arial, sans-serif; background: #f5f5f5; margin: 20px; }}
        h1 {{ color: #333; }}
        .container {{ max-width: 1600px; margin: 0 auto; }}
        .tabs {{ display: flex; gap: 0; margin: 20px 0; border-bottom: 2px solid #007bff; }}
        .tab-button {{ 
            padding: 12px 24px; 
            background: #e0e0e0; 
            border: none; 
            cursor: pointer; 
            font-size: 16px;
            transition: 0.3s;
        }}
        .tab-button.active {{ background: #007bff; color: white; }}
        .tab-button:hover {{ background: #0056b3; color: white; }}
        .tab-content {{ display: none; }}
        .tab-content.active {{ display: block; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(380px, 1fr)); gap: 20px; margin-top: 20px; }}
        .frame-card {{ background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
        .frame-card img {{ width: 100%; height: auto; display: block; }}
        .frame-info {{ padding: 15px; }}
        .frame-info h3 {{ margin: 0 0 8px 0; color: #333; }}
        .frame-info p {{ margin: 4px 0; color: #666; font-size: 14px; }}
        .psnr {{ color: #2ca02c; font-weight: bold; }}
        .mse {{ color: #d62728; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 30px; background: white; }}
        table th, table td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        table th {{ background: #007bff; color: white; font-weight: bold; }}
        table tr:hover {{ background: #f9f9f9; }}
    </style>
    <script>
        function showTab(tabName) {{
            var tabs = document.getElementsByClassName('tab-content');
            var buttons = document.getElementsByClassName('tab-button');
            
            for (var i = 0; i < tabs.length; i++) {{
                tabs[i].classList.remove('active');
            }}
            for (var i = 0; i < buttons.length; i++) {{
                buttons[i].classList.remove('active');
            }}
            
            document.getElementById(tabName).classList.add('active');
            event.target.classList.add('active');
        }}
    </script>
</head>
<body>
    <div class="container">
        <h1>Frame Comparison - H.264 vs H.265</h1>
        <p><strong>Resolution:</strong> 352×288 | <strong>Format:</strong> YUV420 | <strong>Frame:</strong> {frame}</p>
        
        <div class="tabs">
            <button class="tab-button active" onclick="showTab('h264')">H.264 (JSVM)</button>
            <button class="tab-button" onclick="showTab('h265')">H.265 (HM)</button>
            <button class="tab-button" onclick="showTab('comparison')">Comparison</button>
        </div>
        
        <!-- H.264 Tab -->
        <div id="h264" class="tab-content active">
            <h2>H.264 - Different QP Values</h2>
            <div class="grid">
                <div class="frame-card">
                    <img src="../../H264_Codec/frame_comparison/h264_original_frame.bmp" alt="Original">
                    <div class="frame-info">
                        <h3>Original (Uncompressed)</h3>
                        <p>Reference frame</p>
                    </div>
                </div>
""".format(frame=frame_num)
    
    for result in h264_data['results']:
        qp = result['qp']
        psnr = result['psnr']
        mse = result['mse']
        
        html += f"""                <div class="frame-card">
                    <img src="../../H264_Codec/frame_comparison/h264_QP{qp:02d}_frame{frame_num}.bmp" alt="QP{qp}">
                    <div class="frame-info">
                        <h3>QP {qp}</h3>
                        <p><span class="psnr">PSNR: {psnr:.2f} dB</span></p>
                        <p><span class="mse">MSE: {mse:.2f}</span></p>
                    </div>
                </div>
"""
    
    html += """            </div>
            
            <h3>Quality Metrics</h3>
            <table>
                <tr>
                    <th>QP</th>
                    <th>PSNR (dB)</th>
                    <th>MSE</th>
                </tr>
"""
    
    for result in sorted(h264_data['results'], key=lambda x: x['qp']):
        html += f"""                <tr>
                    <td><strong>QP {result['qp']}</strong></td>
                    <td>{result['psnr']:.4f}</td>
                    <td>{result['mse']:.2f}</td>
                </tr>
"""
    
    html += """            </table>
        </div>
        
        <!-- H.265 Tab -->
        <div id="h265" class="tab-content">
            <h2>H.265 - Different QP Values</h2>
            <div class="grid">
                <div class="frame-card">
                    <img src="../../H265_Codec/frame_comparison/h265_original_frame.bmp" alt="Original">
                    <div class="frame-info">
                        <h3>Original (Uncompressed)</h3>
                        <p>Reference frame</p>
                    </div>
                </div>
"""
    
    for result in h265_data['results']:
        qp = result['qp']
        psnr = result['psnr']
        mse = result['mse']
        
        html += f"""                <div class="frame-card">
                    <img src="../../H265_Codec/frame_comparison/h265_QP{qp:02d}_frame{frame_num}.bmp" alt="QP{qp}">
                    <div class="frame-info">
                        <h3>QP {qp}</h3>
                        <p><span class="psnr">PSNR: {psnr:.2f} dB</span></p>
                        <p><span class="mse">MSE: {mse:.2f}</span></p>
                    </div>
                </div>
"""
    
    html += """            </div>
            
            <h3>Quality Metrics</h3>
            <table>
                <tr>
                    <th>QP</th>
                    <th>PSNR (dB)</th>
                    <th>MSE</th>
                </tr>
"""
    
    for result in sorted(h265_data['results'], key=lambda x: x['qp']):
        html += f"""                <tr>
                    <td><strong>QP {result['qp']}</strong></td>
                    <td>{result['psnr']:.4f}</td>
                    <td>{result['mse']:.2f}</td>
                </tr>
"""
    
    html += """            </table>
        </div>
        
        <!-- Comparison Tab -->
        <div id="comparison" class="tab-content">
            <h2>H.264 vs H.265 Comparison</h2>
            
            <table>
                <tr>
                    <th>QP</th>
                    <th>H.264 PSNR (dB)</th>
                    <th>H.265 PSNR (dB)</th>
                    <th>Difference (dB)</th>
                    <th>H.265 Better</th>
                </tr>
"""
    
    for h264_result in sorted(h264_data['results'], key=lambda x: x['qp']):
        qp = h264_result['qp']
        h265_result = next((r for r in h265_data['results'] if r['qp'] == qp), None)
        
        if h265_result:
            h264_psnr = h264_result['psnr']
            h265_psnr = h265_result['psnr']
            diff = h265_psnr - h264_psnr
            better = "✓" if diff > 0 else ""
            
            html += f"""                <tr>
                    <td><strong>QP {qp}</strong></td>
                    <td>{h264_psnr:.4f}</td>
                    <td>{h265_psnr:.4f}</td>
                    <td>{diff:+.4f}</td>
                    <td>{better}</td>
                </tr>
"""
    
    html += """            </table>
        </div>
    </div>
</body>
</html>
"""
    
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html)

def main():
    """Main function"""
    print()
    print("="*70)
    print("Frame Comparison Tool - Extract Frames for Visual Inspection")
    print("="*70)
    print()
    
    # Check input video
    if not os.path.exists(INPUT_VIDEO):
        print(f"ERROR: Input video not found: {INPUT_VIDEO}")
        return 1
    
    # Get frame number from command line or user input
    if len(sys.argv) > 1:
        try:
            frame_num = int(sys.argv[1])
        except ValueError:
            print("ERROR: Invalid frame number argument")
            return 1
    else:
        try:
            frame_num = int(input(f"Enter frame number to extract (0-{VIDEO_FRAMES-1}) [default: 0]: ") or "0")
        except ValueError:
            print("ERROR: Invalid frame number")
            return 1
    
    if frame_num < 0 or frame_num >= VIDEO_FRAMES:
        print(f"ERROR: Frame number must be between 0 and {VIDEO_FRAMES-1}")
        return 1
    
    print(f"\nExtracting frame {frame_num} for all QP values...\n")
    
    # Generate H.264 comparison
    print("\n" + "="*70)
    h264_data = generate_comparison(frame_num, 'h264')
    
    # Generate H.265 comparison
    print("\n" + "="*70)
    h265_data = generate_comparison(frame_num, 'h265')
    
    # Generate unified HTML comparison page
    print("\n" + "="*70)
    if h264_data and h265_data:
        # Create shared directory in Application or Scripts
        shared_output_dir = os.path.join(APPLICATION_DIR, "frame_comparison")
        os.makedirs(shared_output_dir, exist_ok=True)
        
        html_file = os.path.join(shared_output_dir, "frame_comparison.html")
        generate_html(html_file, h264_data, h265_data, frame_num)
        print(f"✓ Unified HTML comparison: {html_file}")
    
    print(f"✓ H.264 frames: H264_Codec/frame_comparison/")
    print(f"✓ H.265 frames: H265_Codec/frame_comparison/")
    print("="*70)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
