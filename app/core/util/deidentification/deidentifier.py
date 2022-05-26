import os
from os.path import dirname, basename
from typing import List
from pathlib import Path
from pydicom import dcmread
from gspread import Cell

from app.config import config
from app.api.v1.gapi.dal import GSheetsDAL, get_gsheets_dal
from app.core.gapi.models import QCTScan
from .models import DeidScan
from .tags import TAGS_TO_ANONYMIZE


class Deidentifier:
    gsheet_dal: GSheetsDAL = get_gsheets_dal()

    def __init__(self, qct_scan: QCTScan) -> None:
        self.qct_scan = qct_scan

    def analyze(self) -> DeidScan:
        def get_dicom_slice_paths(scan_path) -> List[Path]:
            dicom_slice_paths = []

            for base, _, files in os.walk(scan_path):
                for file in files:
                    dicom_slice_path = os.path.join(base, file)
                    if dirname(dicom_slice_path) == scan_path:
                        dicom_slice_paths.append(dicom_slice_path)
                    else:
                        print(
                            "Error: Original DICOM folder depth greater than 1. Check the folder structure or the path."
                        )

            return dicom_slice_paths

        deid_scan = DeidScan(self.qct_scan)
        dicom_slice_paths = get_dicom_slice_paths(deid_scan.dcm_path)
        deid_scan.construct_deid_scan(dicom_slice_paths)

        return deid_scan

    def deidentify(self, deid_scan: DeidScan) -> None:
        for scan_type, series_dict in deid_scan.series_to_deidentify_dict.items():
            for series in series_dict.values():
                # Update deid_in_path, deid_ex_path
                if not deid_scan.qct_scan.deid_in_path and scan_type == "IN":
                    deid_scan.qct_scan.deid_in_path = os.path.relpath(
                        series.deid_path, config.p_drive_path_prefix
                    )
                if not deid_scan.qct_scan.deid_ex_path and scan_type == "EX":
                    deid_scan.qct_scan.deid_ex_path = os.path.relpath(
                        series.deid_path, config.p_drive_path_prefix
                    )

                for slice_path in series.slice_paths:
                    try:
                        dicom_slice = dcmread(slice_path)
                        # Update MRN
                        if not deid_scan.qct_scan.mrn:
                            deid_scan.qct_scan.mrn = dicom_slice.PatientID

                        dicom_slice.PatientID = (
                            dicom_slice.PatientName
                        ) = deid_scan.qct_scan.study_id
                        dicom_slice.PatientBirthDate = (
                            dicom_slice.PatientBirthDate[:-4] + "0101"
                        )
                        # Record proj at 'DeidentificationMethod' tag
                        dicom_slice.add_new(
                            [0x0012, 0x0063], "LO", deid_scan.qct_scan.proj
                        )
                        # Remove PHI, private tags
                        for tag in TAGS_TO_ANONYMIZE:
                            if tag in dicom_slice:
                                delattr(dicom_slice, tag)
                        dicom_slice.remove_private_tags()
                    except:
                        print("Error occurred while de-identifying dicom slices")
                    try:
                        deid_slice_path = os.path.join(
                            series.deid_path, basename(slice_path)
                        )
                        dicom_slice.save_as(deid_slice_path)
                    except:
                        print("Error occured while saving de-identified dicom slices")

    @staticmethod
    def update_qctworksheet_on_deidentification(deid_scan: DeidScan):
        mrn_cell = Cell(deid_scan.qct_scan.row_index, 3, deid_scan.qct_scan.mrn)
        deid_in_cell = Cell(
            deid_scan.qct_scan.row_index, 8, deid_scan.qct_scan.deid_in_path
        )
        deid_ex_cell = Cell(
            deid_scan.qct_scan.row_index, 9, deid_scan.qct_scan.deid_ex_path
        )

        Deidentifier.gsheet_dal.update_cells(
            deid_scan.qct_scan.proj, [mrn_cell, deid_in_cell, deid_ex_cell]
        )

    def run(self) -> None:
        deid_scan = self.analyze()
        self.deidentify(deid_scan)
        Deidentifier.update_qctworksheet_on_deidentification(deid_scan)
        return {"Message": "Success!!!"}


def run_deidentifier(ct_scan: QCTScan):
    return Deidentifier(ct_scan).run()
