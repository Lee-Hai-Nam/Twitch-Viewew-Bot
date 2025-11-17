import logging
from playwright.sync_api import Page
from typing import Optional, Dict, Any
import re


logger = logging.getLogger(__name__)


class AdDetector:
    """
    Detects ads on various streaming platforms by analyzing page content and elements
    """
    
    def __init__(self, page: Page):
        self.page = page
        self.platform_patterns = {
            'twitch': self._detect_twitch_ads,
            'youtube': self._detect_youtube_ads,
            'kick': self._detect_kick_ads,
            'chzzk': self._detect_chzzk_ads,
        }
    
    def detect_ads(self, platform: str) -> bool:
        """
        Detect if an ad is currently playing based on the platform
        """
        detector = self.platform_patterns.get(platform.lower())
        if detector:
            try:
                return detector()
            except Exception as e:
                logger.warning(f"Ad detection error for {platform}: {e}")
                return False
        else:
            logger.warning(f"No ad detector for platform: {platform}")
            return False

    def _detect_twitch_ads(self) -> bool:
        """
        Detect ads on Twitch by looking for ad-related elements and classes
        """
        try:
            # Check for ad player elements
            ad_selectors = [
                "div[data-a-target='player-overlay'] button[data-a-target*='skip']",
                "div[data-test-selector='skip-button-container']",
                "button[aria-label*='Skip' i]",
                "div[data-a-target='player-ad-overlay']",
                "div[class*='ad']",
                "div[class*='commercial']",
            ]
            
            for selector in ad_selectors:
                try:
                    element = self.page.query_selector(selector)
                    if element:
                        # If we find a skip button or ad element, likely an ad is playing
                        # But let's also check if the skip button is clickable (not disabled)
                        if 'skip' in selector.lower():
                            is_disabled = element.get_attribute('disabled')
                            if not is_disabled:
                                return True
                        else:
                            return True
                except:
                    continue
            
            # Check for ad-related text
            try:
                content = self.page.content().lower()
                ad_indicators = ['ad', 'commercial', 'sponsor', 'skip ad', 'skip commercial']
                for indicator in ad_indicators:
                    if indicator in content:
                        return True
            except:
                pass
            
            # Look for specific Twitch ad elements that might not have specific selectors yet
            try:
                ad_elements = self.page.query_selector_all("div[class*='ad' i], div[class*='commercial' i]")
                if ad_elements and len(ad_elements) > 0:
                    # Verify it's actually an ad and not just containing the word
                    for element in ad_elements:
                        class_name = element.get_attribute('class') or ''
                        if any(keyword in class_name.lower() for keyword in ['ad', 'commercial']):
                            # Check if it's likely a real ad (has video or overlay indicators)
                            return True
            except:
                pass
            
            return False
        except Exception as e:
            logger.warning(f"Twitch ad detection error: {e}")
            return False

    def _detect_youtube_ads(self) -> bool:
        """
        Detect ads on YouTube by looking for ad-related elements and classes
        """
        try:
            # Common YouTube ad selectors
            ad_selectors = [
                "button.ytp-ad-skip-button",  # Skip button
                "button.ytp-ad-skip-button-modern",  # Modern skip button
                "div.ytp-ad-overlay-container",  # Ad overlay
                "div.ytp-ad-text",  # Ad text
                "span.ytp-ad-skip-button-text",  # Skip button text
                "div[data-title*='Advertisement']",  # Ad in title area
                "div.ytp-ad-player-overlay",  # Ad player overlay
                "span.ytp-ad-duration-remaining",  # Time remaining for ad
            ]
            
            for selector in ad_selectors:
                try:
                    element = self.page.query_selector(selector)
                    if element:
                        # Check if skip button is visible and clickable
                        if 'skip' in selector.lower():
                            # Check if element is visible and not disabled
                            is_visible = element.is_visible()
                            is_disabled = element.get_attribute('disabled')
                            if is_visible and not is_disabled:
                                return True
                        else:
                            return True
                except:
                    continue
            
            # Check for ad-related text content
            try:
                content = self.page.content().lower()
                ad_indicators = [
                    'advertisement', 'ad is playing', 'skip ad', 'to skip the ad',
                    'you can skip this ad in', 'sponsor', 'paid promotion'
                ]
                for indicator in ad_indicators:
                    if indicator in content:
                        return True
            except:
                pass
            
            # Look for specific YouTube ad elements by class
            try:
                ad_elements = self.page.query_selector_all(
                    "div.ytp-ad, div.ad-container, div.ad-display, div.video-ads"
                )
                for element in ad_elements:
                    if element.is_visible():
                        return True
            except:
                pass
            
            return False
        except Exception as e:
            logger.warning(f"YouTube ad detection error: {e}")
            return False

    def _detect_kick_ads(self) -> bool:
        """
        Detect ads on Kick by looking for ad-related elements and classes
        """
        try:
            # Kick-specific ad selectors (Kick may have different ad implementations)
            ad_selectors = [
                "button[data-testid*='skip' i]",  # Skip button
                "div[data-testid*='ad' i]",  # Ad-related divs
                "div[class*='ad' i]",  # Any div with 'ad' in class
                "div[class*='commercial' i]",  # Commercial breaks
            ]
            
            for selector in ad_selectors:
                try:
                    element = self.page.query_selector(selector)
                    if element and element.is_visible():
                        # Check if it's an ad skip button
                        if 'skip' in selector.lower():
                            # If skip button is visible, likely an ad is playing
                            return True
                        else:
                            return True
                except:
                    continue
            
            # Check page content for ad indicators
            try:
                content = self.page.content().lower()
                ad_indicators = ['ad', 'commercial', 'sponsor', 'skip', 'advertisement']
                for indicator in ad_indicators:
                    if indicator in content and ('skip' in content or 'advertisement' in content):
                        return True
            except:
                pass
            
            return False
        except Exception as e:
            logger.warning(f"Kick ad detection error: {e}")
            return False

    def _detect_chzzk_ads(self) -> bool:
        """
        Detect ads on Chzzk by looking for ad-related elements and classes
        """
        try:
            # Chzzk-specific ad selectors
            ad_selectors = [
                "button.btn_skip",  # Chzzk skip button (already handled in sites.py)
                "div.ad-container",  # General ad container
                "div[data-ad]",  # Data attribute indicating ad
                "div[class*='ad' i]",  # Any div with 'ad' in class
            ]
            
            for selector in ad_selectors:
                try:
                    element = self.page.query_selector(selector)
                    if element and element.is_visible():
                        if 'skip' in selector.lower():
                            # If skip button exists and is clickable, there's an ad
                            return True
                        else:
                            return True
                except:
                    continue
            
            # Check for ad-related content
            try:
                content = self.page.content().lower()
                ad_indicators = ['ad', 'advertisement', 'commercial', 'sponsor']
                for indicator in ad_indicators:
                    if indicator in content:
                        return True
            except:
                pass
            
            return False
        except Exception as e:
            logger.warning(f"Chzzk ad detection error: {e}")
            return False


def detect_ads_on_page(page: Page, platform: str) -> bool:
    """
    Convenience function to detect ads on a page
    """
    detector = AdDetector(page)
    return detector.detect_ads(platform)