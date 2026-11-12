"""
Day 4 S2 — Data Analysis with Pandas
=====================================
Analyze SuryaGharSathi solar guidelines dataset using pandas.

Run with:
    python analysis/explore.py
"""

import pandas as pd
import json
from pathlib import Path


def load_data_to_dataframe():
    """Load records from JSON into a pandas DataFrame."""
    json_path = Path(__file__).parent.parent / "data" / "records.json"
    
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    df = pd.DataFrame(data)
    return df


def analyze_dataset():
    """Run comprehensive analysis on the SuryaGharSathi dataset."""
    
    print("=" * 80)
    print("SuryaGharSathi Dataset Analysis — Powered by Pandas")
    print("=" * 80)
    print()
    
    # Load data
    df = load_data_to_dataframe()
    
    print(f"Dataset loaded: {len(df)} records")
    print()
    
    # ===== FACT 1: Record Count per Source Document / Issuing Body =====
    print("=" * 80)
    print("FACT 1: Record Distribution by Source Document")
    print("=" * 80)
    
    doc_counts = df['document_title'].value_counts()
    print(f"\nTotal unique documents: {len(doc_counts)}")
    print("\nRecords per document:")
    for doc, count in doc_counts.items():
        # Truncate long titles for readability
        short_doc = doc[:70] + "..." if len(doc) > 70 else doc
        print(f"  • {short_doc}")
        print(f"    Count: {count} records ({count/len(df)*100:.1f}%)")
    
    print("\nIssuing Body:")
    issuing_body_counts = df['issuing_body'].value_counts()
    for body, count in issuing_body_counts.items():
        print(f"  • {body}: {count} records")
    
    print()
    
    # ===== FACT 2: Rule Length Statistics and Top Topics =====
    print("=" * 80)
    print("FACT 2: Rule Length Statistics and Top Topics")
    print("=" * 80)
    
    df['key_rule_length'] = df['key_rule'].str.len()
    
    print("\nKey Rule Length Statistics:")
    print(f"  • Mean length: {df['key_rule_length'].mean():.1f} characters")
    print(f"  • Median length: {df['key_rule_length'].median():.1f} characters")
    print(f"  • Min length: {df['key_rule_length'].min()} characters")
    print(f"  • Max length: {df['key_rule_length'].max()} characters")
    print(f"  • Std deviation: {df['key_rule_length'].std():.1f} characters")
    
    print("\nTop 10 Most Common Topics:")
    topic_counts = df['topic'].value_counts().head(10)
    for i, (topic, count) in enumerate(topic_counts.items(), 1):
        print(f"  {i}. {topic}: {count} record(s)")
    
    print()
    
    # ===== FACT 3: Coverage of Key Solar Policy Themes =====
    print("=" * 80)
    print("FACT 3: Coverage of Key Solar Policy Themes")
    print("=" * 80)
    
    # Define key policy themes and their keywords
    themes = {
        "CFA Subsidy": ["cfa", "subsidy", "financial assistance", "benchmark cost"],
        "DISCOM": ["discom", "distribution", "utility"],
        "RESCO": ["resco", "renewable energy service company"],
        "Net Metering": ["net meter", "metering"],
        "Residential Eligibility": ["residential", "eligible", "household"],
        "Capacity & System Size": ["kw", "kwp", "capacity", "system"],
        "DCR (Domestic Content)": ["domestic content", "dcr", "manufactured domestically"],
        "Payment Security": ["payment security", "psm"],
        "Installation & Commissioning": ["installation", "commissioning"],
        "GHS/RWA": ["group housing", "ghs", "rwa", "residential welfare"],
    }
    
    print("\nPolicy Theme Coverage Analysis:")
    print("(Number of records mentioning each theme)\n")
    
    theme_coverage = {}
    for theme_name, keywords in themes.items():
        # Count records where any keyword appears in topic or key_rule (case-insensitive)
        mask = df.apply(
            lambda row: any(
                keyword.lower() in row['topic'].lower() or 
                keyword.lower() in row['key_rule'].lower()
                for keyword in keywords
            ),
            axis=1
        )
        count = mask.sum()
        theme_coverage[theme_name] = count
    
    # Sort by coverage descending
    sorted_themes = sorted(theme_coverage.items(), key=lambda x: x[1], reverse=True)
    
    for theme, count in sorted_themes:
        percentage = (count / len(df)) * 100
        bar = "█" * int(percentage / 2)  # Visual bar (50 chars = 100%)
        print(f"  • {theme:.<30} {count:>3} records ({percentage:>5.1f}%) {bar}")
    
    print()
    
    # ===== ADDITIONAL INSIGHTS =====
    print("=" * 80)
    print("ADDITIONAL INSIGHTS")
    print("=" * 80)
    
    # Date range analysis
    df['date_issued'] = pd.to_datetime(df['date_issued'])
    print(f"\nDate Range:")
    print(f"  • Earliest document: {df['date_issued'].min().strftime('%Y-%m-%d')}")
    print(f"  • Latest document: {df['date_issued'].max().strftime('%Y-%m-%d')}")
    print(f"  • Date span: {(df['date_issued'].max() - df['date_issued'].min()).days} days")
    
    # Source section analysis
    print(f"\nSource Section Coverage:")
    print(f"  • Total unique sections: {df['source_section'].nunique()}")
    print(f"  • Records with section refs: {df['source_section'].notna().sum()}")
    
    # Page citation analysis
    df['num_pages_cited'] = df['source_pages'].apply(len)
    print(f"\nPage Citations:")
    print(f"  • Average pages cited per record: {df['num_pages_cited'].mean():.1f}")
    print(f"  • Max pages cited in one record: {df['num_pages_cited'].max()}")
    
    print()
    print("=" * 80)
    print("Analysis Complete")
    print("=" * 80)


if __name__ == "__main__":
    analyze_dataset()
