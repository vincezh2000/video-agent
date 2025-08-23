#!/usr/bin/env python3
"""
Correctly handle VP9 with alpha channel WebM files.
VP9 stores alpha as a separate stream that needs special handling.
"""

import subprocess
import sys
from pathlib import Path
import argparse
import os


def combine_vp9_alpha_with_background(webm_path, jpg_path, output_path="output.mp4"):
    """
    Use FFmpeg to properly combine VP9 with alpha channel and background.
    VP9 with alpha requires special handling as the alpha is stored separately.
    """
    print(f"Processing VP9 with alpha channel...")
    print(f"  Video: {webm_path}")
    print(f"  Background: {jpg_path}")
    
    # Check if files exist
    if not Path(webm_path).exists():
        print(f"❌ Video not found: {webm_path}")
        return False
    
    if not Path(jpg_path).exists():
        print(f"❌ Background not found: {jpg_path}")
        return False
    
    # Method 1: Direct overlay with alpha channel handling
    cmd = [
        'ffmpeg', '-y',
        '-i', str(jpg_path),      # Background image (input 0)
        '-i', str(webm_path),     # WebM with alpha (input 1)
        '-filter_complex',
        '[0:v]scale=544:736,format=rgb24[bg];'  # Scale background
        '[1:v]format=yuva420p[fg];'              # Ensure foreground has alpha
        '[bg][fg]overlay=0:0:format=auto',       # Overlay with alpha
        '-c:v', 'libx264',
        '-preset', 'medium',
        '-crf', '18',
        '-pix_fmt', 'yuv420p',
        str(output_path)
    ]
    
    print("\n🎬 Running FFmpeg with VP9 alpha support...")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print("First method failed, trying alternative approach...")
            # Method 2: Explicitly handle alpha extraction
            cmd2 = [
                'ffmpeg', '-y',
                '-i', str(jpg_path),
                '-c:v', 'vp9',
                '-i', str(webm_path),
                '-filter_complex',
                '[0:v]scale=544:736[bg];'
                '[bg][1:v]overlay=0:0',
                '-c:v', 'libx264',
                '-preset', 'medium',
                '-crf', '18',
                str(output_path)
            ]
            
            result = subprocess.run(cmd2, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"❌ FFmpeg error: {result.stderr}")
                return False
        
        print(f"✅ Successfully created: {output_path}")
        
        # Check output
        if Path(output_path).exists():
            size_mb = Path(output_path).stat().st_size / (1024 * 1024)
            print(f"📊 File size: {size_mb:.2f} MB")
            
            # Get output info
            probe_cmd = ['ffprobe', '-v', 'error', '-show_entries', 
                        'stream=width,height,r_frame_rate,nb_frames',
                        '-of', 'json', str(output_path)]
            probe_result = subprocess.run(probe_cmd, capture_output=True, text=True)
            if probe_result.returncode == 0:
                import json
                info = json.loads(probe_result.stdout)
                if info.get('streams'):
                    stream = info['streams'][0]
                    print(f"📹 Resolution: {stream.get('width')}x{stream.get('height')}")
        
        return True
        
    except FileNotFoundError:
        print("❌ FFmpeg not found. Please install: brew install ffmpeg")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def extract_alpha_channel(webm_path, alpha_output="alpha.mov"):
    """
    Extract the alpha channel as a separate video for debugging.
    """
    print(f"Extracting alpha channel to: {alpha_output}")
    
    cmd = [
        'ffmpeg', '-y',
        '-i', str(webm_path),
        '-vf', 'alphaextract',
        '-c:v', 'prores_ks',
        '-profile:v', '4',
        str(alpha_output)
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Alpha channel extracted to: {alpha_output}")
            return True
        else:
            print(f"Failed to extract alpha: {result.stderr}")
            return False
    except:
        return False


def check_alpha_presence(webm_path):
    """
    Check if the WebM file truly has an alpha channel.
    """
    print("Checking for alpha channel...")
    
    cmd = [
        'ffmpeg', '-i', str(webm_path), '-vf', 'alphaextract', 
        '-frames:v', '1', '-f', 'null', '-'
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        stderr = result.stderr.lower()
        
        # Check for alpha_mode in metadata
        if 'alpha_mode' in stderr:
            print("✅ Alpha channel detected (alpha_mode present)")
            return True
        
        # Check if alphaextract succeeded
        if result.returncode == 0 and 'error' not in stderr:
            print("✅ Alpha channel detected (alphaextract succeeded)")
            return True
        
        print("⚠️  No alpha channel detected")
        return False
        
    except:
        print("⚠️  Could not check for alpha channel")
        return False


def main():
    """Command line interface."""
    parser = argparse.ArgumentParser(
        description="Combine VP9 WebM with alpha channel with background",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
This tool properly handles VP9 videos with alpha channels.

Examples:
  %(prog)s video.webm background.jpg
  %(prog)s video.webm background.jpg -o output.mp4
  %(prog)s video.webm background.jpg --check-alpha
  %(prog)s video.webm background.jpg --extract-alpha
        """
    )
    
    parser.add_argument("webm", help="WebM video with alpha channel")
    parser.add_argument("background", help="Background image (JPG/PNG)")
    parser.add_argument("-o", "--output", default="output_vp9.mp4", 
                       help="Output file path")
    parser.add_argument("--check-alpha", action="store_true",
                       help="Check if video has alpha channel")
    parser.add_argument("--extract-alpha", action="store_true",
                       help="Extract alpha channel to separate file")
    
    args = parser.parse_args()
    
    print("\n" + "="*50)
    print("VP9 Alpha Channel Video Combiner")
    print("="*50 + "\n")
    
    # Check alpha if requested
    if args.check_alpha:
        has_alpha = check_alpha_presence(args.webm)
        if not has_alpha:
            print("\n⚠️  Warning: No alpha channel detected!")
            print("The video might not have transparency.")
            response = input("\nContinue anyway? (y/n): ")
            if response.lower() != 'y':
                sys.exit(0)
    
    # Extract alpha if requested
    if args.extract_alpha:
        alpha_file = Path(args.webm).stem + "_alpha.mov"
        extract_alpha_channel(args.webm, alpha_file)
        print()
    
    # Process video
    success = combine_vp9_alpha_with_background(
        args.webm, 
        args.background, 
        args.output
    )
    
    if success:
        print(f"\n✅ Done! Output saved to: {args.output}")
        print(f"\nTo play: open {args.output}")
    else:
        print("\n❌ Processing failed")
        sys.exit(1)


if __name__ == "__main__":
    main()