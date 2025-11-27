# Changelog

## Version 0.4.1

### Packaging & Build System

#### Modern Python Packaging
Migrated from deprecated `setup.py` to modern `pyproject.toml` configuration, following PEP 517/518 standards.

*   **`pyproject.toml`**: New build configuration file with complete project metadata, dependencies, and tool configurations.
*   **Build System**: Uses `setuptools>=65.0` with declarative configuration.
*   **Tool Configuration**: Integrated configurations for Black, Ruff, pytest, mypy, and coverage.
*   **Python Support**: Explicit support declaration for Python 3.7-3.13.

**Note**: Legacy files (`setup.py`, `setup.cfg`, `requirements.txt`, `requirements_dev.txt`) are retained for backward compatibility during transition period.

### Documentation

#### NumPy-Style Docstrings
All docstrings throughout the codebase have been standardized to NumPy documentation style for improved clarity and consistency.

*   **Parameters Section**: All function parameters now documented with proper type annotations and descriptions.
*   **Returns Section**: Return values documented with types and clear descriptions.
*   **Raises Section**: Exception types and conditions documented where applicable.
*   **Examples**: Usage examples added to type definitions.

**Files Updated:**
*   `weightipy/scheme.py`: 5 function docstrings updated
*   `weightipy/validate.py`: 2 function docstrings updated
*   `weightipy/weight.py`: 3 function docstrings updated (including `weighting_efficiency()`)
*   `weightipy/internal/helpers.py`: 2 function docstrings updated
*   `weightipy/internal/rim.py`: 3 method docstrings updated
*   `weightipy/internal/weight_engine.py`: 2 method docstrings updated

#### Module-Level Documentation
Added comprehensive module-level docstrings to all main source files.

*   **`weightipy/types.py`**: Type definitions for weighting schemes with usage examples
*   **`weightipy/scheme.py`**: Scheme creation and extraction utilities
*   **`weightipy/validate.py`**: Validation utilities for weighting schemes
*   **`weightipy/weight.py`**: Core weighting functions
*   **`weightipy/internal/helpers.py`**: Internal helper functions
*   **`weightipy/internal/rim.py`**: RIM algorithm implementation
*   **`weightipy/internal/weight_engine.py`**: Weight engine for scheme management

### Benefits

*   **Better IDE Support**: Improved code completion and inline documentation in IDEs.
*   **Documentation Generation**: Sphinx/mkdocs documentation.
*   **Modern Standards**: Follows current Python packaging and documentation best practices.
*   **Type Safety**: Enhanced type hints documentation for better static analysis.

---

## Version 0.4.0

### New Features

#### Nested and Segmented Weighting
Added support for creating segmented weighting schemas. This allows subgroups (e.g., Regions, Ethnicities) to be weighted by specific targets while maintaining a defined global distribution for the groups themselves.

*   **`scheme_from_dict`**: Updated to accept a nested dictionary structure containing `segment_by`, `segment_targets`, and `segments` keys.

#### Data Validation
Introduced validation functions to verify alignment between the survey data and the weighting scheme prior to execution.

*   **`validate_scheme_dict`**: Validates a configuration dictionary against a dataframe. It performs the following checks:
    *   Verifies that target proportions sum to 100% (pre-normalization).
    *   Identifies categories present in the scheme but missing from the data (Critical error).
    *   Identifies categories present in the data but missing from the scheme (Warning).
    *   Checks for the existence of all required weighting columns.
    *   Checks for NaN values in weighting columns.
*   **`validate_scheme`**: Performs the same validation checks against a compiled `Rim` object.
*   **Reporting**: Both functions return a Pandas DataFrame containing a detailed report of issues. They accept a `raise_error` boolean to optionally raise a `ValueError` upon encountering critical errors.

#### Tidy / Long Data Support
Added support for ingesting census data in the "Long" or "Aggregate" format (row-per-category), common in API exports and SQL results.

*   **`scheme_from_long_df`**: Creates a `Rim` scheme from a dataframe structured with `Variable`, `Category`, and `Count` columns. Supports the `col_filter` argument for automatic nested schema generation.

#### Serialization and Intermediate Helpers
Exposed intermediate data extraction functions to support debugging, manual schema modification, serialization, and multi-threaded environments.

*   **`scheme_dict_from_df`**: Extracts a raw configuration dictionary from microdata/detailed dataframes.
*   **`scheme_dict_from_long_df`**: Extracts a raw configuration dictionary from aggregate/tidy dataframes.

### API Changes

| Function | Status | Description |
| :--- | :--- | :--- |
| `scheme_from_dict` | **Updated** | Added logic for nested schema structures. |
| `scheme_from_long_df` | **New** | Creates schemes from Tidy/Long aggregate data. |
| `validate_scheme_dict` | **New** | Validates data against a configuration dictionary. |
| `validate_scheme` | **New** | Validates data against a `Rim` object. |
| `scheme_dict_from_df` | **New** | Extracts configuration dictionary from microdata. |
| `scheme_dict_from_long_df` | **New** | Extracts configuration dictionary from aggregate data. |