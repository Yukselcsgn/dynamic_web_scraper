# Copyright 2024 Yüksel Coşgun
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
HTML analysis utilities for the dynamic web scraper project.
"""

import re
from typing import Any, Dict

from bs4 import BeautifulSoup


def analyze_html(html_content: str, url: str = "") -> Dict[str, Any]:
    """
    Analyze HTML content and extract useful information for web scraping.

    Args:
        html_content: HTML content to analyze
        url: URL of the page (optional, for context)

    Returns:
        Dictionary containing analysis results
    """
    soup = BeautifulSoup(html_content, "html.parser")

    analysis = {
        "page_info": _analyze_page_info(soup, url),
        "structure": _analyze_structure(soup),
        "content": _analyze_content(soup),
        "forms": _analyze_forms(soup),
        "links": _analyze_links(soup, url),
        "images": _analyze_images(soup, url),
        "scripts": _analyze_scripts(soup),
        "meta": _analyze_meta_tags(soup),
        "accessibility": _analyze_accessibility(soup),
        "performance": _analyze_performance(soup),
    }

    return analysis


def _analyze_page_info(soup: BeautifulSoup, url: str) -> Dict[str, Any]:
    """Analyze basic page information."""
    info = {
        "title": "",
        "description": "",
        "keywords": "",
        "language": "",
        "charset": "",
        "viewport": "",
        "robots": "",
        "canonical": "",
    }

    # Title
    title_tag = soup.find("title")
    if title_tag:
        info["title"] = title_tag.get_text(strip=True)

    # Meta tags
    meta_tags = soup.find_all("meta")
    for meta in meta_tags:
        name = meta.get("name", "").lower()
        content = meta.get("content", "")

        if name == "description":
            info["description"] = content
        elif name == "keywords":
            info["keywords"] = content
        elif name == "robots":
            info["robots"] = content
        elif name == "viewport":
            info["viewport"] = content

    # Language
    html_tag = soup.find("html")
    if html_tag:
        info["language"] = html_tag.get("lang", "")

    # Charset
    charset_meta = soup.find("meta", charset=True)
    if charset_meta:
        info["charset"] = charset_meta.get("charset", "")

    # Canonical URL
    canonical = soup.find("link", rel="canonical")
    if canonical:
        info["canonical"] = canonical.get("href", "")

    return info


def _analyze_structure(soup: BeautifulSoup) -> Dict[str, Any]:
    """Analyze page structure and layout."""
    structure = {
        "headings": {},
        "sections": [],
        "navigation": [],
        "main_content": [],
        "sidebar": [],
        "footer": [],
    }

    # Analyze headings
    for i in range(1, 7):
        headings = soup.find_all(f"h{i}")
        structure["headings"][f"h{i}"] = len(headings)

    # Analyze sections
    sections = soup.find_all(
        ["section", "article", "main", "aside", "nav", "header", "footer"]
    )
    for section in sections:
        section_info = {
            "tag": section.name,
            "id": section.get("id", ""),
            "classes": section.get("class", []),
            "text_length": len(section.get_text(strip=True)),
        }
        structure["sections"].append(section_info)

    # Identify navigation
    nav_elements = soup.find_all(
        ["nav", "ul", "ol"], class_=re.compile(r"nav|menu|navigation", re.I)
    )
    for nav in nav_elements:
        links = nav.find_all("a", href=True)
        if links:
            structure["navigation"].append(
                {
                    "element": nav.name,
                    "link_count": len(links),
                    "links": [link.get("href") for link in links],
                }
            )

    return structure


def _analyze_content(soup: BeautifulSoup) -> Dict[str, Any]:
    """Analyze page content and text."""
    content = {
        "text_stats": {},
        "paragraphs": [],
        "lists": [],
        "tables": [],
        "product_indicators": [],
    }

    # Text statistics
    text = soup.get_text(strip=True)
    content["text_stats"] = {
        "total_length": len(text),
        "word_count": len(text.split()),
        "line_count": len(text.split("\n")),
        "character_count": len(text.replace(" ", "")),
    }

    # Paragraphs
    paragraphs = soup.find_all("p")
    content["paragraphs"] = [
        {
            "text": (
                p.get_text(strip=True)[:100] + "..."
                if len(p.get_text(strip=True)) > 100
                else p.get_text(strip=True)
            ),
            "length": len(p.get_text(strip=True)),
        }
        for p in paragraphs[:10]
    ]  # Limit to first 10

    # Lists
    lists = soup.find_all(["ul", "ol"])
    content["lists"] = [
        {
            "type": lst.name,
            "item_count": len(lst.find_all("li")),
            "items": [li.get_text(strip=True)[:50] for li in lst.find_all("li")[:5]],
        }
        for lst in lists[:5]
    ]

    # Tables
    tables = soup.find_all("table")
    content["tables"] = [
        {
            "rows": len(table.find_all("tr")),
            "columns": len(table.find_all("th"))
            or len(table.find_all("td")) // max(len(table.find_all("tr")), 1),
        }
        for table in tables
    ]

    # Product indicators
    product_keywords = [
        "price",
        "buy",
        "add to cart",
        "product",
        "item",
        "sale",
        "discount",
    ]
    text_lower = text.lower()
    content["product_indicators"] = [
        keyword for keyword in product_keywords if keyword in text_lower
    ]

    return content


def _analyze_forms(soup: BeautifulSoup) -> Dict[str, Any]:
    """Analyze forms on the page."""
    forms = soup.find_all("form")
    form_analysis = {"count": len(forms), "forms": []}

    for form in forms:
        form_info = {
            "action": form.get("action", ""),
            "method": form.get("method", "get"),
            "inputs": [],
            "buttons": [],
        }

        # Analyze inputs
        inputs = form.find_all("input")
        for inp in inputs:
            input_info = {
                "type": inp.get("type", "text"),
                "name": inp.get("name", ""),
                "id": inp.get("id", ""),
                "required": inp.get("required") is not None,
            }
            form_info["inputs"].append(input_info)

        # Analyze buttons
        buttons = form.find_all(["button", "input"], type=["submit", "button"])
        for btn in buttons:
            button_info = {
                "type": btn.get("type", "button"),
                "text": btn.get_text(strip=True) or btn.get("value", ""),
                "name": btn.get("name", ""),
            }
            form_info["buttons"].append(button_info)

        form_analysis["forms"].append(form_info)

    return form_analysis


def _analyze_links(soup: BeautifulSoup, base_url: str) -> Dict[str, Any]:
    """Analyze links on the page."""
    links = soup.find_all("a", href=True)
    link_analysis = {
        "total_count": len(links),
        "internal_links": [],
        "external_links": [],
        "link_types": {},
    }

    for link in links:
        href = link.get("href", "")
        text = link.get_text(strip=True)

        # Categorize links
        if href.startswith("http"):
            link_analysis["external_links"].append({"url": href, "text": text[:50]})
        elif href.startswith("/") or href.startswith("#"):
            link_analysis["internal_links"].append({"url": href, "text": text[:50]})

        # Analyze link types
        if "product" in href.lower() or "item" in href.lower():
            link_analysis["link_types"]["product"] = (
                link_analysis["link_types"].get("product", 0) + 1
            )
        elif "category" in href.lower():
            link_analysis["link_types"]["category"] = (
                link_analysis["link_types"].get("category", 0) + 1
            )

    return link_analysis


def _analyze_images(soup: BeautifulSoup, base_url: str) -> Dict[str, Any]:
    """Analyze images on the page."""
    images = soup.find_all("img")
    image_analysis = {
        "total_count": len(images),
        "with_src": 0,
        "with_alt": 0,
        "with_title": 0,
        "product_images": [],
    }

    for img in images:
        if img.get("src"):
            image_analysis["with_src"] += 1

        if img.get("alt"):
            image_analysis["with_alt"] += 1

        if img.get("title"):
            image_analysis["with_title"] += 1

        # Check for product images
        src = img.get("src", "")
        alt = img.get("alt", "")
        classes = img.get("class", [])

        if any(
            keyword in src.lower()
            or keyword in alt.lower()
            or any(keyword in cls.lower() for cls in classes)
            for keyword in ["product", "item", "goods"]
        ):
            image_analysis["product_images"].append(
                {"src": src, "alt": alt, "classes": classes}
            )

    return image_analysis


def _analyze_scripts(soup: BeautifulSoup) -> Dict[str, Any]:
    """Analyze scripts on the page."""
    scripts = soup.find_all("script")
    script_analysis = {
        "total_count": len(scripts),
        "external_scripts": [],
        "inline_scripts": [],
        "frameworks": [],
    }

    for script in scripts:
        src = script.get("src", "")

        if src:
            script_analysis["external_scripts"].append(src)

            # Detect frameworks
            if "jquery" in src.lower():
                script_analysis["frameworks"].append("jQuery")
            elif "react" in src.lower():
                script_analysis["frameworks"].append("React")
            elif "vue" in src.lower():
                script_analysis["frameworks"].append("Vue")
            elif "angular" in src.lower():
                script_analysis["frameworks"].append("Angular")
        else:
            # Inline script
            script_content = script.get_text()
            script_analysis["inline_scripts"].append(
                {
                    "length": len(script_content),
                    "preview": (
                        script_content[:100] + "..."
                        if len(script_content) > 100
                        else script_content
                    ),
                }
            )

    return script_analysis


def _analyze_meta_tags(soup: BeautifulSoup) -> Dict[str, Any]:
    """Analyze meta tags for SEO and social media."""
    meta_tags = soup.find_all("meta")
    meta_analysis = {"seo_tags": {}, "social_tags": {}, "other_tags": {}}

    for meta in meta_tags:
        name = meta.get("name", "").lower()
        property = meta.get("property", "").lower()
        content = meta.get("content", "")

        if name in ["description", "keywords", "author", "robots"]:
            meta_analysis["seo_tags"][name] = content
        elif property.startswith("og:") or property.startswith("twitter:"):
            meta_analysis["social_tags"][property] = content
        else:
            meta_analysis["other_tags"][name or property] = content

    return meta_analysis


def _analyze_accessibility(soup: BeautifulSoup) -> Dict[str, Any]:
    """Analyze accessibility features."""
    accessibility = {
        "alt_text_coverage": 0,
        "aria_labels": [],
        "semantic_elements": [],
        "accessibility_issues": [],
    }

    # Check alt text coverage
    images = soup.find_all("img")
    images_with_alt = soup.find_all("img", alt=True)
    if images:
        accessibility["alt_text_coverage"] = len(images_with_alt) / len(images)

    # Check ARIA labels
    aria_elements = soup.find_all(attrs={"aria-label": True})
    accessibility["aria_labels"] = [elem.get("aria-label") for elem in aria_elements]

    # Check semantic elements
    semantic_tags = ["header", "nav", "main", "article", "section", "aside", "footer"]
    for tag in semantic_tags:
        elements = soup.find_all(tag)
        if elements:
            accessibility["semantic_elements"].append(
                {"tag": tag, "count": len(elements)}
            )

    return accessibility


def _analyze_performance(soup: BeautifulSoup) -> Dict[str, Any]:
    """Analyze potential performance issues."""
    performance = {
        "large_images": [],
        "external_resources": [],
        "inline_styles": 0,
        "performance_issues": [],
    }

    # Check for large images
    images = soup.find_all("img")
    for img in images:
        src = img.get("src", "")
        if src and not src.startswith("data:"):
            # This would need actual image size checking in a real implementation
            performance["large_images"].append(src)

    # Check external resources
    external_resources = soup.find_all(["link", "script"], src=True)
    external_resources.extend(soup.find_all(["link", "script"], href=True))

    for resource in external_resources:
        src = resource.get("src") or resource.get("href", "")
        if src and src.startswith("http"):
            performance["external_resources"].append(src)

    # Check inline styles
    elements_with_style = soup.find_all(style=True)
    performance["inline_styles"] = len(elements_with_style)

    return performance


def detect_ecommerce_patterns(html_content: str) -> Dict[str, Any]:
    """
    Detect e-commerce specific patterns in the HTML.

    Args:
        html_content: HTML content to analyze

    Returns:
        Dictionary containing e-commerce patterns found
    """
    soup = BeautifulSoup(html_content, "html.parser")

    patterns = {
        "shopping_cart": False,
        "product_listings": False,
        "price_elements": False,
        "add_to_cart": False,
        "checkout": False,
        "product_categories": False,
        "confidence_score": 0,
    }

    text = soup.get_text().lower()

    # Check for shopping cart indicators
    cart_indicators = ["shopping cart", "cart", "basket", "bag", "checkout"]
    if any(indicator in text for indicator in cart_indicators):
        patterns["shopping_cart"] = True
        patterns["confidence_score"] += 20

    # Check for product listings
    product_indicators = ["product", "item", "goods", "merchandise", "listing"]
    if any(indicator in text for indicator in product_indicators):
        patterns["product_listings"] = True
        patterns["confidence_score"] += 20

    # Check for price elements
    price_indicators = ["price", "cost", "amount", "$", "€", "£", "₺"]
    if any(indicator in text for indicator in price_indicators):
        patterns["price_elements"] = True
        patterns["confidence_score"] += 20

    # Check for add to cart buttons
    add_to_cart_indicators = ["add to cart", "buy now", "purchase", "order"]
    if any(indicator in text for indicator in add_to_cart_indicators):
        patterns["add_to_cart"] = True
        patterns["confidence_score"] += 20

    # Check for checkout process
    checkout_indicators = ["checkout", "payment", "shipping", "delivery"]
    if any(indicator in text for indicator in checkout_indicators):
        patterns["checkout"] = True
        patterns["confidence_score"] += 10

    # Check for product categories
    category_indicators = ["category", "department", "section", "browse"]
    if any(indicator in text for indicator in category_indicators):
        patterns["product_categories"] = True
        patterns["confidence_score"] += 10

    # Normalize confidence score
    patterns["confidence_score"] = min(100, patterns["confidence_score"])

    return patterns
