"""
Generic Configuration for Video Codec Examples
Auto-detects video properties from Y4M file or uses video_info.json
"""
import os
import json
import re

# ============================================================
# BASE PATHS
# ============================================================
WORKSPACE_ROOT = r"c:\Users\atakan\Desktop\CodecWs"
JSVM_ROOT = os.path.join(WORKSPACE_ROOT, "jsvm")
JSVM_BIN = os.path.join(JSVM_ROOT, "bin")

# JVET HM paths (H.265/HEVC)
JVET_ROOT = os.path.join(WORKSPACE_ROOT, "jvet")
JVET_BIN = os.path.join(JVET_ROOT, "bin", "mgwmake", "gcc-mingw-15.2", "x86_64", "release")

# Example directory structure (auto-detect from script location)
EXAMPLE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXAMPLE_NAME = os.path.basename(EXAMPLE_DIR)
SCRIPTS_DIR = os.path.join(EXAMPLE_DIR, "Scripts")
YUV_VIDEO_DIR = os.path.join(EXAMPLE_DIR, "YUV_Video")
H264_CODEC_DIR = os.path.join(EXAMPLE_DIR, "H264_Codec")
H265_CODEC_DIR = os.path.join(EXAMPLE_DIR, "H265_Codec")

# ============================================================
# EXECUTABLES
# ============================================================
ENCODER_EXE = os.path.join(JSVM_BIN, "H264AVCEncoderLibTestStatic.exe")
DECODER_EXE = os.path.join(JSVM_BIN, "H264AVCDecoderLibTestStatic.exe")
H265_ENCODER_EXE = os.path.join(JVET_BIN, "TAppEncoder.exe")
H265_DECODER_EXE = os.path.join(JVET_BIN, "TAppDecoder.exe")

# ============================================================
# VIDEO INFO - Auto-detect or load from video_info.json
# ============================================================
VIDEO_INFO_FILE = os.path.join(EXAMPLE_DIR, "video_info.json")
INPUT_VIDEO = os.path.join(YUV_VIDEO_DIR, "input.yuv")


def parse_y4m_header(y4m_path):
    """Parse Y4M file header to extract video properties."""
    with open(y4m_path, 'rb') as f:
        header = f.read(256).decode('ascii', errors='ignore')
        header_line = header.split('\n')[0]
    
    info = {'chroma': '420'}
    
    # Parse width
    m = re.search(r'W(\d+)', header_line)
    if m:
        info['width'] = int(m.group(1))
    
    # Parse height
    m = re.search(r'H(\d+)', header_line)
    if m:
        info['height'] = int(m.group(1))
    
    # Parse framerate
    m = re.search(r'F(\d+):(\d+)', header_line)
    if m:
        info['framerate'] = float(m.group(1)) / float(m.group(2))
    
    # Parse chroma subsampling
    m = re.search(r'C(\d+)', header_line)
    if m:
        info['chroma'] = m.group(1)
    
    # Calculate frame count from file size
    if 'width' in info and 'height' in info:
        file_size = os.path.getsize(y4m_path)
        header_size = len(header_line) + 1
        
        w, h = info['width'], info['height']
        chroma = info.get('chroma', '420')
        
        if chroma == '422':
            frame_size = w * h + 2 * (w // 2) * h + 6  # FRAME header
        else:  # 420
            frame_size = w * h + 2 * (w // 2) * (h // 2) + 6
        
        info['frames'] = (file_size - header_size) // frame_size
    
    return info


def find_y4m_file():
    """Find Y4M file in YUV_Video directory."""
    if not os.path.exists(YUV_VIDEO_DIR):
        return None
    for f in os.listdir(YUV_VIDEO_DIR):
        if f.endswith('.y4m'):
            return os.path.join(YUV_VIDEO_DIR, f)
    return None


def load_video_info():
    """Load video info from JSON or auto-detect from Y4M."""
    # Try JSON first
    if os.path.exists(VIDEO_INFO_FILE):
        with open(VIDEO_INFO_FILE, 'r') as f:
            return json.load(f)
    
    # Try auto-detect from Y4M
    y4m_path = find_y4m_file()
    if y4m_path:
        info = parse_y4m_header(y4m_path)
        info['y4m_source'] = y4m_path
        return info
    
    # Default fallback
    return {
        'width': 352,
        'height': 288,
        'frames': 300,
        'framerate': 30.0,
        'chroma': '420'
    }


# Load video info
_video_info = load_video_info()
VIDEO_WIDTH = _video_info.get('width', 352)
VIDEO_HEIGHT = _video_info.get('height', 288)
VIDEO_FRAMES = _video_info.get('frames', 300)
VIDEO_FRAMERATE = _video_info.get('framerate', 30.0)
VIDEO_CHROMA = _video_info.get('chroma', '420')
Y4M_SOURCE = _video_info.get('y4m_source', find_y4m_file())

# ============================================================
# HELPER FUNCTIONS
# ============================================================
def get_codec_dir(qp, codec='h264'):
    if codec == 'h264':
        return os.path.join(H264_CODEC_DIR, f"QP{qp}")
    return os.path.join(H265_CODEC_DIR, f"QP{qp}")

def get_matched_dir(qp, codec='h264'):
    if codec == 'h264':
        return os.path.join(H264_CODEC_DIR, f"QP{qp}_matched")
    return os.path.join(H265_CODEC_DIR, f"QP{qp}_matched")


if __name__ == "__main__":
    print(f"Example: {EXAMPLE_NAME}")
    print(f"Directory: {EXAMPLE_DIR}")
    print(f"Video: {VIDEO_WIDTH}x{VIDEO_HEIGHT}, {VIDEO_FRAMES} frames @ {VIDEO_FRAMERATE} fps")
    print(f"Chroma: {VIDEO_CHROMA}")
    print(f"Y4M Source: {Y4M_SOURCE}")
    print(f"Input YUV: {INPUT_VIDEO}")
