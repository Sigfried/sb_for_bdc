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
    - harmonized_vars.tsv: Mapping of var_name -> var_label. Lives in the repo
      under harmonized_qaqc/QAQC_support_files_will_be_copied_into_project-files/
      (read directly from the workspace clone — not copied into project-files).
    - MeasurementObservation.tsv: One per cohort/consent group, under
      /sbgenomics/project-files/DataRun_*/DMC_*_Processed_*/<study>_BDCHM/mapped-data/

Output files (written to OUTPUT_DIR):
    - measurement_summary_<timestamp>.tsv: Summary statistics by observation type
    - table_s5_paste_<timestamp>.tsv: Paste-ready TSV for Google Sheets Table S5 (cell B3)
    - s5_coverage_<timestamp>.tsv: Per-S5-label match status (matched/aliased/missing)
"""

import csv
import pandas as pd
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime

# =============================================================================
# Configuration - adjust these paths as needed for your environment
# =============================================================================
BASE_DIR = '/sbgenomics/project-files/DataRun_20260412_1830'
HARMONIZED_VARS_PATH = str(
    Path(__file__).parent
    / 'QAQC_support_files_will_be_copied_into_project-files'
    / 'harmonized_vars.tsv'
)
OUTPUT_DIR = Path('/sbgenomics/workspace/sb_for_bdc/harmonized_qaqc/output')


@dataclass
class LoadResult:
    """Container for loaded data from load_measurement_observations()."""
    df: pd.DataFrame


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
    Load all MeasurementObservation.tsv files from a DataRun_* directory.

    Layout (post-2026-04 BDCHM pipeline):
        <base_dir>/DMC_<study>_<COHORT>_Processed_<ts>/<study>_BDCHM/mapped-data/MeasurementObservation.tsv

    Each MeasurementObservation.tsv has the same flat name; cohort/consent is
    encoded in the parent DMC_* directory.

    Args:
        base_dir: DataRun_* directory. Defaults to BASE_DIR.
        priority_vars: Set of observation_type values to keep. If given, non-priority
            rows are dropped (tracked in the loader's stdout summary).

    Returns:
        LoadResult with df containing all priority-filtered rows plus source_dir
        (the DMC_* dir name, used as cohort/consent identifier).
    """
    if base_dir is None:
        base_dir = BASE_DIR
    base_path = Path(base_dir)
    dfs = []

    tsv_files = sorted(base_path.glob("DMC_*/*/mapped-data/MeasurementObservation.tsv"))
    print(f"Found {len(tsv_files)} MeasurementObservation.tsv files\n", flush=True)

    for tsv_file in tsv_files:
        # source_dir is the DMC_<...>_Processed_<ts> directory (cohort/consent ID)
        source_dir = tsv_file.parents[2].name
        print(f"Loading {source_dir}...", flush=True)

        file_df = pd.read_csv(
            tsv_file,
            sep='\t',
            dtype=str,
            engine='python',
            on_bad_lines=lambda bad_line: bad_line[:5]
        )
        file_df['source_dir'] = source_dir

        if priority_vars:
            file_df = file_df[file_df['observation_type'].isin(priority_vars)]

        dfs.append(file_df)

    combined = pd.concat(dfs, ignore_index=True, sort=False) if dfs else pd.DataFrame()
    return LoadResult(df=combined)


def load_with_excluded_summary(base_dir: str = None, priority_vars: set = None) -> tuple:
    """
    Like load_measurement_observations, but also returns a top-N excluded codes
    summary across all files. Useful as a sanity check that priority_vars
    matches what's actually in the data.

    Returns:
        (LoadResult, excluded_summary_df) — excluded_summary_df has columns
        observation_type and count, sorted descending.
    """
    if base_dir is None:
        base_dir = BASE_DIR
    base_path = Path(base_dir)
    dfs = []
    all_excluded_counts = {}

    tsv_files = sorted(base_path.glob("DMC_*/*/mapped-data/MeasurementObservation.tsv"))
    print(f"Found {len(tsv_files)} MeasurementObservation.tsv files\n", flush=True)

    for tsv_file in tsv_files:
        source_dir = tsv_file.parents[2].name
        print(f"Loading {source_dir}...", flush=True)

        file_df = pd.read_csv(
            tsv_file,
            sep='\t',
            dtype=str,
            engine='python',
            on_bad_lines=lambda bad_line: bad_line[:5]
        )
        file_df['source_dir'] = source_dir

        if priority_vars:
            mask = file_df['observation_type'].isin(priority_vars)
            for code, n in file_df.loc[~mask, 'observation_type'].value_counts().items():
                all_excluded_counts[code] = all_excluded_counts.get(code, 0) + int(n)
            file_df = file_df[mask]

        dfs.append(file_df)

    combined = pd.concat(dfs, ignore_index=True, sort=False) if dfs else pd.DataFrame()
    excluded = (
        pd.DataFrame(
            sorted(all_excluded_counts.items(), key=lambda kv: -kv[1]),
            columns=['observation_type', 'count'],
        )
        if all_excluded_counts
        else pd.DataFrame(columns=['observation_type', 'count'])
    )
    return LoadResult(df=combined), excluded


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
# S5 column-A labels that don't match harmonized_vars.tsv var_label exactly.
# Maps S5 label -> tsv label so the canonical TSV (and the data labels derived
# from it) can stay as-is while still finding the right row for the sheet.
S5_LABEL_ALIASES = {
    "Alcohol Consumption": "Alcohol",
    "Basophils Count": "basophils count",
    "CRP c-reactive protein": "c-reactive protein CRP",
    "Fruit consumption": "Fruits",
    "Mean corpuscular hemoglobin": "mean corpuscular hemoglobin",
    "Mean corpuscular hemoglobin concentration": "mean corpuscular hemoglobin concentration",
    "Mean corpuscular volume": "mean corpuscular volume",
    "Mean platelet volume": "mean platelet volume",
    "Monocytes count": "monocytes count",
    "Vegetable consumption": "Vegetables",
    "Von Willebrand factor": "von Willebrand factor",
}

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


def format_for_sheets(summary: pd.DataFrame, var_labels: dict) -> tuple:
    """
    Format summary for pasting into Google Sheets Table S5.

    Creates a TSV with columns in the exact order expected by the sheet:
    n, nulls/missing, mean, median, max, min, sd, enums, participants

    Rows are ordered to match TABLE_S5_LABELS. Variables not in the summary
    get blank rows. Raw numbers (no commas) for proper Sheets formatting.

    S5 labels are looked up against summary labels via S5_LABEL_ALIASES first,
    then by exact match.

    Args:
        summary: DataFrame from summarize_observations() with 'label' column.
        var_labels: Dict mapping var_name to label (used to detect missing vars).

    Returns:
        (tsv_string, coverage_df) — TSV ready to paste into cell B3 of Table S5,
        and a DataFrame with one row per S5 label showing match status.
    """
    summary_by_label = {}
    if 'label' in summary.columns:
        for _, row in summary.iterrows():
            if pd.notna(row.get('label')):
                summary_by_label[row['label']] = row

    sheet_cols = ['n', 'nulls_missing', 'mean', 'median', 'max', 'min', 'sd', 'enums', 'participants']

    lines = []
    coverage_rows = []
    for label in TABLE_S5_LABELS:
        lookup = S5_LABEL_ALIASES.get(label, label)
        row = summary_by_label.get(lookup)
        if row is not None:
            status = 'aliased' if lookup != label else 'matched'
            values = []
            for col in sheet_cols:
                if col == 'enums':
                    values.append('')
                elif col in ('nulls_missing', 'n', 'participants'):
                    val = row.get(col, '')
                    values.append('' if pd.isna(val) else str(int(val)))
                else:
                    val = row.get(col, '')
                    values.append('' if pd.isna(val) else str(val))
            lines.append('\t'.join(values))
            n_val = row.get('n')
        else:
            status = 'missing'
            lines.append('\t'.join([''] * len(sheet_cols)))
            n_val = None
        coverage_rows.append({
            's5_label': label,
            'lookup_label': lookup,
            'status': status,
            'n': int(n_val) if pd.notna(n_val) else None,
        })

    coverage = pd.DataFrame(coverage_rows)
    return '\n'.join(lines), coverage


def format_coverage_markdown(coverage: pd.DataFrame) -> str:
    """Format S5 coverage report as markdown, grouped by status."""
    counts = coverage['status'].value_counts().to_dict()
    header = (
        f"**S5 coverage:** {counts.get('matched', 0)} matched, "
        f"{counts.get('aliased', 0)} matched via alias, "
        f"{counts.get('missing', 0)} missing.\n"
    )
    return header + '\n' + format_markdown(coverage, int_cols=['n'])


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
    Main entry point: load data, generate summaries, write outputs.

    Uses module-level constants BASE_DIR, HARMONIZED_VARS_PATH, and OUTPUT_DIR.
    Can also be run step-by-step in a Jupyter notebook - see module docstring.
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    print("Loading variable mappings...", flush=True)
    var_labels = get_var_label_lookup()
    priority_vars = set(var_labels.keys())
    print(f"Found {len(priority_vars)} priority variables\n", flush=True)

    print(f"Loading MeasurementObservation files from {BASE_DIR}...", flush=True)
    result, excluded = load_with_excluded_summary(BASE_DIR, priority_vars)

    print("\n" + "="*80)
    print("GENERATING SUMMARY STATISTICS")
    print("="*80)
    summary = summarize_observations(result.df, var_labels)
    summary_file = OUTPUT_DIR / f'measurement_summary_{timestamp}.tsv'
    summary.to_csv(summary_file, sep='\t', index=False)
    print(f"Summary saved to: {summary_file}")

    sheets_tsv, coverage = format_for_sheets(summary, var_labels)
    sheets_file = OUTPUT_DIR / f'table_s5_paste_{timestamp}.tsv'
    sheets_file.write_text(sheets_tsv)
    print(f"Sheets paste-ready TSV saved to: {sheets_file}")

    coverage_file = OUTPUT_DIR / f's5_coverage_{timestamp}.tsv'
    coverage.to_csv(coverage_file, sep='\t', index=False)
    print(f"S5 coverage report saved to: {coverage_file}")

    print("\n" + "="*80)
    print("RUN SUMMARY")
    print("="*80)
    cohort_dirs = sorted(result.df['source_dir'].unique()) if len(result.df) else []
    print(f"Files loaded: {len(cohort_dirs)} cohort/consent dirs")
    print(f"Total rows (priority-filtered): {len(result.df):,}")
    if len(result.df):
        print(f"Unique observation types: {result.df['observation_type'].nunique()}")
        print(f"Unique participants: {result.df['associated_participant'].nunique():,}")

    if len(excluded):
        total_excluded = int(excluded['count'].sum())
        print(f"\nExcluded {total_excluded:,} non-priority rows. Top 10 codes:")
        print(excluded.head(10).to_string(index=False))

    print("\n" + "="*80)
    print("S5 COVERAGE")
    print("="*80)
    counts = coverage['status'].value_counts().to_dict()
    print(f"matched: {counts.get('matched', 0)}, "
          f"aliased: {counts.get('aliased', 0)}, "
          f"missing: {counts.get('missing', 0)}")
    missing = coverage[coverage['status'] == 'missing']['s5_label'].tolist()
    if missing:
        print(f"\nMissing from data ({len(missing)}):")
        for m in missing:
            print(f"  - {m}")


if __name__ == '__main__':
    main()