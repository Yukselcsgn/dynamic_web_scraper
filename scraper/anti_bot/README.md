# Anti-Bot Package

The `anti_bot` package provides advanced anti-bot evasion techniques to bypass protection systems like Cloudflare, CAPTCHAs, and browser fingerprinting detection.

## Modules

### 1. Stealth Manager (`stealth_manager.py`)
Core anti-bot manager that orchestrates various evasion techniques.

**Key Classes:**
- **`StealthProfile`**: Configuration profiles for different stealth behaviors
  - Defines user agents, headers, timing, mouse movements, fingerprinting, etc.
- **`StealthManager`**: Main manager class
  - **Features:**
    - Multiple stealth profiles (aggressive, moderate, minimal)
    - Browser fingerprint generation
    - Human-like timing and behavior
    - Session management with request limits
    - Browser automation with stealth techniques
    - Cloudflare bypass integration

### 2. Cloudflare Bypass (`cloudflare_bypass.py`)
Specialized module for bypassing Cloudflare protection.

**Key Class:** `CloudflareBypass`
- **Features:**
  - Multiple bypass methods (cloudscraper, Playwright, requests-html)
  - Realistic browser headers and timing
  - Challenge page detection
  - Automatic retry logic
  - Cookie and session persistence

### 3. Human Behavior Simulator (`human_behavior.py`)
Simulates realistic human interactions to avoid detection.

**Key Class:** `HumanBehaviorSimulator`
- **Features:**
  - Reading behavior simulation (with pauses and variations)
  - Realistic scrolling patterns
  - Mouse movement simulation
  - Typing behavior with delays
  - Page interaction patterns
  - Context-aware delays
  - Realistic header generation

## Usage

The anti-bot modules work together to provide comprehensive evasion:
1. `StealthManager` selects an appropriate profile based on the target site
2. `CloudflareBypass` handles specific Cloudflare challenges
3. `HumanBehaviorSimulator` adds realistic delays and patterns to avoid detection
