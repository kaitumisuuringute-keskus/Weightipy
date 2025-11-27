# Nested (Segmented) Weighting

Standard RIM weighting tries to fit the global distribution of a dataset to specific targets. However, this can fail when demographic distributions vary significantly between subgroups (e.g., Region or Ethnicity).

**The Problem:**
Imagine two ethnic groups:
*   **Ethnicity A:** Population is 57% Male / 43% Female.
*   **Ethnicity B:** Population is 49% Male / 51% Female.

If you simply weight the whole dataset to 53% Male (the global average), you might accidentally force Ethnicity A to be 53% Male (too low) and Ethnicity B to be 53% Male (too high).

**The Solution:**
Nested weighting creates independent weighting groups for each slice (Ethnicity), ensuring the internal demographics are correct for *that specific group*, while also correcting the size of the groups themselves.

---

## 1. Using Reference Microdata (`scheme_from_df`)

The easiest way to handle this is if you have a "Census" or "Golden Standard" dataframe. This dataframe should contain the demographic combinations and a frequency column.

**Example Census Data (Microdata / Detailed Wide Format):**
| gender | age_group | ethnicity | freq |
|:---|:---|:---|---:|
| Female | 25-34 | B | 226 |
| Male | 25-34 | B | 320 |
| Female | 55+ | A | 391 |

### Creating the Schema

You can create a nested schema by simply providing the `col_filter` argument.

```python
# OPTION A: Nested Weighting (Correct Subgroups)
# Weight Gender and Age specific to each Ethnicity
schema_nested = wp.scheme_from_df(
    df_census,
    cols_weighting=["gender", "age_group"],
    col_freq="freq",
    col_filter="ethnicity"  # <--- The Magic Parameter
)

# OPTION B: Simple Weighting (Incorrect Subgroups)
# Weights globally. Ignores the relationship between Ethnicity and Gender.
schema_simple = wp.scheme_from_df(
    df_census,
    cols_weighting=["gender", "age_group", "ethnicity"],
    col_freq="freq"
)
```

---

## 2. Using Tidy/Long Aggregate Data (`scheme_from_long_df`)

Often, Census bureaus do not release microdata. Instead, they provide **tables** or **API exports** in a "Long" or "Tidy" format. This format lists one row per category count rather than per individual/combination.

**Example Census Data (Tidy / Long Format):**

| Region | Variable | Category | Count |
|:-------|:---------|:---------|------:|
| North  | Gender   | Male     | 400   |
| North  | Gender   | Female   | 600   |
| North  | Age      | 18-24    | 200   |
| North  | Age      | 25+      | 800   |
| South  | Gender   | Male     | 500   |
| South  | Gender   | Female   | 500   |
| South  | Age      | 18-24    | 100   |
| South  | Age      | 25+      | 900   |

### Creating the Schema

Weightipy can ingest this format directly. When `col_filter` is used, it performs two actions:
1.  **Global Targets:** It calculates the total size of "North" vs "South" (by summing the counts of the first variable it finds, e.g., Gender).
2.  **Nested Targets:** It creates specific Rim groups for North and South with their respective Age/Gender distributions.

```python
df_tidy = pd.read_csv("census_api_export.csv")

schema = wp.scheme_from_long_df(
    df=df_tidy,
    col_variable="Variable", # Column name containing 'Gender', 'Age'
    col_category="Category", # Column name containing 'Male', '18-24'
    col_value="Count",       # Column name containing the numbers
    col_filter="Region"      # <--- Nesting happens here
)

# Now apply to your survey
df_survey["weights"] = wp.weight(df_survey, schema)
```

---

## 3. Using a Dictionary (`scheme_from_dict`)

If you do not have a census dataframe but you have the targets written down, you can construct a **Segmented Scheme Dictionary**.

This structure defines the `segment_targets` (how big the groups should be globally) and `segments` (the targets within each group).

```python
targets = {
    "segment_by": "ethnicity",
    
    # 1. Global Targets: Ethnicity A is 54% of total, B is 46%
    "segment_targets": {"A": 54.0, "B": 46.0}, 
    
    "segments": {
        # 2. Inner Targets for A
        "A": {
            "gender": {"Male": 57.0, "Female": 43.0},
            "age_group": {"18-24": 17.0, "25-34": 17.0, "55+": 26.0, ...}
        },
        # 3. Inner Targets for B
        "B": {
            "gender": {"Male": 49.0, "Female": 51.0},
            "age_group": {"18-24": 24.0, "25-34": 15.0, "55+": 26.0, ...}
        }
    }
}

# Validate before creating schema
wp.validate_scheme_dict(df_survey, targets)

# Create Scheme
schema = wp.scheme_from_dict(targets)
df["weights"] = wp.weight(df, schema)
```

---

## 4. Using the Rim Class (Advanced)

For full programmatic control, you can build the `Rim` object manually. This is useful if you need to programmatically generate complex filter definitions or partial targets.

```python
schema_rim = wp.Rim("manual_nested")

# 1. Add Group A
schema_rim.add_group(
    name="ethnicity_A",
    filter_def="ethnicity == 'A'",  # Pandas query string
    targets=[
        {"gender": {"Male": 57, "Female": 43}},
        {"age_group": {"18-24": 17, "25-34": 17, "55+": 26}}
    ]
)

# 2. Add Group B
schema_rim.add_group(
    name="ethnicity_B",
    filter_def="ethnicity == 'B'",
    targets=[
        {"gender": {"Male": 49, "Female": 51}},
        {"age_group": {"18-24": 24, "25-34": 15, "55+": 26}}
    ]
)

# 3. Set Global Group Targets (Critical Step)
# This ensures the sum of weights for A vs B matches these proportions.
schema_rim.group_targets({
    "ethnicity_A": 54,
    "ethnicity_B": 46
})

df["weights"] = wp.weight(df, schema_rim)
```

---

## 5. Validating the Data

When working with nested schemas, it is easy to make mistakes (e.g., a category exists in Ethnicity A but not in Ethnicity B). Use the validation tools to check your data.

```python
# Check for errors
report = wp.validate_scheme(df_survey, schema_rim, raise_error=False)

if not report.empty:
    print(report)
```

---

<details>
  <summary><strong>Click to see the full Python script used to generate the comparison tables</strong></summary>

```python
import pandas as pd
import numpy as np
import weightipy as wp
import itertools

## 1. GENERATE FAKE CENSUS
# Define categories for demographic variables
genders = ['Male', 'Female']
age_groups = ['18-24', '25-34', '35-44', '45-54', '55+']
ethnicities = ['A', 'B']

# Create all unique combinations of demographic variables
all_combinations = list(itertools.product(genders, age_groups, ethnicities))

# Prepare data for the DataFrame
data_for_df = []
np.random.seed(42)
for gender_val, age_group_val, race_val in all_combinations:
    # Create some bias so A and B are different
    bias = 100 if race_val == 'A' and gender_val == 'Male' else 0
    
    data_for_df.append({
        'gender': gender_val,
        'age_group': age_group_val,
        'ethnicity': race_val,
        'freq': np.random.randint(50, 500) + bias
    })

df_census = pd.DataFrame(data_for_df)
df_census["inv_freq"] = 1 / df_census["freq"]

## 2. GENERATE FAKE SURVEY
# Sample 1000 responders from df_census (biased sample)
df_survey = df_census.sample(n=1000, replace=True, random_state=99, weights=df_census["inv_freq"])
df_survey = df_survey[['gender', 'age_group', 'ethnicity']].reset_index(drop=True)

## 3. CREATE SCHEMAS
# Nested
schema_nested = wp.scheme_from_df(
    df_census,
    cols_weighting=["gender", "age_group"],
    col_freq="freq",
    col_filter="ethnicity"
)
# Simple
schema_simple = wp.scheme_from_df(
    df_census,
    cols_weighting=["gender", "age_group", "ethnicity"],
    col_freq="freq"
)

## 4. WEIGHT THE DATA
df_survey["weight_nested"] = wp.weight(df_survey, schema_nested)
df_survey["weight_simple"] = wp.weight(df_survey, schema_simple)

## 5. COMPARE RESULTS
def compare(df_census, df_survey):
    rows = []
    for demo in ["gender", "age_group", "ethnicity"]:
        values = df_survey[demo].unique()
        for value in values:
            df_sub_census = df_census[df_census[demo] == value]
            df_sub_survey = df_survey[df_survey[demo] == value]

            share_census = df_sub_census["freq"].sum() / df_census["freq"].sum()
            share_survey_raw = len(df_sub_survey) / len(df_survey)
            share_survey_weighted = df_sub_survey["weight_simple"].sum() / df_survey["weight_simple"].sum()
            share_survey_nested = df_sub_survey["weight_nested"].sum() / df_survey["weight_nested"].sum()

            rows.append({
                "demo": demo,
                "value": value,
                "census": share_census,
                "survey": share_survey_raw,
                "weighted_simple": share_survey_weighted,
                "weighted_nested": share_survey_nested
            })
    return pd.DataFrame(rows).set_index(["demo", "value"]).round(2)

print("--- General Distribution ---")
print(compare(df_census, df_survey).to_markdown())

print("\n--- Ethnicity A Distribution ---")
print(compare(df_census[df_census['ethnicity']=='A'], df_survey[df_survey['ethnicity']=='A']).to_markdown())
```
</details>
