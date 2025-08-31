#!/usr/bin/env python3
"""
Human Behavior Simulator

This module implements realistic human behavior patterns for web scraping
to avoid detection by anti-bot systems.
"""

import logging
import random
import time
from typing import Dict, List, Optional, Tuple

# Import log_message for consistent logging
try:
    from scraper.logging_manager.logging_manager import log_message
except ImportError:

    def log_message(level, message):
        logging.log(getattr(logging, level.upper(), logging.INFO), message)


class HumanBehaviorSimulator:
    """
    Simulates realistic human behavior patterns for web scraping.
    """

    def __init__(self, config: Dict = None):
        """
        Initialize the human behavior simulator.

        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.session_start_time = time.time()
        self.request_count = 0
        self.last_request_time = 0

        # Human behavior patterns
        self.reading_speeds = {
            "fast": (0.5, 1.5),  # Fast reader
            "normal": (1.0, 3.0),  # Normal reader
            "slow": (2.0, 5.0),  # Slow reader
        }

        self.scroll_patterns = [
            "smooth",  # Smooth scrolling
            "jerky",  # Jerky scrolling
            "pause",  # Pause and read
            "quick",  # Quick scroll through
        ]

        self.mouse_movements = [
            "linear",  # Straight line movement
            "curved",  # Curved movement
            "hesitant",  # Hesitant movement
            "confident",  # Confident movement
        ]

    def get_reading_speed(self) -> str:
        """Get a realistic reading speed based on user behavior."""
        # Most users are normal readers
        weights = {"fast": 0.2, "normal": 0.6, "slow": 0.2}
        return random.choices(list(weights.keys()), weights=list(weights.values()))[0]

    def calculate_reading_time(
        self, text_length: int, reading_speed: str = None
    ) -> float:
        """
        Calculate realistic reading time based on text length.

        Args:
            text_length: Length of text to read
            reading_speed: Reading speed preference

        Returns:
            Reading time in seconds
        """
        if reading_speed is None:
            reading_speed = self.get_reading_speed()

        # Average reading speed: 200-300 words per minute
        # Assume average word length of 5 characters
        words = text_length / 5
        words_per_minute = random.randint(200, 300)

        base_time = (words / words_per_minute) * 60

        # Add variation based on reading speed
        min_time, max_time = self.reading_speeds[reading_speed]
        variation = random.uniform(min_time, max_time)

        return max(base_time, variation)

    def simulate_reading_behavior(self, text_length: int = None) -> float:
        """
        Simulate realistic reading behavior with pauses and variations.

        Args:
            text_length: Length of text to read (optional)

        Returns:
            Total time spent reading
        """
        if text_length is None:
            text_length = random.randint(100, 1000)

        reading_speed = self.get_reading_speed()
        base_time = self.calculate_reading_time(text_length, reading_speed)

        # Add micro-pauses for more realistic behavior
        micro_pauses = random.randint(2, 5)
        for _ in range(micro_pauses):
            pause_time = random.uniform(0.1, 0.5)
            time.sleep(pause_time)
            base_time += pause_time

        # Add occasional longer pauses (user thinking/processing)
        if random.random() < 0.3:  # 30% chance
            thinking_pause = random.uniform(1.0, 3.0)
            time.sleep(thinking_pause)
            base_time += thinking_pause

        return base_time

    def simulate_scroll_behavior(self, scroll_distance: int = None) -> float:
        """
        Simulate realistic scrolling behavior.

        Args:
            scroll_distance: Distance to scroll (optional)

        Returns:
            Time spent scrolling
        """
        if scroll_distance is None:
            scroll_distance = random.randint(200, 800)

        pattern = random.choice(self.scroll_patterns)
        total_time = 0

        if pattern == "smooth":
            # Smooth scrolling with small increments
            steps = random.randint(10, 20)
            step_size = scroll_distance // steps
            for _ in range(steps):
                time.sleep(random.uniform(0.05, 0.15))
                total_time += 0.1

        elif pattern == "jerky":
            # Jerky scrolling with irregular pauses
            steps = random.randint(5, 10)
            step_size = scroll_distance // steps
            for _ in range(steps):
                time.sleep(random.uniform(0.1, 0.4))
                total_time += 0.25

        elif pattern == "pause":
            # Pause and read while scrolling
            steps = random.randint(3, 6)
            step_size = scroll_distance // steps
            for _ in range(steps):
                time.sleep(random.uniform(0.2, 0.5))
                # Simulate reading pause
                if random.random() < 0.4:
                    reading_pause = random.uniform(1.0, 2.5)
                    time.sleep(reading_pause)
                    total_time += reading_pause
                total_time += 0.35

        elif pattern == "quick":
            # Quick scroll through
            steps = random.randint(3, 5)
            step_size = scroll_distance // steps
            for _ in range(steps):
                time.sleep(random.uniform(0.05, 0.1))
                total_time += 0.075

        return total_time

    def simulate_mouse_movement(
        self, start_pos: Tuple[int, int], end_pos: Tuple[int, int]
    ) -> float:
        """
        Simulate realistic mouse movement between two points.

        Args:
            start_pos: Starting position (x, y)
            end_pos: Ending position (x, y)

        Returns:
            Time spent moving mouse
        """
        pattern = random.choice(self.mouse_movements)

        # Calculate distance
        distance = (
            (end_pos[0] - start_pos[0]) ** 2 + (end_pos[1] - start_pos[1]) ** 2
        ) ** 0.5

        if pattern == "linear":
            # Straight line movement
            speed = random.uniform(0.5, 1.5)  # pixels per millisecond
            movement_time = distance / (speed * 1000)

        elif pattern == "curved":
            # Curved movement (longer path)
            curved_distance = distance * random.uniform(1.2, 1.8)
            speed = random.uniform(0.3, 1.0)
            movement_time = curved_distance / (speed * 1000)

        elif pattern == "hesitant":
            # Hesitant movement with pauses
            speed = random.uniform(0.2, 0.8)
            movement_time = distance / (speed * 1000)
            # Add hesitation pauses
            hesitation_pauses = random.randint(1, 3)
            for _ in range(hesitation_pauses):
                pause_time = random.uniform(0.1, 0.3)
                movement_time += pause_time

        elif pattern == "confident":
            # Confident, fast movement
            speed = random.uniform(1.0, 2.0)
            movement_time = distance / (speed * 1000)

        # Ensure minimum movement time
        movement_time = max(movement_time, 0.1)

        # Add small random variations
        variation = random.uniform(0.8, 1.2)
        movement_time *= variation

        return movement_time

    def simulate_typing_behavior(self, text: str) -> float:
        """
        Simulate realistic typing behavior.

        Args:
            text: Text to type

        Returns:
            Time spent typing
        """
        # Average typing speed: 40-80 words per minute
        words = len(text.split())
        wpm = random.randint(40, 80)
        base_time = (words / wpm) * 60

        # Add variation for different typing speeds
        typing_speed_variation = random.uniform(0.7, 1.3)
        base_time *= typing_speed_variation

        # Add pauses for thinking/editing
        thinking_pauses = random.randint(0, 3)
        for _ in range(thinking_pauses):
            pause_time = random.uniform(0.5, 2.0)
            base_time += pause_time

        # Add occasional typos and corrections
        if random.random() < 0.1:  # 10% chance of typo
            typo_correction_time = random.uniform(1.0, 3.0)
            base_time += typo_correction_time

        return base_time

    def simulate_page_interaction(self, page_type: str = "general") -> Dict[str, float]:
        """
        Simulate realistic page interaction behavior.

        Args:
            page_type: Type of page (e.g., "ecommerce", "news", "form")

        Returns:
            Dictionary with interaction times
        """
        interactions = {}

        if page_type == "ecommerce":
            # E-commerce page behavior
            interactions["page_load_wait"] = random.uniform(2.0, 5.0)
            interactions["product_browse"] = random.uniform(10.0, 30.0)
            interactions["price_check"] = random.uniform(3.0, 8.0)
            interactions["image_view"] = random.uniform(2.0, 6.0)
            interactions["scroll_behavior"] = random.uniform(5.0, 15.0)

        elif page_type == "news":
            # News page behavior
            interactions["page_load_wait"] = random.uniform(1.0, 3.0)
            interactions["article_read"] = random.uniform(15.0, 45.0)
            interactions["headline_scan"] = random.uniform(5.0, 12.0)
            interactions["scroll_behavior"] = random.uniform(3.0, 10.0)

        elif page_type == "form":
            # Form page behavior
            interactions["page_load_wait"] = random.uniform(1.0, 2.0)
            interactions["form_reading"] = random.uniform(5.0, 15.0)
            interactions["field_filling"] = random.uniform(10.0, 25.0)
            interactions["form_review"] = random.uniform(3.0, 8.0)

        else:
            # General page behavior
            interactions["page_load_wait"] = random.uniform(1.0, 4.0)
            interactions["content_read"] = random.uniform(5.0, 20.0)
            interactions["scroll_behavior"] = random.uniform(3.0, 12.0)
            interactions["navigation"] = random.uniform(2.0, 6.0)

        return interactions

    def get_session_behavior(self) -> Dict[str, any]:
        """
        Get realistic session behavior patterns.

        Returns:
            Dictionary with session behavior data
        """
        session_duration = time.time() - self.session_start_time

        # Simulate different user types
        user_types = ["casual", "focused", "researcher", "shopper"]
        user_type = random.choice(user_types)

        behavior = {
            "user_type": user_type,
            "session_duration": session_duration,
            "request_count": self.request_count,
            "avg_time_between_requests": (
                (time.time() - self.last_request_time) / max(self.request_count, 1)
            ),
            "reading_speed": self.get_reading_speed(),
            "scroll_pattern": random.choice(self.scroll_patterns),
            "mouse_pattern": random.choice(self.mouse_movements),
        }

        return behavior

    def simulate_realistic_delay(self, context: str = "general") -> float:
        """
        Simulate realistic delay based on context.

        Args:
            context: Context of the delay (e.g., "page_load", "form_fill", "reading")

        Returns:
            Delay time in seconds
        """
        if context == "page_load":
            # Wait for page to load
            delay = random.uniform(1.0, 4.0)

        elif context == "form_fill":
            # Time to fill out forms
            delay = random.uniform(3.0, 8.0)

        elif context == "reading":
            # Time to read content
            delay = random.uniform(2.0, 6.0)

        elif context == "navigation":
            # Time to navigate between pages
            delay = random.uniform(1.0, 3.0)

        elif context == "thinking":
            # Time to think/process information
            delay = random.uniform(0.5, 2.0)

        else:
            # General delay
            delay = random.uniform(1.0, 3.0)

        # Add micro-variations for more human-like behavior
        micro_variations = random.randint(1, 3)
        for _ in range(micro_variations):
            micro_delay = random.uniform(0.1, 0.3)
            time.sleep(micro_delay)
            delay += micro_delay

        time.sleep(delay)
        return delay

    def update_session_stats(self):
        """Update session statistics."""
        self.request_count += 1
        self.last_request_time = time.time()

    def get_realistic_headers(self, url: str) -> Dict[str, str]:
        """
        Generate realistic headers based on user behavior.

        Args:
            url: Target URL

        Returns:
            Dictionary of realistic headers
        """
        # Get session behavior
        behavior = self.get_session_behavior()

        # Base headers
        headers = {
            "User-Agent": random.choice(
                [
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                ]
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": random.choice(
                [
                    "en-US,en;q=0.9",
                    "en-GB,en;q=0.9",
                    "tr-TR,tr;q=0.9,en;q=0.8",
                ]
            ),
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": random.choice(["1", "0"]),
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Cache-Control": "max-age=0",
        }

        # Add referer based on user behavior
        if behavior["user_type"] == "shopper":
            headers["Referer"] = "https://www.google.com/"
        elif behavior["user_type"] == "researcher":
            headers["Referer"] = "https://www.google.com/search?q=research"
        else:
            headers["Referer"] = "https://www.google.com/"

        return headers
