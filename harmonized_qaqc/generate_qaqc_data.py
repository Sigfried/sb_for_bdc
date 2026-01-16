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
    priority_vars = set(var_labels.keys())
    result = load_measurement_observations(BASE_DIR, priority_vars)
    summary = summarize_observations(result.df, var_labels)

    # View as markdown with commafied numbers:
    print(format_diagnostics_markdown(result.diagnostics))
    print(format_summary_markdown(summary))

    # Generate paste-ready TSV for Google Sheets Table S5:
    sheets_tsv = format_for_sheets(summary, var_labels)
    print(sheets_tsv)  # Copy this output and paste into cell B3

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


def load_measurement_observations(base_dir: str = None, priority_vars: set = None) -> LoadResult:
    """
    Load all MeasurementObservation files from *-remapped directories.

    Scans base_dir for directories matching *-remapped, then loads all TSV files
    matching *MeasurementObservation*.tsv. Optionally filters to priority variables
    and tracks diagnostics about excluded observation types.

    Args:
        base_dir: Directory containing *-remapped subdirectories. Defaults to BASE_DIR.
        priority_vars: Set of observation_type values (var_names) to keep. If provided,
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

            if priority_vars:
                priority_mask = file_df['observation_type'].isin(priority_vars)
                priority_rows = int(priority_mask.sum())
                excluded_rows = total_rows - priority_rows

                # Top excluded observation types
                excluded_df = file_df[~priority_mask]
                top_excluded = (
                    excluded_df['observation_type']
                    .value_counts()
                    .head(5)
                    .to_dict()
                )

                # Keep only priority vars
                file_df = file_df[priority_mask]
            else:
                priority_rows = total_rows
                excluded_rows = 0
                top_excluded = {}
            
            diag_rows.append({
                'source_dir': remapped_dir.name,
                'source_file': tsv_file.name,
                'total_rows': total_rows,
                'priority_rows': priority_rows,
                'excluded_rows': excluded_rows,
                'participants': total_participants,
                'top_excluded': top_excluded if top_excluded else None,
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


# =============================================================================
# Google Sheets target format (Table S5)
# =============================================================================
# Ordered list of priority variable labels for Table S5
# This defines the exact row order for the paste-ready output
TABLE_S5_LABELS = [
    "8-epi-PGF2a in urine",
    "Activity LP-PLA2 in blood",
    "AHI Apnea-Hypopnea Index",
    "Albumin creatinine ratio in urine",
    "Albumin in blood",
    "Albumin in urine",
    "Alcohol Consumption",
    "ALT SGPT",
    "AST SGOT",
    "Basophils Count",
    "Bilirubin Conjugated Direct",
    "Bilirubin total",
    "BMI",
    "BNP",
    "Body weight",
    "BUN",
    "BUN Creatinine ratio",
    "CRP c-reactive protein",
    "CAC Score",
    "CAC volume",
    "Carotid IMT",
    "Carotid stenosis left",
    "Carotid stenosis right",
    "CD40 in blood",
    "CESD score",
    "Chloride in blood",
    "Cigarette smoking",
    "Creatinine in blood",
    "Creatinine in urine",
    "Cystatin C in blood",
    "D-Dimer",
    "Diastolic blood pressure",
    "E-selectin in blood",
    "EGFR",
    "Eosinophils count",
    "Factor VII",
    "Factor VIII",
    "Fasting blood glucose",
    "Fasting lipids",
    "Ferritin",
    "FEV1 - Forced Expiratory Volume in 1 sec",
    "FEV1 FVC",
    "Fibrinogen",
    "Fruit consumption",
    "FVC - Forced Vital Capacity",
    "GFR",
    "Glucose in blood",
    "HDL",
    "Heart rate",
    "Height",
    "Hematocrit",
    "Hemoglobin",
    "Hemoglobin A1c",
    "Hip circumference",
    "ICAM1 in blood",
    "Insulin in blood",
    "Interleukin 1 beta in blood",
    "Interleukin 10 in blood",
    "interleukin 6 in blood",
    "Lactate Dehydrogenase LDH",
    "Lactate in blood",
    "LDL",
    "Lymphocytes count",
    "Lymphocytes percent",
    "Mass LP-PLA2 in blood",
    "MCP1 in blood",
    "Mean arterial pressure",
    "Mean corpuscular hemoglobin",
    "Mean corpuscular hemoglobin concentration",
    "Mean corpuscular volume",
    "Mean platelet volume",
    "MMP9 in blood",
    "Monocytes count",
    "Myeloperoxidase in blood",
    "Neutrophils count",
    "Neutrophils percent",
    "NT pro BNP",
    "Osteoprotegerin in blood",
    "P-selectin in blood",
    "Platelet count",
    "Potassium in blood",
    "PR interval",
    "QRS interval",
    "QT interval",
    "Red blood cell count",
    "Red cell distribution width",
    "Sleep hours",
    "Sodium in blood",
    "Sodium intake",
    "SpO2",
    "Systolic blood pressure",
    "Temperature",
    "TNFa in blood",
    "TNFa-R1 in blood",
    "Total cholesterol in blood",
    "Triglycerides in blood",
    "Troponin all types",
    "Vegetable consumption",
    "Von Willebrand factor",
    "Waist circumference",
    "Waist-hip ratio",
    "White blood cell count",
]


def format_for_sheets(summary: pd.DataFrame, var_labels: dict) -> str:
    """
    Format summary for pasting into Google Sheets Table S5.

    Creates a TSV with columns in the exact order expected by the sheet:
    n, nulls/missing, mean, median, max, min, sd, enums, participants

    Rows are ordered to match TABLE_S5_LABELS. Variables not in the summary
    get blank rows. Raw numbers (no commas) for proper Sheets formatting.

    Args:
        summary: DataFrame from summarize_observations() with 'label' column.
        var_labels: Dict mapping var_name to label (used to detect missing vars).

    Returns:
        TSV string ready to paste into cell B3 of Table S5.
    """
    # Build lookup from label to summary row
    summary_by_label = {}
    if 'label' in summary.columns:
        for _, row in summary.iterrows():
            if pd.notna(row.get('label')):
                summary_by_label[row['label']] = row

    # Sheet column order (excluding the Priority Variable column which is col A)
    sheet_cols = ['n', 'nulls_missing', 'mean', 'median', 'max', 'min', 'sd', 'enums', 'participants']

    lines = []
    for label in TABLE_S5_LABELS:
        if label in summary_by_label:
            row = summary_by_label[label]
            values = []
            for col in sheet_cols:
                if col == 'enums':
                    values.append('')  # Empty for now (numeric data)
                elif col == 'nulls_missing':
                    val = row.get('nulls_missing', '')
                    values.append('' if pd.isna(val) else str(int(val)))
                elif col in ['n', 'participants']:
                    val = row.get(col, '')
                    values.append('' if pd.isna(val) else str(int(val)))
                else:
                    val = row.get(col, '')
                    values.append('' if pd.isna(val) else str(val))
            lines.append('\t'.join(values))
        else:
            # Blank row for missing variable
            lines.append('\t'.join([''] * len(sheet_cols)))

    return '\n'.join(lines)


def format_markdown(df: pd.DataFrame, int_cols: list = None, float_cols: list = None) -> str:
    """
    Format a DataFrame as markdown with commafied numbers.

    Args:
        df: DataFrame to format.
        int_cols: Columns to format as integers with commas.
        float_cols: Columns to format as floats with commas (2 decimal places).

    Returns:
        Markdown table string.
    """
    fmt_df = df.copy()

    if int_cols:
        for col in int_cols:
            if col in fmt_df.columns:
                fmt_df[col] = fmt_df[col].apply(
                    lambda x: f'{int(x):,}' if pd.notna(x) else ''
                )

    if float_cols:
        for col in float_cols:
            if col in fmt_df.columns:
                fmt_df[col] = fmt_df[col].apply(
                    lambda x: f'{x:,.2f}' if pd.notna(x) else ''
                )

    return fmt_df.to_markdown(index=False)


def format_diagnostics_markdown(diagnostics: pd.DataFrame) -> str:
    """Format diagnostics DataFrame as markdown with commafied numbers."""
    return format_markdown(
        diagnostics,
        int_cols=['total_rows', 'priority_rows', 'excluded_rows', 'participants']
    )


def format_summary_markdown(summary: pd.DataFrame) -> str:
    """Format summary DataFrame as markdown with commafied numbers."""
    return format_markdown(
        summary,
        int_cols=['n', 'nulls_missing', 'participants'],
        float_cols=['mean', 'median', 'min', 'max', 'sd']
    )


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
    priority_vars = set(var_labels.keys())
    print(f"Found {len(priority_vars)} priority variables\n", flush=True)

    # Load data
    print("Loading MeasurementObservation files...", flush=True)
    result = load_measurement_observations(BASE_DIR, priority_vars)
    
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
    
    total_excluded = result.diagnostics['excluded_rows'].sum()
    if total_excluded > 0:
        print(f"\nNOTE: {total_excluded:,} rows with non-priority observation types were excluded")


if __name__ == '__main__':
    main()