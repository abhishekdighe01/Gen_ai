"""
Generate sample payback chart for documentation.
"""

import os
import sys

import matplotlib.pyplot as plt

# Add parent to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.tools import solar_cfa_calculator


def generate_payback_chart():
    """Generate sample 3 kW payback chart."""

    # Calculate for 3 kW system
    calc = solar_cfa_calculator(
        capacity_kw=3.0,
        special_category_state=False,
        monthly_bill_inr=2000.0
    )

    # Calculate yearly data
    annual_savings = 2000 * 12 * 0.70  # 70% bill offset
    net_cost = calc['net_cost_inr']

    years = list(range(0, 16))
    cumulative_savings = [annual_savings * year for year in years]
    net_cost_line = [net_cost] * len(years)

    # Find payback year
    payback_year = None
    for year, savings in enumerate(cumulative_savings):
        if savings >= net_cost:
            payback_year = year
            break

    # Create figure
    fig, ax = plt.subplots(figsize=(12, 7))

    # Plot lines
    ax.plot(years, cumulative_savings, 'g-', linewidth=3, label='Cumulative Electricity Savings', marker='o')
    ax.plot(years, net_cost_line, 'r--', linewidth=3, label='Net System Cost (after CFA)')

    # Mark payback point
    if payback_year:
        ax.axvline(x=payback_year, color='orange', linestyle=':', linewidth=2.5, alpha=0.7)
        ax.plot(payback_year, net_cost_line[0], 'o', markersize=15, color='orange',
                label=f'Break-Even at Year {payback_year}', zorder=5)
        ax.text(payback_year, net_cost_line[0] * 1.15, f'Payback: {payback_year} years',
                ha='center', fontsize=12, fontweight='bold', color='orange',
                bbox=dict(boxstyle='round', facecolor='white', edgecolor='orange', linewidth=2))

    # Add annotations
    ax.annotate(f'CFA Subsidy: ₹{calc["cfa_subsidy_inr"]:,.0f}',
                xy=(8, net_cost * 0.5), fontsize=11,
                bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.8))

    ax.annotate(f'Net Cost: ₹{net_cost:,.0f}',
                xy=(8, net_cost * 1.1), fontsize=11,
                bbox=dict(boxstyle='round', facecolor='lightcoral', alpha=0.8))

    # Styling
    ax.set_xlabel('Years', fontsize=14, fontweight='bold')
    ax.set_ylabel('Amount (₹)', fontsize=14, fontweight='bold')
    ax.set_title('SuryaGharSathi — 3 kW Rooftop Solar Payback Analysis\n'
                 'PM Surya Ghar: Muft Bijli Yojana for Kopargaon Homeowner',
                 fontsize=16, fontweight='bold', pad=20)
    ax.legend(loc='upper left', fontsize=12, framealpha=0.95)
    ax.grid(True, alpha=0.3, linestyle='--')

    # Format y-axis
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'₹{x/1000:.0f}K' if x >= 1000 else f'₹{x:.0f}'))

    # Set background color
    ax.set_facecolor('#f8f9fa')
    fig.patch.set_facecolor('white')

    plt.tight_layout()

    # Save
    os.makedirs('docs', exist_ok=True)
    output_path = 'docs/suryagharsathi_ui.png'
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    print(f"Chart saved to {output_path}")

    return output_path


if __name__ == "__main__":
    generate_payback_chart()
