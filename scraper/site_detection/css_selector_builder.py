"""
CSS selector builder for the dynamic web scraper project.
"""

from bs4 import BeautifulSoup, Tag
import re
from typing import List, Dict


def build_selector(element: Tag, strategy: str = "smart") -> str:
    """
    Build a CSS selector for a given element using different strategies.

    Args:
        element: BeautifulSoup Tag element
        strategy: Strategy to use ('id', 'class', 'smart', 'path')

    Returns:
        CSS selector string
    """
    if not element or not element.name:
        return ""

    if strategy == "id":
        return _build_id_selector(element)
    elif strategy == "class":
        return _build_class_selector(element)
    elif strategy == "path":
        return _build_path_selector(element)
    else:  # smart strategy
        return _build_smart_selector(element)


def _build_id_selector(element: Tag) -> str:
    """Build selector using element ID."""
    if element.get("id"):
        return f"#{element['id']}"
    return ""


def _build_class_selector(element: Tag) -> str:
    """Build selector using element classes."""
    classes = element.get("class", [])
    if not classes:
        return ""

    # Filter out dynamic classes
    static_classes = [cls for cls in classes if not _is_dynamic_class(cls)]
    if not static_classes:
        return ""

    return f"{element.name}.{'.'.join(static_classes)}"


def _build_path_selector(element: Tag, max_depth: int = 3) -> str:
    """Build selector using element path."""
    path = []
    current = element
    depth = 0

    while current and current.name and depth < max_depth:
        selector = _build_smart_selector(current)
        if selector:
            path.append(selector)
        current = current.parent
        depth += 1

    return " > ".join(reversed(path))


def _build_smart_selector(element: Tag) -> str:
    """Build selector using smart strategy (ID > class > attributes)."""
    # Try ID first (highest specificity)
    if element.get("id"):
        return f"#{element['id']}"

    # Try classes
    classes = element.get("class", [])
    if classes:
        static_classes = [cls for cls in classes if not _is_dynamic_class(cls)]
        if static_classes:
            return f"{element.name}.{'.'.join(static_classes)}"

    # Try data attributes
    data_attrs = [attr for attr in element.attrs.keys() if attr.startswith("data-")]
    for attr in data_attrs:
        if element.get(attr):
            return f"{element.name}[{attr}='{element[attr]}']"

    # Try other attributes
    for attr in ["name", "title", "alt"]:
        if element.get(attr):
            return f"{element.name}[{attr}='{element[attr]}']"

    # Fallback to tag name
    return element.name


def _is_dynamic_class(class_name: str) -> bool:
    """Check if a class name is likely dynamic/generated."""
    dynamic_patterns = [
        r"\d{4,}",  # Long numbers
        r"[a-f0-9]{8,}",  # Hash-like strings
        r"[A-Z]{2,}",  # All caps
        r"[a-z]{20,}",  # Very long lowercase
        r"[0-9_]{3,}",  # Multiple numbers/underscores
    ]

    return any(re.search(pattern, class_name) for pattern in dynamic_patterns)


def build_product_selectors(html_content: str) -> Dict[str, List[str]]:
    """
    Build selectors for common product elements.

    Args:
        html_content: HTML content to analyze

    Returns:
        Dictionary with element types and their selectors
    """
    soup = BeautifulSoup(html_content, "html.parser")

    selectors = {
        "containers": [],
        "titles": [],
        "prices": [],
        "images": [],
        "links": [],
        "descriptions": [],
    }

    # Find product containers
    container_patterns = [
        r"product",
        r"item",
        r"card",
        r"listing",
        r"goods",
        r"product-item",
        r"product-card",
        r"item-card",
    ]

    for pattern in container_patterns:
        elements = soup.find_all(
            ["div", "article", "section"], class_=re.compile(pattern, re.I)
        )
        for element in elements:
            selector = build_selector(element, "smart")
            if selector and selector not in selectors["containers"]:
                selectors["containers"].append(selector)

    # Find product titles
    title_elements = soup.find_all(
        ["h1", "h2", "h3", "h4", "span", "div"],
        class_=re.compile(r"title|name|product", re.I),
    )
    for element in title_elements:
        selector = build_selector(element, "smart")
        if selector and selector not in selectors["titles"]:
            selectors["titles"].append(selector)

    # Find product prices
    price_elements = soup.find_all(
        ["span", "div", "p"], class_=re.compile(r"price|cost|amount", re.I)
    )
    for element in price_elements:
        selector = build_selector(element, "smart")
        if selector and selector not in selectors["prices"]:
            selectors["prices"].append(selector)

    # Find product images
    image_elements = soup.find_all("img", src=True)
    for element in image_elements:
        selector = build_selector(element, "smart")
        if selector and selector not in selectors["images"]:
            selectors["images"].append(selector)

    # Find product links
    link_elements = soup.find_all("a", href=True)
    for element in link_elements:
        selector = build_selector(element, "smart")
        if selector and selector not in selectors["links"]:
            selectors["links"].append(selector)

    # Find product descriptions
    desc_elements = soup.find_all(
        ["p", "div", "span"], class_=re.compile(r"description|desc|summary", re.I)
    )
    for element in desc_elements:
        selector = build_selector(element, "smart")
        if selector and selector not in selectors["descriptions"]:
            selectors["descriptions"].append(selector)

    return selectors


def build_unique_selector(element: Tag, context_elements: List[Tag] = None) -> str:
    """
    Build a unique selector that identifies the element among similar elements.

    Args:
        element: Target element
        context_elements: List of similar elements for comparison

    Returns:
        Unique CSS selector
    """
    if not element:
        return ""

    # Try different strategies in order of preference
    strategies = ["id", "smart", "path"]

    for strategy in strategies:
        selector = build_selector(element, strategy)
        if not selector:
            continue

        # Check if this selector is unique
        if context_elements:
            matches = [e for e in context_elements if e.select(selector)]
            if len(matches) == 1:
                return selector
        else:
            return selector

    # If no unique selector found, build a more specific path
    return _build_path_selector(element, max_depth=5)


def build_adaptive_selector(element: Tag, html_content: str) -> str:
    """
    Build an adaptive selector that works across different page states.

    Args:
        element: Target element
        html_content: Full HTML content for context

    Returns:
        Adaptive CSS selector
    """
    BeautifulSoup(html_content, "html.parser")

    # Start with smart selector
    base_selector = build_selector(element, "smart")
    if not base_selector:
        return ""

    # Check if selector is too specific (might break with dynamic content)
    if _is_too_specific(base_selector):
        # Try to make it more flexible
        return _make_selector_flexible(base_selector, element)

    return base_selector


def _is_too_specific(selector: str) -> bool:
    """Check if a selector is too specific and might break with dynamic content."""
    # Count specific attributes
    specific_attrs = selector.count("[") + selector.count("#")
    return specific_attrs > 2


def _make_selector_flexible(selector: str, element: Tag) -> str:
    """Make a selector more flexible for dynamic content."""
    # Remove specific attributes, keep only essential ones
    if "[" in selector:
        # Keep only data-* attributes and essential ones
        parts = selector.split("[")
        base = parts[0]

        for part in parts[1:]:
            if "]" in part:
                attr_part = part.split("]")[0]
                if attr_part.startswith("data-") or attr_part.startswith("class="):
                    base += f"[{attr_part}]"

        return base

    return selector


def validate_selector_stability(
    selector: str, html_content: str, iterations: int = 3
) -> float:
    """
    Validate the stability of a selector across multiple checks.

    Args:
        selector: CSS selector to test
        html_content: HTML content to test against
        iterations: Number of iterations to test

    Returns:
        Stability score between 0 and 1
    """
    soup = BeautifulSoup(html_content, "html.parser")

    try:
        elements = soup.select(selector)
        if not elements:
            return 0.0

        # Count elements found
        element_count = len(elements)

        # Check if elements have consistent structure
        consistent_count = 0
        for _ in range(iterations):
            try:
                current_elements = soup.select(selector)
                if len(current_elements) == element_count:
                    consistent_count += 1
            except Exception:
                pass

        stability = consistent_count / iterations

        # Bonus for finding multiple elements (indicates good pattern)
        if element_count > 1:
            stability += 0.2

        return min(1.0, stability)

    except Exception:
        return 0.0
