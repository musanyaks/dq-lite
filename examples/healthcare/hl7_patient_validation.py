"""Healthcare patient record validation example.

Demonstrates domain-specific checks for HL7/FHIR-style patient data.
This is a template for contributors to add their own domain packs.
"""

import pandas as pd
from dqlite import validate, expect


def create_patient_records() -> pd.DataFrame:
    """Generate sample patient records."""
    return pd.DataFrame({
        "patient_id": ["P-10001", "P-10002", "P-10003"],
        "mrn": ["MRN-001", "MRN-002", "MRN-003"],  # Medical Record Number
        "age": [45, 67, -5],  # Will fail: negative age
        "gender": ["M", "F", "X"],  # Will fail if strict
        "diagnosis_code": ["ICD10-E11", "ICD10-I10", None],  # Will fail: null
        "visit_date": ["2024-01-15", "2024-02-20", "2024-03-10"],
    })


def main():
    df = create_patient_records()

    result = validate(df, expectations=[
        expect("patient_id").not_null(),
        expect("patient_id").unique(),
        expect("mrn").not_null(),
        expect("age").between(0, 120),
        expect("gender").in_set(["M", "F", "O", "U"]),  # Male, Female, Other, Unknown
        expect("diagnosis_code").not_null(),
        expect("diagnosis_code").matches_regex(r"ICD10-[A-Z][0-9]{2}"),
    ])

    print(result.to_markdown())
    return result


if __name__ == "__main__":
    main()
