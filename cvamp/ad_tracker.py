import json
import os
import threading
import time
from datetime import datetime


class AdTracker:
    """
    Tracks ad detection and counting for CVAmp instances
    """
    def __init__(self, ad_log_file="ad_tracking.json"):
        self.ad_log_file = ad_log_file
        self.ads_data_lock = threading.Lock()
        self.ads_data = self.load_ads_data()
        self.instance_ads_count = {}  # Tracks ads per instance
        self.instance_ad_timestamps = {}  # Tracks when ads were detected per instance

    def load_ads_data(self):
        """Load existing ads data from file"""
        if os.path.exists(self.ad_log_file):
            try:
                with open(self.ad_log_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data
            except (json.JSONDecodeError, FileNotFoundError):
                pass
        
        # Default structure
        return {
            "total_ads_detected": 0,
            "instances": {},
            "detection_log": []
        }

    def save_ads_data(self):
        """Save ads data to file"""
        with self.ads_data_lock:
            try:
                with open(self.ad_log_file, 'w', encoding='utf-8') as f:
                    json.dump(self.ads_data, f, indent=2, ensure_ascii=False)
            except Exception as e:
                print(f"Error saving ad data: {e}")

    def record_ad_detected(self, instance_id):
        """Record that an ad was detected for an instance"""
        current_time = datetime.now().isoformat()
        
        with self.ads_data_lock:
            # Update instance counter
            if str(instance_id) not in self.ads_data["instances"]:
                self.ads_data["instances"][str(instance_id)] = 0
            self.ads_data["instances"][str(instance_id)] += 1
            
            # Update total counter
            self.ads_data["total_ads_detected"] += 1
            
            # Log the detection
            detection_entry = {
                "timestamp": current_time,
                "instance_id": instance_id,
                "ad_number_for_instance": self.ads_data["instances"][str(instance_id)]
            }
            self.ads_data["detection_log"].append(detection_entry)
            
            # Keep only last 1000 entries to prevent file growing too large
            if len(self.ads_data["detection_log"]) > 1000:
                self.ads_data["detection_log"] = self.ads_data["detection_log"][-1000:]
        
        self.save_ads_data()
        
        print(f"Ad detected and recorded for instance {instance_id} at {current_time}")

    def get_instance_ad_count(self, instance_id):
        """Get number of ads detected for a specific instance"""
        with self.ads_data_lock:
            return self.ads_data["instances"].get(str(instance_id), 0)

    def get_total_ads_count(self):
        """Get total number of ads detected across all instances"""
        with self.ads_data_lock:
            return self.ads_data["total_ads_detected"]

    def get_ads_summary(self):
        """Get a summary of all ads data"""
        with self.ads_data_lock:
            return {
                "total_ads_detected": self.ads_data["total_ads_detected"],
                "instances_with_ads": dict(self.ads_data["instances"]),
                "recent_detections": self.ads_data["detection_log"][-10:]  # Last 10 detections
            }


# Global ad tracker instance (singleton pattern)
_ad_tracker_instance = None
_ad_tracker_lock = threading.Lock()


def get_ad_tracker():
    """Get the global ad tracker instance"""
    global _ad_tracker_instance
    with _ad_tracker_lock:
        if _ad_tracker_instance is None:
            _ad_tracker_instance = AdTracker()
        return _ad_tracker_instance