#!/usr/bin/env python3
"""
Y4M to YUV Converter
Converts Y4M (YUV4MPEG2) format to raw YUV format
"""
import os
import sys
import struct

def parse_y4m_header(line):
    """Parse Y4M header line"""
    # Example: MPEG4MPEG2 W352 H288 F25:1 Ip A0:0 C420
    params = {}
    
    parts = line.split()
    for part in parts[1:]:  # Skip 'MPEG4MPEG2'
        if part[0] == 'W':
            params['width'] = int(part[1:])
        elif part[0] == 'H':
            params['height'] = int(part[1:])
        elif part[0] == 'F':
            rate_parts = part[1:].split(':')
            params['framerate_num'] = int(rate_parts[0])
            params['framerate_den'] = int(rate_parts[1])
        elif part[0] == 'C':
            params['colorspace'] = part[1:]
    
    return params

def get_frame_size(width, height, colorspace='420'):
    """Calculate raw frame size for YUV 4:2:0"""
    if colorspace == '420':
        return width * height + (width * height) // 2
    elif colorspace == '422':
        return width * height * 2
    elif colorspace == '444':
        return width * height * 3
    else:
        return width * height + (width * height) // 2  # Default to 420

def convert_y4m_to_yuv(input_file, output_file, max_frames=None):
    """Convert Y4M to raw YUV format"""
    print(f"Converting Y4M to YUV")
    print(f"Input: {os.path.basename(input_file)}")
    print(f"Output: {os.path.basename(output_file)}")
    
    with open(input_file, 'rb') as infile:
        # Read and parse header
        header_line = b''
        while True:
            byte = infile.read(1)
            if byte == b'\n':
                break
            header_line += byte
        
        header = header_line.decode('ascii').strip()
        print(f"Header: {header}")
        
        params = parse_y4m_header(header)
        width = params.get('width')
        height = params.get('height')
        colorspace = params.get('colorspace', '420')
        framerate_num = params.get('framerate_num', 25)
        framerate_den = params.get('framerate_den', 1)
        
        print(f"Resolution: {width}x{height}")
        print(f"Framerate: {framerate_num}/{framerate_den} fps")
        print(f"Colorspace: {colorspace}")
        print()
        
        frame_size = get_frame_size(width, height, colorspace)
        print(f"Frame size: {frame_size} bytes")
        
        # Convert frames
        frame_count = 0
        with open(output_file, 'wb') as outfile:
            while True:
                # Look for FRAME marker
                frame_marker = infile.read(6)
                if not frame_marker:
                    break
                
                if frame_marker != b'FRAME\n':
                    # Try to find next FRAME
                    pos = infile.tell()
                    search = frame_marker.decode('ascii', errors='ignore')
                    if 'FRAME' in search:
                        infile.seek(pos - 5)
                    continue
                
                # Read frame data
                frame_data = infile.read(frame_size)
                if len(frame_data) < frame_size:
                    break
                
                outfile.write(frame_data)
                frame_count += 1
                
                if frame_count % 10 == 0:
                    print(f"  Converted frame {frame_count}...")
                
                if max_frames and frame_count >= max_frames:
                    break
    
    print()
    print(f"✓ Conversion completed!")
    print(f"  Frames: {frame_count}")
    print(f"  Output size: {os.path.getsize(output_file):,} bytes")
    
    return {
        'width': width,
        'height': height,
        'frames': frame_count,
        'framerate': framerate_num / framerate_den if framerate_den > 0 else 25,
        'colorspace': colorspace
    }

def main():
    if len(sys.argv) < 2:
        print("Usage: python y4m_to_yuv.py <input.y4m> [output.yuv] [max_frames]")
        print()
        return 1
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else 'output.yuv'
    max_frames = int(sys.argv[3]) if len(sys.argv) > 3 else None
    
    if not os.path.exists(input_file):
        print(f"Error: File not found: {input_file}")
        return 1
    
    return 0 if convert_y4m_to_yuv(input_file, output_file, max_frames) else 1

if __name__ == "__main__":
    sys.exit(main())
