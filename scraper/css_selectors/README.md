# CSS Selectors Package

The `css_selectors` package provides dynamic CSS selector generation and management.

## Modules

### 1. Dynamic Selector (`dynamic_selector.py`)
Intelligent selector generation that adapts to different website structures.

**Key Class:** `DynamicSelector`
- **Features:**
  - Site type detection (e-commerce, blog, news, etc.)
  - Pattern-based selector generation
  - Selector scoring and optimization
  - Site-specific adaptation
  - Selector caching
  - Confidence calculation

### 2. CSS Rules (`css_rules.py`)
Defines CSS selector rules and patterns.

### 3. CSS Selector Generator (`css_selector_generator.py`)
Generates CSS selectors for web elements.

## Usage

The dynamic selector system automatically analyzes website structure and generates appropriate CSS selectors, reducing the need for manual selector configuration.
