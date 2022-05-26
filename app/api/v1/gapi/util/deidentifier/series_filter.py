from typing import Union

from pydicom import Dataset


class SeriesFilter:
    LHC = {
        "SliceThickness": 1.5,
        "ScanType": {
            "IN": ["IN", "TLC"],
            "EX": ["EX", "RV"],
            "DOSE": ["DOSE"],
            "SCOUT": ["SCOUT"],
        },
    }

    GALA = {
        "SliceThickness": 1.5,
        "ScanType": {"IN": ["IN", "TLC"], "EX": ["EX", "RV"]},
    }

    PRECISE = {
        "SliceThickness": 1.5,
        "ScanType": {"IN": ["IN", "TLC"], "EX": ["EX", "RV"]},
    }

    SARP4 = {
        "SliceThickness": 1.5,
        "ScanType": {"IN": ["IN", "TLC"], "EX": ["EX", "RV"]},
    }

    @staticmethod
    def validate(dicom_slice: Dataset, project: str) -> Union[str, bool]:
        project_series_filter = getattr(SeriesFilter, project).copy()
        series_description = dicom_slice.SeriesDescription

        # Validate SliceThickness
        if (
            "SliceThickness" in dicom_slice
            and "SliceThickness" in project_series_filter
        ):
            series_slice_thickness = dicom_slice.SliceThickness
            if (
                isinstance(series_slice_thickness, float)
                and series_slice_thickness > project_series_filter["SliceThickness"]
            ):
                return False

        # Validate ScanType with substring check in SeriesDescription
        if "ScanType" in project_series_filter:
            for scan_type, validator_strings in project_series_filter[
                "ScanType"
            ].items():
                for validator_string in validator_strings:
                    if validator_string in series_description:
                        return scan_type

        return False
