"""
Utilities for adding text-to-image prompts to recommended product ideas.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Iterable


def build_text_to_image_prompt(
    product_name: str,
    *,
    category: str = "",
    market: str = "",
    product_type: str = "",
    differentiation: str = "",
    price: str = "",
) -> str:
    """Build a reusable product image generation prompt for ecommerce concepts."""
    name = _clean(product_name) or _clean(category) or "product concept"
    category_text = _clean(category)
    market_text = _clean(market)
    type_text = _clean(product_type)
    differentiation_text = _clean(differentiation)
    price_text = _clean(price)

    context_parts = []
    if category_text:
        context_parts.append(f"category: {category_text}")
    if market_text:
        context_parts.append(f"target market: {market_text}")
    if type_text:
        context_parts.append(f"product role: {type_text}")
    if differentiation_text:
        context_parts.append(f"key differentiation: {differentiation_text}")
    if price_text:
        context_parts.append(f"suggested price range: {price_text}")

    context = "; ".join(context_parts)
    if context:
        context = f" ({context})"

    return (
        f"Photorealistic ecommerce product concept image for '{name}'{context}. "
        "Show the product clearly as the hero object with premium materials, realistic scale, "
        "clean modern packaging beside it, soft studio lighting, sharp details, commercial Amazon listing style, "
        "white or very light neutral background, no brand logo, no readable text, no watermark, no clutter. "
        "Use a 4:5 vertical composition suitable for marketplace product imagery."
    )


def attach_image_prompts(
    recommendations: Iterable[dict[str, Any]],
    *,
    category: str = "",
    market: str = "",
) -> list[dict[str, Any]]:
    """Return copied recommendations with image_prompt filled when missing."""
    enriched: list[dict[str, Any]] = []
    for recommendation in recommendations:
        item = deepcopy(recommendation)
        prompt = item.get("image_prompt") or item.get("text_to_image_prompt")
        if not prompt:
            name = (
                item.get("name")
                or item.get("title")
                or item.get("keyword")
                or item.get("direction")
                or item.get("category")
                or category
            )
            differentiation = " | ".join(
                str(value)
                for value in (item.get("why"), item.get("detail"), item.get("action"), item.get("description"))
                if value
            )
            prompt = build_text_to_image_prompt(
                str(name),
                category=category,
                market=market,
                product_type=str(item.get("type") or item.get("product_type") or ""),
                differentiation=differentiation,
                price=str(item.get("price") or ""),
            )
        item["image_prompt"] = prompt
        item.setdefault("text_to_image_prompt", prompt)
        enriched.append(item)
    return enriched


def _clean(value: Any) -> str:
    return " ".join(str(value or "").split())
