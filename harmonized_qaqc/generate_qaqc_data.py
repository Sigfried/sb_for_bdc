#!/usr/bin/env python3
"""
Generate QAQC summary statistics for harmonized MeasurementObservation data.

This script loads MeasurementObservation TSV files from the BioData Catalyst
harmonized cohort data, filters to known observation types, and generates
summary statistics (counts, means, medians, etc.) for each variable.

Directory structure on Seven Bridges DataStudio:
    /sbgenomics/project-files/     - Read-only project files (input data)
    /sbgenomics/workspace/         - Read-write workspace (code and output)

Usage:
    # As a script:
    python generate_qaqc_data.py

    # In Jupyter notebook (no debugger on DataStudio, but can run cells):
    from generate_qaqc_data import *
    var_labels = get_var_label_lookup()
    result = load_measurement_observations(BASE_DIR, set(var_labels.keys()))
    summary = summarize_observations(result.df, var_labels)

Input files:
    - harmonized_vars.tsv: Mapping of observation_type codes to human-readable labels
      Located in /sbgenomics/project-files/QAQC_support_files/
    - *MeasurementObservation*.tsv: Harmonized data files in *-remapped directories
      Located in /sbgenomics/project-files/TSV_output/

Output files (written to OUTPUT_DIR):
    - diagnostics_<timestamp>.tsv: Per-file row counts and unexpected code info
    - measurement_summary_<timestamp>.tsv: Summary statistics by observation type
"""

import csv
import pandas as pd
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime

# =============================================================================
# Configuration - adjust these paths as needed for your environment
# =============================================================================
BASE_DIR = '/sbgenomics/project-files/TSV_output'
HARMONIZED_VARS_PATH = '/sbgenomics/project-files/QAQC_support_files/harmonized_vars.tsv'
OUTPUT_DIR = Path('/sbgenomics/workspace/sb_for_bdc/harmonized_qaqc/output')


@dataclass
class LoadResult:
    """Container for loaded data and diagnostics from load_measurement_observations()."""
    df: pd.DataFrame          # Combined MeasurementObservation data
    diagnostics: pd.DataFrame  # Per-file statistics and unexpected code info


def get_var_label_lookup(file_path: str = None) -> dict:
    """
    Load the variable name to label mapping from harmonized_vars.tsv.

    Args:
        file_path: Path to harmonized_vars.tsv. Defaults to HARMONIZED_VARS_PATH.

    Returns:
        Dict mapping observation_type codes (e.g., 'bmi_1') to labels (e.g., 'body mass index').
    """
    if file_path is None:
        file_path = HARMONIZED_VARS_PATH

    with open(file_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        rows = list(reader)

    return {r['var_name']: r['var_label'] for r in rows}


def load_measurement_observations(base_dir: str = None, valid_codes: set = None) -> LoadResult:
    """
    Load all MeasurementObservation files from *-remapped directories.

    Scans base_dir for directories matching *-remapped, then loads all TSV files
    matching *MeasurementObservation*.tsv. Optionally filters to known observation
    types and tracks diagnostics about unexpected codes.

    Args:
        base_dir: Directory containing *-remapped subdirectories. Defaults to BASE_DIR.
        valid_codes: Set of valid observation_type values to keep. If provided,
            rows with other observation types are excluded and tracked in diagnostics.

    Returns:
        LoadResult with:
            - df: Combined DataFrame with columns from source files plus source_file, source_dir
            - diagnostics: DataFrame with per-file statistics
    """
    if base_dir is None:
        base_dir = BASE_DIR
    base_path = Path(base_dir)
    dfs = []
    diag_rows = []
    
    for remapped_dir in sorted(base_path.glob("*-remapped")):
        for tsv_file in remapped_dir.glob("*MeasurementObservation*.tsv"):
            print(f"Loading {tsv_file.name}...", flush=True)
            file_df = pd.read_csv(
                tsv_file,
                sep='\t',
                dtype=str,
                engine='python',
                on_bad_lines=lambda bad_line: bad_line[:5]
            )
            file_df['source_file'] = tsv_file.name
            file_df['source_dir'] = remapped_dir.name
            
            # Diagnostics for this file
            total_rows = len(file_df)
            total_participants = file_df['associated_participant'].nunique()
            
            if valid_codes:
                expected_mask = file_df['observation_type'].isin(valid_codes)
                expected_rows = int(expected_mask.sum())
                unexpected_rows = total_rows - expected_rows
                
                # Top unexpected codes
                unexpected_df = file_df[~expected_mask]
                top_unexpected = (
                    unexpected_df['observation_type']
                    .value_counts()
                    .head(5)
                    .to_dict()
                )
                
                # Keep only expected
                file_df = file_df[expected_mask]
            else:
                expected_rows = total_rows
                unexpected_rows = 0
                top_unexpected = {}
            
            diag_rows.append({
                'source_dir': remapped_dir.name,
                'source_file': tsv_file.name,
                'total_rows': total_rows,
                'expected_rows': expected_rows,
                'unexpected_rows': unexpected_rows,
                'participants': total_participants,
                'top_unexpected': top_unexpected if top_unexpected else None,
            })
            
            dfs.append(file_df)
    
    combined = pd.concat(dfs, ignore_index=True, sort=False) if dfs else pd.DataFrame()
    diagnostics = pd.DataFrame(diag_rows)
    
    return LoadResult(df=combined, diagnostics=diagnostics)


def summarize_observations(df: pd.DataFrame, var_labels: dict = None) -> pd.DataFrame:
    """
    Generate summary statistics for each observation_type.

    For each unique observation_type, computes:
        - n: Total row count
        - nulls_missing: Count of null/None values
        - participants: Unique participant count
        - mean, median, min, max, sd: Numeric statistics (if values are numeric)

    Args:
        df: DataFrame with observation_type, value columns, and associated_participant.
        var_labels: Optional dict mapping observation_type to human-readable labels.

    Returns:
        DataFrame with one row per observation_type and summary columns.
    """
    df = df.copy()
    df['value'] = df.get('value_quantity__value_decimal')
    if 'value_quantity__value_concept' in df.columns:
        df['value'] = df['value'].fillna(df['value_quantity__value_concept'])
    
    # Convert to numeric where possible
    df['value_numeric'] = pd.to_numeric(df['value'], errors='coerce')
    
    def summarize_group(g):
        numeric_vals = g['value_numeric'].dropna()
        
        n = len(g)
        nulls = g['value'].isna().sum() + (g['value'] == 'None').sum()
        participants = g['associated_participant'].nunique()
        
        result = {
            'n': int(n),
            'nulls_missing': int(nulls),
            'participants': int(participants),
        }
        
        if len(numeric_vals) > 0:
            result.update({
                'mean': round(numeric_vals.mean(), 3),
                'median': round(numeric_vals.median(), 3),
                'min': numeric_vals.min(),
                'max': round(numeric_vals.max(), 3),
                'sd': round(numeric_vals.std(), 3),
            })
        else:
            result.update({
                'mean': None,
                'median': None,
                'min': None,
                'max': None,
                'sd': None,
            })
        
        return pd.Series(result)
    
    summary = df.groupby('observation_type').apply(summarize_group)
    summary = summary.reset_index()
    
    # Add labels if provided
    if var_labels:
        summary['label'] = summary['observation_type'].map(var_labels)
        cols = ['observation_type', 'label'] + [c for c in summary.columns if c not in ['observation_type', 'label']]
        summary = summary[cols]
    
    return summary


def format_summary_for_print(summary: pd.DataFrame) -> str:
    """Format summary with commas for integer columns."""
    df = summary.copy()
    for col in ['n', 'nulls_missing', 'participants']:
        if col in df.columns:
            df[col] = df[col].apply(lambda x: f'{x:,}' if pd.notna(x) else '')
    return df.to_string()


def main():
    """
    Main entry point: load data, generate summaries, and save outputs.

    Uses module-level constants BASE_DIR, HARMONIZED_VARS_PATH, and OUTPUT_DIR.
    Can also be run step-by-step in a Jupyter notebook - see module docstring.
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    # Load mappings
    print("Loading variable mappings...", flush=True)
    var_labels = get_var_label_lookup()
    valid_codes = set(var_labels.keys())
    print(f"Found {len(valid_codes)} valid observation codes\n", flush=True)

    # Load data
    print("Loading MeasurementObservation files...", flush=True)
    result = load_measurement_observations(BASE_DIR, valid_codes)
    
    # Print diagnostics
    print("\n" + "="*80)
    print("DIAGNOSTICS BY FILE")
    print("="*80)
    print(result.diagnostics.to_string())
    
    # Save diagnostics
    diag_file = OUTPUT_DIR / f'diagnostics_{timestamp}.tsv'
    result.diagnostics.to_csv(diag_file, sep='\t', index=False)
    print(f"\nDiagnostics saved to: {diag_file}")
    
    # Summarize
    print("\n" + "="*80)
    print("GENERATING SUMMARY STATISTICS")
    print("="*80)
    summary = summarize_observations(result.df, var_labels)
    
    # Print summary
    print("\n" + format_summary_for_print(summary))
    
    # Save summary
    summary_file = OUTPUT_DIR / f'measurement_summary_{timestamp}.tsv'
    summary.to_csv(summary_file, sep='\t', index=False)
    print(f"\nSummary saved to: {summary_file}")
    
    # Quick stats
    print("\n" + "="*80)
    print("QUICK STATS")
    print("="*80)
    print(f"Total rows loaded: {len(result.df):,}")
    print(f"Unique observation types: {result.df['observation_type'].nunique()}")
    print(f"Unique participants: {result.df['associated_participant'].nunique():,}")
    
    total_unexpected = result.diagnostics['unexpected_rows'].sum()
    if total_unexpected > 0:
        print(f"\nWARNING: {total_unexpected:,} rows with unexpected observation types were excluded")


if __name__ == '__main__':
    main()