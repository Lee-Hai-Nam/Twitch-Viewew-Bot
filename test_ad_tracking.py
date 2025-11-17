#!/usr/bin/env python3
"""
Test script to verify the ad tracking functionality
"""
import sys
import os
import tempfile
import shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cvamp.ad_tracker import AdTracker


def test_ad_tracking():
    print("Testing ad tracking functionality...")
    
    # Create a temporary file for testing
    temp_dir = tempfile.mkdtemp()
    temp_file = os.path.join(temp_dir, "test_ads.json")
    
    try:
        # Create tracker instance
        tracker = AdTracker(ad_log_file=temp_file)
        
        print("Initial state:")
        print(f"  Total ads: {tracker.get_total_ads_count()}")
        print(f"  Instance 1 ads: {tracker.get_instance_ad_count(1)}")
        
        # Record some ads
        print("\nRecording ads...")
        tracker.record_ad_detected(1)
        tracker.record_ad_detected(2)
        tracker.record_ad_detected(1)  # Second ad for instance 1
        
        print(f"  Total ads after recording: {tracker.get_total_ads_count()}")
        print(f"  Instance 1 ads: {tracker.get_instance_ad_count(1)}")
        print(f"  Instance 2 ads: {tracker.get_instance_ad_count(2)}")
        
        # Get summary
        summary = tracker.get_ads_summary()
        print(f"\nSummary:")
        print(f"  Total ads: {summary['total_ads_detected']}")
        print(f"  Instances: {summary['instances_with_ads']}")
        print(f"  Recent detections: {len(summary['recent_detections'])}")
        
        # Verify counts are correct
        assert tracker.get_total_ads_count() == 3, f"Expected 3 total ads, got {tracker.get_total_ads_count()}"
        assert tracker.get_instance_ad_count(1) == 2, f"Expected 2 ads for instance 1, got {tracker.get_instance_ad_count(1)}"
        assert tracker.get_instance_ad_count(2) == 1, f"Expected 1 ad for instance 2, got {tracker.get_instance_ad_count(2)}"
        
        print("\nAll tests passed!")
        
        # Clean up
        shutil.rmtree(temp_dir)
        return True
        
    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()
        # Clean up even if there's an error
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        return False


if __name__ == "__main__":
    success = test_ad_tracking()
    if success:
        print("\n[SUCCESS] Ad tracking test PASSED!")
        sys.exit(0)
    else:
        print("\n[FAILED] Ad tracking test FAILED!")
        sys.exit(1)