#!/usr/bin/env python3
"""
YUV Video Viewer
View YUV 4:2:0 video files - exports to BMP format (no dependencies)
"""
import os
import sys
import struct
from config import *

# Try to import PIL, but work without it
try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

def yuv_to_rgb(y, u, v):
    """Convert YUV to RGB (BT.601)"""
    r = y + 1.402 * (v - 128)
    g = y - 0.344136 * (u - 128) - 0.714136 * (v - 128)
    b = y + 1.772 * (u - 128)
    return (
        max(0, min(255, int(r))),
        max(0, min(255, int(g))),
        max(0, min(255, int(b)))
    )

def read_yuv_frame(file_handle, width, height):
    """Read a single YUV 4:2:0 frame and convert to RGB"""
    y_size = width * height
    uv_size = width * height // 4
    frame_size = y_size + 2 * uv_size
    
    data = file_handle.read(frame_size)
    if len(data) < frame_size:
        return None
    
    # Extract planes
    y_plane = list(data[:y_size])
    u_plane = list(data[y_size:y_size + uv_size])
    v_plane = list(data[y_size + uv_size:])
    
    # Convert to RGB
    rgb_data = []
    uv_width = width // 2
    
    for row in range(height):
        for col in range(width):
            y = y_plane[row * width + col]
            uv_row = row // 2
            uv_col = col // 2
            u = u_plane[uv_row * uv_width + uv_col]
            v = v_plane[uv_row * uv_width + uv_col]
            rgb_data.append(yuv_to_rgb(y, u, v))
    
    return rgb_data

def save_bmp(filename, width, height, rgb_data):
    """Save RGB data as BMP file (no dependencies needed)"""
    # BMP row padding
    row_padding = (4 - (width * 3) % 4) % 4
    row_size = width * 3 + row_padding
    pixel_data_size = row_size * height
    file_size = 54 + pixel_data_size
    
    with open(filename, 'wb') as f:
        # BMP Header
        f.write(b'BM')                           # Signature
        f.write(struct.pack('<I', file_size))    # File size
        f.write(struct.pack('<HH', 0, 0))        # Reserved
        f.write(struct.pack('<I', 54))           # Pixel data offset
        
        # DIB Header (BITMAPINFOHEADER)
        f.write(struct.pack('<I', 40))           # Header size
        f.write(struct.pack('<i', width))        # Width
        f.write(struct.pack('<i', height))       # Height (positive = bottom-up)
        f.write(struct.pack('<HH', 1, 24))       # Planes, Bits per pixel
        f.write(struct.pack('<I', 0))            # Compression (none)
        f.write(struct.pack('<I', pixel_data_size))  # Image size
        f.write(struct.pack('<i', 2835))         # X pixels per meter
        f.write(struct.pack('<i', 2835))         # Y pixels per meter
        f.write(struct.pack('<I', 0))            # Colors in color table
        f.write(struct.pack('<I', 0))            # Important colors
        
        # Pixel data (bottom-up, BGR format)
        padding = bytes(row_padding)
        for row in range(height - 1, -1, -1):
            for col in range(width):
                r, g, b = rgb_data[row * width + col]
                f.write(bytes([b, g, r]))  # BGR order
            f.write(padding)

def export_frames_as_bmp(yuv_file, output_dir, width, height, max_frames=None):
    """Export YUV frames as BMP images (pure Python, no dependencies)"""
    os.makedirs(output_dir, exist_ok=True)
    
    frame_idx = 0
    with open(yuv_file, 'rb') as f:
        while True:
            if max_frames and frame_idx >= max_frames:
                break
            
            rgb_data = read_yuv_frame(f, width, height)
            if rgb_data is None:
                break
            
            # Save as BMP
            output_path = os.path.join(output_dir, f'frame_{frame_idx:04d}.bmp')
            save_bmp(output_path, width, height, rgb_data)
            
            frame_idx += 1
            if frame_idx % 10 == 0:
                print(f"  Exported frame {frame_idx}...")
    
    return frame_idx

def export_frames_as_png(yuv_file, output_dir, width, height, max_frames=None):
    """Export YUV frames as PNG images (requires PIL)"""
    if not HAS_PIL:
        print("  PIL not available, using BMP format instead...")
        return export_frames_as_bmp(yuv_file, output_dir, width, height, max_frames)
    
    os.makedirs(output_dir, exist_ok=True)
    
    frame_idx = 0
    with open(yuv_file, 'rb') as f:
        while True:
            if max_frames and frame_idx >= max_frames:
                break
            
            rgb_data = read_yuv_frame(f, width, height)
            if rgb_data is None:
                break
            
            # Create image
            img = Image.new('RGB', (width, height))
            img.putdata(rgb_data)
            
            # Save
            output_path = os.path.join(output_dir, f'frame_{frame_idx:04d}.png')
            img.save(output_path)
            
            frame_idx += 1
            if frame_idx % 10 == 0:
                print(f"  Exported frame {frame_idx}...")
    
    return frame_idx

def create_animated_gif(png_dir, output_file, fps=10, max_frames=None):
    """Create animated GIF from PNG frames (requires PIL)"""
    if not HAS_PIL:
        print("  PIL not available - cannot create GIF")
        print("  Install Pillow: pip install pillow")
        return False
    
    # Get image files (PNG or BMP)
    img_files = sorted([f for f in os.listdir(png_dir) if f.endswith(('.png', '.bmp'))])
    if max_frames:
        img_files = img_files[:max_frames]
    
    if not img_files:
        print("No image files found")
        return False
    
    images = []
    for img_file in img_files:
        img = Image.open(os.path.join(png_dir, img_file))
        images.append(img.copy())
        img.close()
    
    # Save as GIF
    duration = int(1000 / fps)  # ms per frame
    images[0].save(
        output_file,
        save_all=True,
        append_images=images[1:],
        duration=duration,
        loop=0
    )
    
    return True

def show_frame_interactive(yuv_file, width, height, frame_num=0):
    """Show a specific frame"""
    frame_size = width * height * 3 // 2
    
    with open(yuv_file, 'rb') as f:
        f.seek(frame_num * frame_size)
        rgb_data = read_yuv_frame(f, width, height)
    
    if rgb_data is None:
        print(f"Could not read frame {frame_num}")
        return
    
    if HAS_PIL:
        img = Image.new('RGB', (width, height))
        img.putdata(rgb_data)
        img.show()
    else:
        # Save as BMP and open with system viewer
        temp_file = os.path.join(EXAMPLE_DIR, f'temp_frame_{frame_num}.bmp')
        save_bmp(temp_file, width, height, rgb_data)
        print(f"Saved frame to: {temp_file}")
        # Try to open with default viewer
        if sys.platform == 'win32':
            os.startfile(temp_file)
        else:
            print("Open the BMP file with your image viewer")

def export_comparison(original, decoded, output_dir, width, height, frames=[0, 10, 25, 49]):
    """Export side-by-side comparison of original vs decoded"""
    os.makedirs(output_dir, exist_ok=True)
    frame_size = width * height * 3 // 2
    
    for frame_num in frames:
        # Read original frame
        with open(original, 'rb') as f:
            f.seek(frame_num * frame_size)
            orig_rgb = read_yuv_frame(f, width, height)
        
        # Read decoded frame
        with open(decoded, 'rb') as f:
            f.seek(frame_num * frame_size)
            dec_rgb = read_yuv_frame(f, width, height)
        
        if orig_rgb is None or dec_rgb is None:
            continue
        
        # Calculate difference
        diff_sum = 0
        for i in range(len(orig_rgb)):
            for c in range(3):
                diff_sum += abs(orig_rgb[i][c] - dec_rgb[i][c])
        avg_diff = diff_sum / (len(orig_rgb) * 3)
        
        if HAS_PIL:
            # Create comparison image with PIL
            comparison = Image.new('RGB', (width * 2 + 10, height + 30), color=(40, 40, 40))
            
            orig_img = Image.new('RGB', (width, height))
            orig_img.putdata(orig_rgb)
            comparison.paste(orig_img, (0, 25))
            
            dec_img = Image.new('RGB', (width, height))
            dec_img.putdata(dec_rgb)
            comparison.paste(dec_img, (width + 10, 25))
            
            output_path = os.path.join(output_dir, f'comparison_frame_{frame_num:04d}.png')
            comparison.save(output_path)
        else:
            # Save separate BMP files for original and decoded
            orig_path = os.path.join(output_dir, f'frame_{frame_num:04d}_original.bmp')
            dec_path = os.path.join(output_dir, f'frame_{frame_num:04d}_decoded.bmp')
            save_bmp(orig_path, width, height, orig_rgb)
            save_bmp(dec_path, width, height, dec_rgb)
        
        print(f"  Frame {frame_num}: avg pixel diff = {avg_diff:.2f}")
    
    return True

def main():
    print()
    print("YUV Video Viewer / Exporter")
    print("=" * 50)
    print()
    
    # Check input files
    if not os.path.exists(INPUT_VIDEO):
        print(f"Input video not found: {INPUT_VIDEO}")
        print("Run 'python create_video.py' first.")
        return 1
    
    # Create output directories
    frames_dir = os.path.join(EXAMPLE_DIR, "frames")
    comparison_dir = os.path.join(EXAMPLE_DIR, "comparison")
    
    print(f"Source: {os.path.basename(INPUT_VIDEO)}")
    print(f"Resolution: {VIDEO_WIDTH}x{VIDEO_HEIGHT}")
    print()
    
    # Menu
    print("Options:")
    print("  1. Export first 10 frames as PNG")
    print("  2. Export all frames as PNG")
    print("  3. Create animated GIF (first 20 frames)")
    print("  4. View single frame")
    print("  5. Export comparison (original vs decoded)")
    print("  6. Export all + GIF + comparison")
    print()
    
    choice = input("Select option (1-6) or press Enter for option 6: ").strip()
    if not choice:
        choice = "6"
    
    print()
    
    if choice == "1":
        print("Exporting first 10 frames...")
        count = export_frames_as_png(INPUT_VIDEO, frames_dir, VIDEO_WIDTH, VIDEO_HEIGHT, max_frames=10)
        print(f"Exported {count} frames to: {frames_dir}")
        
    elif choice == "2":
        print("Exporting all frames...")
        count = export_frames_as_png(INPUT_VIDEO, frames_dir, VIDEO_WIDTH, VIDEO_HEIGHT)
        print(f"Exported {count} frames to: {frames_dir}")
        
    elif choice == "3":
        print("Creating animated GIF...")
        # First export frames
        export_frames_as_png(INPUT_VIDEO, frames_dir, VIDEO_WIDTH, VIDEO_HEIGHT, max_frames=20)
        # Then create GIF
        gif_path = os.path.join(EXAMPLE_DIR, "preview.gif")
        if create_animated_gif(frames_dir, gif_path, fps=10, max_frames=20):
            print(f"Created: {gif_path}")
        
    elif choice == "4":
        frame_num = input("Enter frame number (0-49): ").strip()
        frame_num = int(frame_num) if frame_num.isdigit() else 0
        print(f"Opening frame {frame_num}...")
        show_frame_interactive(INPUT_VIDEO, VIDEO_WIDTH, VIDEO_HEIGHT, frame_num)
        
    elif choice == "5":
        if not os.path.exists(DECODED_VIDEO):
            print(f"Decoded video not found. Run encoder/decoder first.")
            return 1
        print("Exporting comparison frames...")
        export_comparison(INPUT_VIDEO, DECODED_VIDEO, comparison_dir, VIDEO_WIDTH, VIDEO_HEIGHT)
        print(f"Saved to: {comparison_dir}")
        
    elif choice == "6":
        print("=== Exporting frames ===")
        count = export_frames_as_png(INPUT_VIDEO, frames_dir, VIDEO_WIDTH, VIDEO_HEIGHT, max_frames=20)
        print(f"Exported {count} frames")
        print()
        
        print("=== Creating GIF ===")
        gif_path = os.path.join(EXAMPLE_DIR, "preview.gif")
        if create_animated_gif(frames_dir, gif_path, fps=10):
            print(f"Created: {gif_path}")
            file_size = os.path.getsize(gif_path)
            print(f"Size: {file_size/1024:.1f} KB")
        print()
        
        if os.path.exists(DECODED_VIDEO):
            print("=== Exporting comparison ===")
            export_comparison(INPUT_VIDEO, DECODED_VIDEO, comparison_dir, VIDEO_WIDTH, VIDEO_HEIGHT)
            print(f"Saved to: {comparison_dir}")
    
    print()
    print("Done! You can open the PNG/GIF files with any image viewer.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
