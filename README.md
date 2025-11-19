# Weightipy

Weightipy is a modernized, lightweight, and high-performance library for weighting survey data using the RIM (iterative raking) algorithm. It is a streamlined fork of [Quantipy3](https://github.com/Quantipy/quantipy3).

### Why Weightipy?
- **Fast:** Runs up to 6x faster than Quantipy.
- **Modern:** Supports Python 3.7+ and the latest Pandas/Numpy versions.
- **Flexible:** Supports simple raking, segmented (nested) weighting, and loading targets from various census data formats.
- **Lightweight:** Removed heavy dependencies and reporting overhead to focus purely on the weighting engine.

---

## Installation

```bash
pip install weightipy
```

## Quick Start

Weightipy creates a new column of weights that aligns your dataset's distribution with specific targets.

### 1. Simple Weighting (Manual Dictionary)
If you have a simple list of percentages, you can define them in a dictionary.

```python
import weightipy as wp
import pandas as pd

# Your survey data
df = pd.read_csv("my_survey.csv")

# Define targets (percentages)
targets = {
    "age_group": {"18-24": 10.0, "25+": 90.0},
    "gender": {"Male": 49.0, "Female": 51.0}
}

# Create schema and weight
scheme = wp.scheme_from_dict(targets)
df_weighted = wp.weight_dataframe(df, scheme, weight_column="weights")

# Check efficiency
eff = wp.weighting_efficiency(df_weighted["weights"])
print(f"Weighting Efficiency: {eff:.2f}%")
```

### 2. Segmented Weighting (Nested)
A common requirement is to weight specific groups differently (e.g., weight Age and Gender *within* Region, while also correcting the size of the Regions themselves).

You can now do this in a single step using a **Segmented Scheme**:

```python
targets = {
    "segment_by": "region",
    "segment_targets": {"North": 40.0, "South": 60.0}, # Global proportions
    "segments": {
        "North": {
            "age_group": {"18-24": 15.0, "25+": 85.0},
            "gender": {"Male": 50.0, "Female": 50.0}
        },
        "South": {
            "age_group": {"18-24": 10.0, "25+": 90.0},
            "gender": {"Male": 48.0, "Female": 52.0}
        }
    }
}

scheme = wp.scheme_from_dict(targets)
df_weighted = wp.weight_dataframe(df, scheme)
```

---

## Working with Census Data

Manually typing targets is tedious. Weightipy provides tools to generate schemas directly from census tables or reference datasets.

### Scenario A: You have "Tidy/Long" Aggregates
*Common with US Census API, Eurostat, tidycensus, or SQL exports.*

If your target data looks like this:

| Region | Variable | Category | Count |
|:-------|:---------|:---------|:------|
| East   | Age      | 18-24    | 500   |
| East   | Gender   | Male     | 450   |

Use `scheme_from_long_df`:

```python
df_census = pd.read_csv("census_long_format.csv")

scheme = wp.scheme_from_long_df(
    df=df_census,
    col_variable="Variable", # Column containing 'Age', 'Gender'
    col_category="Category", # Column containing '18-24', 'Male'
    col_value="Count",       # Column containing the population count
    col_filter="Region"      # Optional: Split schema by Region
)

df_weighted = wp.weight_dataframe(df, scheme)
```

### Scenario B: You have Reference Data (Wide/Detailed)
*Common when you have a "Golden Standard" dataset, a detailed frequency table of all combinations, or raw microdata.*

If your target data looks like this (one row per combination, or one row per combination of demographic variables):

| Region | Age   | Gender | Population_Count |
|:-------|:------|:-------|:-----------------|
| East   | 18-24 | Male   | 250              |
| East   | 18-24 | Female | 260              |

Use `scheme_from_df`. Weightipy will group and sum the data to calculate the correct distributions.

```python
df_reference = pd.read_csv("census_detailed.csv")

scheme = wp.scheme_from_df(
    df=df_reference,
    cols_weighting=["Age", "Gender"],
    col_freq="Population_Count",
    col_filter="Region"  # Optional: Weight Age/Gender within Region
)

df_weighted = wp.weight_dataframe(df, scheme)
```

---

## Data Validation

Before applying weights, it is highly recommended to validate that your survey data aligns with your schema. Weightipy can detect critical errors (e.g., a category exists in the census but is missing in the survey) and warnings (e.g., targets not summing to 100%).

```python
# Get a report of all issues (does not raise exception)
report = wp.validate_scheme_dict(df, targets, raise_error=False)

if not report.empty:
    print(report)
    # Columns: [group, variable, issue_type, severity, details]

# Or strict validation (raises ValueError on Critical errors)
wp.validate_scheme_dict(df, targets, raise_error=True)
```

---

## Serialization & Advanced Usage

For advanced workflows—such as manual overrides, multi-threading, or network transmission—it is often better to work with the raw configuration dictionary rather than the `Rim` class directly.

Weightipy exposes the intermediate extraction functions for this purpose. These return a JSON-serializable dictionary.

```python
# 1. Extract raw dictionary from data
config = wp.scheme_dict_from_df(df_census, cols_weighting=..., col_freq=...)

# 2. Modify manually (e.g., fix a specific target)
config['segments']['North']['age_group']['18-24'] = 12.5

# 3. Serialize (safe for network or threading)
import json
payload = json.dumps(config)

# 4. Reconstruct Scheme later/elsewhere
scheme = wp.scheme_from_dict(config)
```

---

## API Reference

| Function | Description |
|:---|:---|
| `weight_dataframe` | Main entry point. Weights data by a scheme and appends a weight column. |
| `weight_df` | Alias to weight_dataframe |
| `weighting_efficiency` | Calculates the efficiency of the weights (Kish's effective sample size). |
| `scheme_from_dict` | Creates a scheme from a python dictionary. Supports both simple (flat) and segmented (nested) structures. |
| `scheme_from_long_df` | Creates a scheme from "Tidy" aggregate data (Variable/Category/Value columns). |
| `scheme_from_df` | Creates a scheme from a reference dataframe (Microdata or Detailed Aggregates). |
| `scheme_dict_from_df` | Extracts the raw configuration dictionary from a reference dataframe. Useful for debugging, manual adjustments, or serialization. |
| `scheme_dict_from_long_df` | Extracts the raw configuration dictionary from Tidy/Long data. |
| `validate_scheme_dict` | Validates a survey dataframe against a scheme dictionary. Checks for missing categories, NaNs, and target sums. |
| `validate_scheme` | Validates a survey dataframe against a compiled `Rim` object. |
| `Rim` | The underlying class for defining complex schemas. |
| `WeightEngine` | The engine that runs the iterative algorithm. Useful for advanced manipulation. |

## Contributing

We welcome volunteers!

*   **Run Tests:** `python3 -m pytest tests`
*   **Development:** Please include a test case with any pull request.

## Origins & Credits

Weightipy is based on **Quantipy**.

*   **Quantipy Creator:** Gary Nelson (Datasmoothie)
*   **Contributors:** Alexander Buchhammer, Alasdair Eaglestone, James Griffiths, Kerstin Müller (YouGov), Birgir Hrafn Sigurðsson, Geir Freysson.
