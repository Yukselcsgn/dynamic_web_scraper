"""
CSS selector generator for the dynamic web scraper project.
"""

from bs4 import BeautifulSoup, Tag
import re
from typing import List, Dict


def generate_selector(element: Tag) -> str:
    """
    Generate a CSS selector for a given BeautifulSoup element.

    Args:
        element: BeautifulSoup Tag element

    Returns:
        str: CSS selector string
    """
    if not element or not element.name:
        return ""

    # Start with tag name
    selector = element.name

    # Add ID if present (highest specificity)
    if element.get("id"):
        return f"#{element['id']}"

    # Add classes if present
    classes = element.get("class", [])
    if classes:
        # Filter out dynamic classes (containing numbers or special chars)
        static_classes = [cls for cls in classes if not re.search(r"[0-9_]", cls)]
        if static_classes:
            selector += "." + ".".join(static_classes)

    # Add attributes for better specificity
    attributes = ["data-testid", "data-cy", "aria-label", "title"]
    for attr in attributes:
        if element.get(attr):
            selector += f'[{attr}="{element[attr]}"]'
            break

    return selector


def generate_unique_selector(element: Tag, max_parents: int = 3) -> str:
    """
    Generate a unique CSS selector by traversing up the DOM tree.

    Args:
        element: BeautifulSoup Tag element
        max_parents: Maximum number of parent elements to include

    Returns:
        str: Unique CSS selector string
    """
    if not element:
        return ""

    selectors = []
    current = element
    count = 0

    while current and current.name and count < max_parents:
        selector = generate_selector(current)
        if selector:
            selectors.append(selector)
        current = current.parent
        count += 1

    return " > ".join(reversed(selectors))


def find_product_selectors(html_content: str) -> Dict[str, List[str]]:
    """
    Automatically detect potential product-related selectors from HTML content.

    Args:
        html_content: HTML string to analyze

    Returns:
        Dict containing lists of potential selectors for different product elements
    """
    soup = BeautifulSoup(html_content, "html.parser")

    selectors = {
        "product_containers": [],
        "product_titles": [],
        "product_prices": [],
        "product_images": [],
        "product_links": [],
    }

    # Common patterns for product containers
    container_patterns = ["product", "item", "card", "listing", "goods", "merchandise"]

    # Find potential product containers
    for pattern in container_patterns:
        elements = soup.find_all(
            ["div", "article", "section"], class_=re.compile(pattern, re.I)
        )
        for element in elements:
            selector = generate_unique_selector(element)
            if selector:
                selectors["product_containers"].append(selector)

    # Find potential title elements
    title_elements = soup.find_all(
        ["h1", "h2", "h3", "h4", "span", "div"],
        class_=re.compile(r"title|name|product", re.I),
    )
    for element in title_elements:
        selector = generate_unique_selector(element)
        if selector:
            selectors["product_titles"].append(selector)

    # Find potential price elements
    price_elements = soup.find_all(
        ["span", "div", "p"], class_=re.compile(r"price|cost|amount", re.I)
    )
    for element in price_elements:
        selector = generate_unique_selector(element)
        if selector:
            selectors["product_prices"].append(selector)

    # Find potential image elements
    image_elements = soup.find_all("img", src=True)
    for element in image_elements:
        selector = generate_unique_selector(element)
        if selector:
            selectors["product_images"].append(selector)

    # Find potential link elements
    link_elements = soup.find_all("a", href=True)
    for element in link_elements:
        selector = generate_unique_selector(element)
        if selector:
            selectors["product_links"].append(selector)

    return selectors


def validate_selector(html_content: str, selector: str) -> bool:
    """
    Validate if a CSS selector works with the given HTML content.

    Args:
        html_content: HTML string to test against
        selector: CSS selector to validate

    Returns:
        bool: True if selector finds elements, False otherwise
    """
    try:
        soup = BeautifulSoup(html_content, "html.parser")
        elements = soup.select(selector)
        return len(elements) > 0
    except Exception:
        return False


def optimize_selector(html_content: str, selector: str) -> str:
    """
    Optimize a CSS selector to be more specific and reliable.

    Args:
        html_content: HTML string to analyze
        selector: Original CSS selector

    Returns:
        str: Optimized CSS selector
    """
    soup = BeautifulSoup(html_content, "html.parser")

    try:
        elements = soup.select(selector)
        if not elements:
            return selector

        # If multiple elements found, try to make it more specific
        if len(elements) > 1:
            # Try adding nth-child
            for i, element in enumerate(elements):
                parent = element.parent
                if parent:
                    child_index = list(parent.children).index(element) + 1
                    optimized = f"{selector}:nth-child({child_index})"
                    if validate_selector(html_content, optimized):
                        return optimized

        return selector
    except Exception:
        return selector
