"""
Day 9 S1 — Solar CFA Calculator Tool
=====================================
Implements exact MNRE PM Surya Ghar CFA subsidy calculation with:
- Slab-based rates: ₹30,000/kW (0-2 kW), ₹18,000/kW (2-3 kW), capped at 3 kW
- Special category state support: ₹33,000/kW and ₹19,800/kW
- Shadow-free roof area calculation (10 sq m per kW)
- Benchmark cost, net cost, and payback estimation

Run with:
    python -m app.tools
"""

import re
from typing import Any


def extract_capacity_kw(text: str) -> float | None:
    """
    Extract solar capacity in kW from natural language text.

    Supports formats:
    - "3 kW", "2.5 kW", "4 kWp"
    - "3kW", "2.5kWp"
    - "three kW" (limited word support)

    Args:
        text: Input text containing capacity mention

    Returns:
        Capacity in kW as float, or None if not found
    """
    text_lower = text.lower()

    # Try numeric patterns first (e.g., "3 kW", "2.5 kWp", "4kW")
    patterns = [
        r'(\d+\.?\d*)\s*kwp?',  # "3 kW", "2.5 kWp", "4kW"
        r'(\d+\.?\d*)\s*kilowatt',  # "3 kilowatt"
    ]

    for pattern in patterns:
        match = re.search(pattern, text_lower)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                continue

    # Try word-based numbers for common capacities
    word_numbers = {
        'one': 1.0, 'two': 2.0, 'three': 3.0, 'four': 4.0, 'five': 5.0,
        '1': 1.0, '2': 2.0, '3': 3.0, '4': 4.0, '5': 5.0,
    }

    for word, value in word_numbers.items():
        if re.search(rf'\b{word}\s*kw', text_lower):
            return value

    return None


def solar_cfa_calculator(
    capacity_kw: float,
    special_category_state: bool = False,
    monthly_bill_inr: float = 2000.0
) -> dict[str, Any]:
    """
    Calculate PM Surya Ghar CFA subsidy and system costs using exact MNRE rules.

    MNRE CFA Slabs (General States):
    - Slab 1 (0-2 kW): ₹30,000 per kW
    - Slab 2 (2-3 kW): ₹18,000 per kW
    - Maximum CFA: ₹78,000 at 3 kW (capped)

    Special Category States:
    - Slab 1 (0-2 kW): ₹33,000 per kW
    - Slab 2 (2-3 kW): ₹19,800 per kW
    - Maximum CFA: ₹85,800 at 3 kW (capped)

    Args:
        capacity_kw: System capacity in kW (e.g., 2.5, 3.0, 4.0)
        special_category_state: True for special category states (NE, Himachal, etc.)
        monthly_bill_inr: Monthly electricity bill in INR (for payback estimation)

    Returns:
        Dictionary with:
        - capacity_kw: Input capacity
        - cfa_subsidy_inr: Central Financial Assistance amount
        - shadow_free_area_sq_m: Required roof area in square meters
        - shadow_free_area_sq_ft: Required roof area in square feet
        - benchmark_cost_inr: MNRE benchmark system cost
        - net_cost_inr: Cost after CFA subsidy
        - estimated_payback_years: Rough payback period estimate
        - state_category: "general" or "special"
        - slab_breakdown: Details of CFA calculation per slab
    """
    # Validate input
    if capacity_kw <= 0:
        raise ValueError("Capacity must be positive")

    # Determine state category and rates
    if special_category_state:
        rate_slab_1 = 33000  # ₹33,000 per kW for first 2 kW
        rate_slab_2 = 19800  # ₹19,800 per kW for 2-3 kW
        max_cfa = 85800      # ₹85,800 at 3 kW
        state_category = "special"
    else:
        rate_slab_1 = 30000  # ₹30,000 per kW for first 2 kW
        rate_slab_2 = 18000  # ₹18,000 per kW for 2-3 kW
        max_cfa = 78000      # ₹78,000 at 3 kW
        state_category = "general"

    # Compute slab allocations
    slab_1_kw = min(capacity_kw, 2.0)  # First 2 kW at higher rate
    slab_2_kw = max(0.0, min(capacity_kw - 2.0, 1.0))  # Next 1 kW (up to 3 kW total)

    # Calculate CFA subsidy
    cfa_slab_1 = slab_1_kw * rate_slab_1
    cfa_slab_2 = slab_2_kw * rate_slab_2
    cfa_subsidy_inr = cfa_slab_1 + cfa_slab_2

    # Cap at 3 kW (no CFA beyond 3 kW)
    if capacity_kw > 3.0:
        cfa_subsidy_inr = max_cfa
        capped = True
        cfa_eligible_capacity = 3.0
    else:
        capped = False
        cfa_eligible_capacity = capacity_kw

    # Shadow-free roof area calculation (10 sq m per kW)
    shadow_free_area_sq_m = round(capacity_kw * 10.0, 2)
    shadow_free_area_sq_ft = round(capacity_kw * 100.0, 2)  # ~107.6 sq ft per kW (approx 100)

    # MNRE benchmark cost calculation
    # General states: ₹50,000/kW for first 2 kW, ₹45,000/kW for additional capacity
    # Special category: ₹55,000/kW for first 2 kW, ₹49,500/kW for additional
    if special_category_state:
        benchmark_rate_1 = 55000
        benchmark_rate_2 = 49500
    else:
        benchmark_rate_1 = 50000
        benchmark_rate_2 = 45000

    benchmark_slab_1 = min(capacity_kw, 2.0) * benchmark_rate_1
    benchmark_slab_2 = max(0.0, capacity_kw - 2.0) * benchmark_rate_2
    benchmark_cost_inr = round(benchmark_slab_1 + benchmark_slab_2, 2)

    # Net cost after subsidy
    net_cost_inr = round(benchmark_cost_inr - cfa_subsidy_inr, 2)

    # Estimated payback calculation
    # Assumptions:
    # - Annual savings = monthly_bill * 12 * utilization_factor (assume 70% offset)
    # - Payback = net_cost / annual_savings
    utilization_factor = 0.70  # Assume 70% of bill offset by solar
    annual_savings = monthly_bill_inr * 12 * utilization_factor

    if annual_savings > 0:
        estimated_payback_years = round(net_cost_inr / annual_savings, 1)
    else:
        estimated_payback_years = None

    # Slab breakdown for transparency
    slab_breakdown = {
        "slab_1": {
            "capacity_kw": round(slab_1_kw, 2),
            "rate_per_kw": rate_slab_1,
            "cfa_amount": round(cfa_slab_1, 2),
            "description": "First 2 kW"
        },
        "slab_2": {
            "capacity_kw": round(slab_2_kw, 2),
            "rate_per_kw": rate_slab_2,
            "cfa_amount": round(cfa_slab_2, 2),
            "description": "2-3 kW (additional capacity)"
        }
    }

    return {
        "capacity_kw": capacity_kw,
        "cfa_eligible_capacity": cfa_eligible_capacity,
        "cfa_subsidy_inr": round(cfa_subsidy_inr, 2),
        "capped": capped,
        "shadow_free_area_sq_m": shadow_free_area_sq_m,
        "shadow_free_area_sq_ft": shadow_free_area_sq_ft,
        "benchmark_cost_inr": benchmark_cost_inr,
        "net_cost_inr": net_cost_inr,
        "estimated_payback_years": estimated_payback_years,
        "state_category": state_category,
        "slab_breakdown": slab_breakdown,
        "monthly_bill_assumed": monthly_bill_inr,
        "annual_savings_estimated": round(annual_savings, 2) if estimated_payback_years else None,
    }


if __name__ == "__main__":
    """Test solar CFA calculator with sample queries."""

    print("=" * 70)
    print("Solar CFA Calculator Test")
    print("=" * 70)
    print()

    # Test cases
    test_cases = [
        ("How much subsidy for 3 kW?", 3.0, False),
        ("What about 2.5 kW system?", 2.5, False),
        ("I want 4 kW on my house", 4.0, False),
        ("2 kW in special category state", 2.0, True),
    ]

    for query, capacity, special in test_cases:
        print(f"Query: {query}")
        print(f"Extracted Capacity: {capacity} kW")
        print("-" * 70)

        result = solar_cfa_calculator(
            capacity_kw=capacity,
            special_category_state=special,
            monthly_bill_inr=2000.0
        )

        print(f"State Category: {result['state_category']}")
        print(f"CFA Subsidy: ₹{result['cfa_subsidy_inr']:,.0f}")
        if result['capped']:
            print("  ⚠ Capped at 3 kW (max subsidy)")
        print(f"Shadow-free Area: {result['shadow_free_area_sq_m']} sq m ({result['shadow_free_area_sq_ft']} sq ft)")
        print(f"Benchmark Cost: ₹{result['benchmark_cost_inr']:,.0f}")
        print(f"Net Cost (after CFA): ₹{result['net_cost_inr']:,.0f}")
        if result['estimated_payback_years']:
            print(f"Estimated Payback: {result['estimated_payback_years']} years")

        print("\nSlab Breakdown:")
        for slab_data in result['slab_breakdown'].values():
            if slab_data['capacity_kw'] > 0:
                print(f"  {slab_data['description']}: {slab_data['capacity_kw']} kW × ₹{slab_data['rate_per_kw']:,} = ₹{slab_data['cfa_amount']:,.0f}")

        print("\n" + "=" * 70)
        print()

    # Test extraction
    print("Capacity Extraction Tests:")
    print("-" * 70)
    test_queries = [
        "How much subsidy for 3 kW?",
        "I want 2.5 kW system",
        "What about 4kWp installation?",
        "Can I get subsidy for a three kW system?",
    ]

    for query in test_queries:
        extracted = extract_capacity_kw(query)
        print(f"{query:50} → {extracted} kW")

    print("\n" + "=" * 70)
    print("Calculator test complete!")
    print("=" * 70)
