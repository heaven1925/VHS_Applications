"""
Configuration for 02_CrewExample
Organized structure for H.264 codec experiments

Directory Structure:
    02_CrewExample/
    ├── Scripts/           # All Python scripts (this folder)
    ├── YUV_Video/         # Source and decoded videos
    │   ├── crew_cif.y4m   # Original Y4M
    │   ├── input.yuv      # Converted YUV
    │   └── decoded.yuv    # Decoded output
    └── H264_Codec/        # H.264 encoding results
        └── QP28/          # Results for QP=28
            ├── encoder.cfg
            ├── encoded.264
            └── results.txt
"""
import os

# ============================================================
# BASE PATHS
# ============================================================
WORKSPACE_ROOT = r"c:\Users\atakan\Desktop\CodecWs"
JSVM_ROOT = os.path.join(WORKSPACE_ROOT, "jsvm")
JSVM_BIN = os.path.join(JSVM_ROOT, "bin")

# JVET HM paths (H.265/HEVC)
JVET_ROOT = os.path.join(WORKSPACE_ROOT, "jvet")
JVET_BIN = os.path.join(JVET_ROOT, "bin", "mgwmake", "gcc-mingw-15.2", "x86_64", "release")

# Example directory structure
EXAMPLE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Parent of Scripts/
SCRIPTS_DIR = os.path.join(EXAMPLE_DIR, "Scripts")
APPLICATION_DIR = os.path.join(EXAMPLE_DIR, "Application")
YUV_VIDEO_DIR = os.path.join(EXAMPLE_DIR, "YUV_Video")
H264_CODEC_DIR = os.path.join(EXAMPLE_DIR, "H264_Codec")
H265_CODEC_DIR = os.path.join(EXAMPLE_DIR, "H265_Codec")

# ============================================================
# EXECUTABLES
# ============================================================
# H.264 (JSVM)
ENCODER_EXE = os.path.join(JSVM_BIN, "H264AVCEncoderLibTestStatic.exe")
DECODER_EXE = os.path.join(JSVM_BIN, "H264AVCDecoderLibTestStatic.exe")

# H.265 (HM)
H265_ENCODER_EXE = os.path.join(JVET_BIN, "TAppEncoder.exe")
H265_DECODER_EXE = os.path.join(JVET_BIN, "TAppDecoder.exe")

# ============================================================
# VIDEO SETTINGS (CIF = 352x288)
# ============================================================
VIDEO_WIDTH = 352
VIDEO_HEIGHT = 288
VIDEO_FRAMES = 300      # Number of frames to encode
VIDEO_FRAMERATE = 30.0  # From Y4M header

# ============================================================
# ENCODER SETTINGS
# ============================================================
QP = 28  # Current QP setting

# ============================================================
# FILE PATHS - YUV Video
# ============================================================
Y4M_SOURCE = os.path.join(YUV_VIDEO_DIR, "crew_cif.y4m")
INPUT_VIDEO = os.path.join(YUV_VIDEO_DIR, "input.yuv")
DECODED_VIDEO = os.path.join(YUV_VIDEO_DIR, "decoded.yuv")

# ============================================================
# FILE PATHS - H264 Codec (QP specific)
# ============================================================
def get_codec_dir(qp=None):
    """Get codec output directory for given QP"""
    if qp is None:
        qp = QP
    return os.path.join(H264_CODEC_DIR, f"QP{qp}")

def get_encoder_config(qp=None):
    """Get encoder config file path"""
    return os.path.join(get_codec_dir(qp), "encoder.cfg")

def get_bitstream_file(qp=None):
    """Get bitstream output file path"""
    return os.path.join(get_codec_dir(qp), "encoded.264")

def get_results_file(qp=None):
    """Get results file path"""
    return os.path.join(get_codec_dir(qp), "results.txt")

# Default paths (for backward compatibility)
CODEC_DIR = get_codec_dir()
ENCODER_CONFIG = get_encoder_config()
BITSTREAM_FILE = get_bitstream_file()
RESULTS_FILE = get_results_file()

# ============================================================
# H.265 FILE PATHS
# ============================================================
def get_h265_codec_dir(qp=None):
    """Get H.265 codec output directory for given QP"""
    if qp is None:
        qp = QP
    return os.path.join(H265_CODEC_DIR, f"QP{qp}")

def get_h265_encoder_config(qp=None):
    """Get H.265 encoder config file path"""
    return os.path.join(get_h265_codec_dir(qp), "encoder.cfg")

def get_h265_bitstream_file(qp=None):
    """Get H.265 bitstream output file path"""
    return os.path.join(get_h265_codec_dir(qp), "encoded.265")

def get_h265_results_file(qp=None):
    """Get H.265 results file path"""
    return os.path.join(get_h265_codec_dir(qp), "results.txt")

def get_h265_reconstructed_file(qp=None):
    """Get H.265 reconstructed file path"""
    return os.path.join(get_h265_codec_dir(qp), "reconstructed.yuv")

# ============================================================
# HELPER FUNCTIONS
# ============================================================
def ensure_dirs():
    """Create all necessary directories"""
    os.makedirs(YUV_VIDEO_DIR, exist_ok=True)
    os.makedirs(get_codec_dir(), exist_ok=True)

def get_video_info():
    """Return video information dict"""
    return {
        'width': VIDEO_WIDTH,
        'height': VIDEO_HEIGHT,
        'frames': VIDEO_FRAMES,
        'framerate': VIDEO_FRAMERATE,
        'format': 'YUV420'
    }

if __name__ == "__main__":
    print("02_CrewExample Configuration")
    print("=" * 50)
    print(f"Example Dir:    {EXAMPLE_DIR}")
    print(f"Scripts Dir:    {SCRIPTS_DIR}")
    print(f"YUV Video Dir:  {YUV_VIDEO_DIR}")
    print(f"H264 Codec Dir: {H264_CODEC_DIR}")
    print()
    print(f"Video: {VIDEO_WIDTH}x{VIDEO_HEIGHT} @ {VIDEO_FRAMERATE} fps")
    print(f"Frames: {VIDEO_FRAMES}")
    print(f"QP: {QP}")

