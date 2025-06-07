#!/usr/bin/env python3
"""
Master script to run all arXiv aggregators in sequence.
This provides a single command to generate all category pages.
"""

import sys
import subprocess
import time
import os
import shutil
import ftplib
from datetime import datetime
from featured_tracker import clear_featured_ids
from config import FTP_HOST, FTP_USER, FTP_PASS, FTP_REMOTE_DIR

def log(message):
    """Print timestamped log message."""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")

def clear_ftp_server():
    """Clear HTML files and images from the FTP server."""
    try:
        log("🌐 Connecting to FTP server to clear old content...")
        with ftplib.FTP(FTP_HOST, FTP_USER, FTP_PASS) as ftp:
            ftp.encoding = 'utf-8'
            ftp.cwd(FTP_REMOTE_DIR)
            
            # List of HTML files to remove
            html_files = ["index.html", "ml.html", "cv.html", "cr.html", "ro.html", "hc.html"]
            cleared_html = 0
            
            # Get list of files on server
            server_files = ftp.nlst()
            
            # Remove HTML files
            for html_file in html_files:
                if html_file in server_files:
                    try:
                        ftp.delete(html_file)
                        cleared_html += 1
                        log(f"🗑️  Removed {html_file} from FTP server")
                    except ftplib.error_perm as e:
                        log(f"⚠️  Failed to remove {html_file} from FTP server: {e}")
            
            # Clear images directory on server
            cleared_images = 0
            if 'images' in server_files:
                try:
                    # Change to images directory
                    ftp.cwd('images')
                    
                    # Get list of image files
                    image_files = [f for f in ftp.nlst() if f.endswith('.jpg')]
                    cleared_images = len(image_files)
                    
                    # Remove all image files
                    for image_file in image_files:
                        try:
                            ftp.delete(image_file)
                        except ftplib.error_perm as e:
                            log(f"⚠️  Failed to remove {image_file}: {e}")
                    
                    # Go back to root directory
                    ftp.cwd('..')
                    
                    if cleared_images > 0:
                        log(f"🗑️  Removed {cleared_images} image files from FTP server")
                        
                except ftplib.error_perm as e:
                    log(f"⚠️  Failed to access images directory on FTP server: {e}")
            
            # Summary
            if cleared_html > 0 or cleared_images > 0:
                log(f"🌐 FTP cleanup complete: {cleared_html} HTML files, {cleared_images} images cleared")
            else:
                log("🌐 No files to clear on FTP server")
                
    except Exception as e:
        log(f"❌ Failed to connect to FTP server for cleanup: {e}")
        log("⚠️  Continuing with local cleanup only...")

def clear_generated_content():
    """Clear all generated HTML files and images from the output directory."""
    output_dir = "output"
    
    if not os.path.exists(output_dir):
        log("📁 Output directory doesn't exist, nothing to clear")
        return
    
    # Clear HTML files
    html_files = ["index.html", "ml.html", "cv.html", "cr.html", "ro.html", "hc.html"]
    cleared_html = 0
    
    for html_file in html_files:
        html_path = os.path.join(output_dir, html_file)
        if os.path.exists(html_path):
            try:
                os.remove(html_path)
                cleared_html += 1
                log(f"🗑️  Removed {html_file}")
            except Exception as e:
                log(f"⚠️  Failed to remove {html_file}: {e}")
    
    # Clear images directory
    images_dir = os.path.join(output_dir, "images")
    cleared_images = 0
    
    if os.path.exists(images_dir):
        try:
            # Count files before clearing
            image_files = [f for f in os.listdir(images_dir) if f.endswith('.jpg')]
            cleared_images = len(image_files)
            
            # Remove the entire images directory and recreate it
            shutil.rmtree(images_dir)
            os.makedirs(images_dir)
            
            if cleared_images > 0:
                log(f"🗑️  Removed {cleared_images} image files from images directory")
        except Exception as e:
            log(f"⚠️  Failed to clear images directory: {e}")
    
    # Summary
    if cleared_html > 0 or cleared_images > 0:
        log(f"🧹 Local cleanup complete: {cleared_html} HTML files, {cleared_images} images cleared")
    else:
        log("🧹 No local files to clear")

def run_aggregator(script_name, category_name):
    """Run a single aggregator script and handle errors."""
    log(f"Starting {category_name} aggregator...")
    
    try:
        # Run the aggregator script
        result = subprocess.run([sys.executable, script_name], 
                              capture_output=True, 
                              text=True, 
                              timeout=600)  # 10 minute timeout
        
        if result.returncode == 0:
            log(f"✅ {category_name} aggregator completed successfully")
            return True
        else:
            log(f"❌ {category_name} aggregator failed with exit code {result.returncode}")
            if result.stderr:
                log(f"Error output: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        log(f"❌ {category_name} aggregator timed out after 10 minutes")
        return False
    except Exception as e:
        log(f"❌ {category_name} aggregator failed with exception: {e}")
        return False

def main():
    """Run all aggregators in sequence."""
    log("🚀 Starting arXiv aggregator batch run...")
    
    # Clear featured article tracking to start fresh
    clear_featured_ids()
    log("🔄 Cleared featured article tracking for fresh batch")
    
    # Clear generated content to conserve server resources and ensure fresh content
    clear_ftp_server()  # Clear FTP server first
    clear_generated_content()  # Then clear local files
    
    start_time = time.time()
    
    # List of aggregators to run: (script_name, display_name)
    aggregators = [
        ("aggregator.py", "AI Research"),
        ("aggregator_ml.py", "Machine Learning"),
        ("aggregator_cv.py", "Computer Vision"),
        ("aggregator_cr.py", "Security/Cryptography"),
        ("aggregator_ro.py", "Robotics"),
        ("aggregator_hc.py", "Human-Computer Interaction"),
    ]
    
    results = {}
    
    for script_name, category_name in aggregators:
        success = run_aggregator(script_name, category_name)
        results[category_name] = success
        
        if success:
            log(f"✅ {category_name} page generated and uploaded")
        else:
            log(f"❌ {category_name} page failed")
        
        # Small delay between aggregators to avoid overwhelming APIs
        time.sleep(2)
    
    # Summary
    elapsed_time = time.time() - start_time
    log(f"\n📊 BATCH RUN SUMMARY (completed in {elapsed_time:.1f}s)")
    log("=" * 50)
    
    success_count = 0
    for category_name, success in results.items():
        status = "✅ SUCCESS" if success else "❌ FAILED"
        log(f"{category_name:20} {status}")
        if success:
            success_count += 1
    
    log("=" * 50)
    log(f"Total: {success_count}/{len(aggregators)} aggregators completed successfully")
    
    if success_count == len(aggregators):
        log("🎉 All aggregators completed successfully!")
        return 0
    else:
        log("⚠️  Some aggregators failed. Check logs above for details.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)