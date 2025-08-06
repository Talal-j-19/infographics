#!/usr/bin/env python3
"""
Job Manager for Infographic Generation
Creates unique job folders for each generation to avoid caching issues
"""

import os
import uuid
import time
from pathlib import Path
import shutil


class ParallelInfographicJobManager:
    """Manages parallel infographic generation jobs with batch folders for variants"""

    def __init__(self, base_dir="generated", variant_count=3):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True)
        self.current_batch_id = None
        self.current_batch_dir = None
        self.variant_count = variant_count
        self.variant_jobs = []
        
    def create_batch_job(self, topic="infographic"):
        """
        Create a new batch job with unique ID and variant folders

        Args:
            topic: Topic name for the infographic (used in folder naming)

        Returns:
            tuple: (batch_id, batch_directory_path, variant_job_managers)
        """
        # Generate unique batch ID
        timestamp = int(time.time())
        unique_id = str(uuid.uuid4())[:8]  # Short UUID

        # Clean topic name for folder
        clean_topic = "".join(c for c in topic if c.isalnum() or c in (' ', '-', '_')).strip()
        clean_topic = clean_topic.replace(' ', '_').lower()[:30]  # Max 30 chars

        # Create batch ID
        self.current_batch_id = f"batch_{timestamp}_{unique_id}_{clean_topic}"

        # Create batch directory
        self.current_batch_dir = self.base_dir / self.current_batch_id
        self.current_batch_dir.mkdir(parents=True, exist_ok=True)

        # Create variant directories and job managers
        variant_managers = []
        for i in range(self.variant_count):
            variant_dir = self.current_batch_dir / f"variant_{i+1}"
            variant_dir.mkdir(parents=True, exist_ok=True)

            # Create individual job manager for each variant
            from job_manager import InfographicJobManager
            variant_manager = InfographicJobManager(str(variant_dir))
            variant_job_id = f"{self.current_batch_id}_variant_{i+1}"
            variant_manager.current_job_id = variant_job_id
            variant_manager.current_job_dir = variant_dir
            variant_managers.append(variant_manager)

        # Store variant managers
        self.variant_jobs = variant_managers

        print(f"🆔 Created new batch job: {self.current_batch_id}")
        print(f"📁 Batch directory: {self.current_batch_dir}")
        print(f"🎯 Created {self.variant_count} variant folders")

        return self.current_batch_id, self.current_batch_dir, variant_managers
    
    def get_file_paths(self):
        """
        Get file paths for the current job
        
        Returns:
            dict: Dictionary with file paths for html, png, svg
        """
        if not self.current_job_dir:
            raise ValueError("No active job. Call create_new_job() first.")
        
        return {
            'html': self.current_job_dir / "infographic.html",
            'png': self.current_job_dir / "infographic.png", 
            'svg': self.current_job_dir / "infographic.svg",
            'job_info': self.current_job_dir / "job_info.txt"
        }

    def get_variant_managers(self):
        """
        Get the variant job managers for the current batch

        Returns:
            list: List of InfographicJobManager instances for each variant
        """
        if not self.variant_jobs:
            raise ValueError("No active batch job. Call create_batch_job() first.")

        return self.variant_jobs

    def get_batch_info(self):
        """
        Get information about the current batch job

        Returns:
            dict: Dictionary with batch information
        """
        if not self.current_batch_id:
            raise ValueError("No active batch job. Call create_batch_job() first.")

        return {
            'batch_id': self.current_batch_id,
            'batch_dir': self.current_batch_dir,
            'variant_count': self.variant_count,
            'variant_dirs': [manager.current_job_dir for manager in self.variant_jobs]
        }

    def save_job_info(self, topic, elements_count=None, generation_time=None):
        """Save job information to a text file"""
        if not self.current_job_dir:
            return
        
        paths = self.get_file_paths()
        job_info = f"""Infographic Generation Job
========================
Job ID: {self.current_job_id}
Topic: {topic}
Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}
Elements Count: {elements_count or 'N/A'}
Generation Time: {generation_time or 'N/A'}

Files:
- HTML: infographic.html
- PNG: infographic.png  
- SVG: infographic.svg
"""
        
        with open(paths['job_info'], 'w', encoding='utf-8') as f:
            f.write(job_info)
    
    def list_jobs(self, limit=10):
        """List recent jobs"""
        if not self.base_dir.exists():
            print("No jobs found.")
            return []
        
        jobs = []
        for job_dir in sorted(self.base_dir.iterdir(), reverse=True):
            if job_dir.is_dir():
                job_info_file = job_dir / "job_info.txt"
                if job_info_file.exists():
                    try:
                        with open(job_info_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                            # Extract topic from job info
                            topic_line = [line for line in content.split('\n') if line.startswith('Topic:')]
                            topic = topic_line[0].split(':', 1)[1].strip() if topic_line else "Unknown"
                            
                            jobs.append({
                                'job_id': job_dir.name,
                                'topic': topic,
                                'path': job_dir
                            })
                    except:
                        jobs.append({
                            'job_id': job_dir.name,
                            'topic': "Unknown",
                            'path': job_dir
                        })
                
                if len(jobs) >= limit:
                    break
        
        return jobs
    
    def open_job_in_browser(self, job_id=None):
        """Open a job's HTML file in browser"""
        if job_id:
            job_dir = self.base_dir / job_id
        else:
            job_dir = self.current_job_dir
        
        if not job_dir or not job_dir.exists():
            print(f"❌ Job directory not found: {job_dir}")
            return False
        
        html_file = job_dir / "infographic.html"
        if not html_file.exists():
            print(f"❌ HTML file not found: {html_file}")
            return False
        
        import webbrowser
        webbrowser.open(f'file://{html_file.absolute()}')
        print(f"🌐 Opened {html_file} in browser")
        return True
    
    def cleanup_old_jobs(self, keep_count=20):
        """Keep only the most recent jobs, delete older ones"""
        if not self.base_dir.exists():
            return
        
        jobs = sorted(self.base_dir.iterdir(), key=lambda x: x.stat().st_mtime, reverse=True)
        
        deleted_count = 0
        for job_dir in jobs[keep_count:]:
            if job_dir.is_dir():
                try:
                    shutil.rmtree(job_dir)
                    deleted_count += 1
                except Exception as e:
                    print(f"⚠️  Could not delete {job_dir}: {e}")
        
        if deleted_count > 0:
            print(f"🧹 Cleaned up {deleted_count} old jobs")


def main():
    """Command line interface for job management"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Manage infographic generation jobs')
    parser.add_argument('--list', action='store_true', help='List recent jobs')
    parser.add_argument('--open', help='Open job in browser by job ID')
    parser.add_argument('--cleanup', type=int, default=20, help='Keep only N recent jobs')
    
    args = parser.parse_args()
    
    manager = InfographicJobManager()
    
    if args.list:
        jobs = manager.list_jobs()
        if jobs:
            print("\n📋 Recent Jobs:")
            for i, job in enumerate(jobs, 1):
                print(f"{i:2d}. {job['job_id']} - {job['topic']}")
        else:
            print("No jobs found.")
    
    elif args.open:
        manager.open_job_in_browser(args.open)
    
    elif args.cleanup:
        manager.cleanup_old_jobs(args.cleanup)


if __name__ == '__main__':
    main()
