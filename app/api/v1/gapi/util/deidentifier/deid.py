import os
import re
import string
from os.path import basename, dirname
from pathlib import Path
from typing import Dict, List
from pydicom import Dataset, dcmread

from app.api.v1.gapi.dal import GSheetsDAL
from app.core.gapi.enums import ScanTypeEnum, ValidProtocolEnum
from app.core.gapi.models import CTScan
from .tags import TAGS_TO_ANONYMIZE


class deidentify:
    def __init__(self, ctscan: CTScan) -> None:
        self.ctscan = ctscan
        self.series_filter = None

    @property
    def series_dict(self):
        pass

    def get_dicom_paths(dicom_path: Path):
        pass

    # create ~~~_deid_tk folder
    def set_deid_root_dir_path(dicom_path: Path):
        pass


def deidentify_ctscan(ctscan: CTScan, gsheets_dal: GSheetsDAL) -> None:
    if not ctscan.type or ctscan.type not in list(ScanTypeEnum):
        print("Invalid CT scan type")

    def create_processed_series_dict(scan_type: str):
        if scan_type == ScanTypeEnum.IN:
            return {ScanTypeEnum.IN: {}}
        elif scan_type == ScanTypeEnum.EX:
            return {ScanTypeEnum.EX: {}}
        elif scan_type == ScanTypeEnum.BOTH:
            return {ScanTypeEnum.IN: {}, ScanTypeEnum.EX: {}}

    def get_dicom_paths(ctscan_path: Path) -> List[Path]:
        dicom_paths = []
        for base, _, files in os.walk(ctscan_path):
            for file in files:
                file_path = os.path.join(base, file)
                if dirname(file_path) == ctscan_path:
                    dicom_paths.append(file_path)
                else:
                    print(
                        "Exception: CT scan folder path greater than 1. Check the folder structure."
                    )
                    return []
        return dicom_paths

    def prepare_deid_dicom_dir(ctscan_path: Path) -> Path:
        try:
            root_folder = dirname(ctscan_path)
            deid_root_folder = basename(root_folder).split("_")[:3]
            deid_root_folder.extend(["deid", root_folder.split("_")[-1]])
            deid_root_folder = ("_").join(deid_root_folder)
            deid_root_folder_path = os.path.join(dirname(root_folder), deid_root_folder)
            deid_ctscan_folder_path = os.path.join(
                deid_root_folder_path, basename(ctscan_path)
            )
        except:
            print("Exception: CT scan folder naming convention is wrong.")

        if not os.path.exists(deid_root_folder_path):
            os.mkdir(deid_root_folder_path)
        if not os.path.exists(deid_ctscan_folder_path):
            os.mkdir(deid_ctscan_folder_path)

        return deid_ctscan_folder_path

    def prepare_deid_dicom_subdir(
        ctscan: CTScan,
        dicom: Dataset,
        deid_dicom_dir_path: Path,
        processed_series_dict: Dict,
    ):
        series_uuid = dicom.SeriesInstanceUID
        # Prepare deid_dicom_subdir_path
        if series_uuid in processed_series_dict[ctscan.type]:
            deid_dicom_subdir_path = processed_series_dict[ctscan.type][series_uuid]
        else:
            deid_dicom_subdir = ("_").join(
                [
                    "DCM",
                    ctscan.proj,
                    ctscan.subj.replace("-", ""),
                    ctscan.type + ctscan.fu,
                ]
            )
            # Check if there are multiple IN or EX in one set
            num_of_duplicate_IN_EX_series = len(processed_series_dict[ctscan.type])
            if num_of_duplicate_IN_EX_series > 0:
                postfix_list = [string.ascii_lowercase]
                postfix = postfix_list[num_of_duplicate_IN_EX_series - 1]
                deid_dicom_subdir = deid_dicom_subdir + postfix
            # Create de-identified dicom subdirectory path (ex: ./DCM_PROJ_SUBJ_INEX0a)
            deid_dicom_subdir_path = os.path.join(
                deid_dicom_dir_path, deid_dicom_subdir
            )
            if not os.path.exists(deid_dicom_subdir_path):
                os.mkdir(deid_dicom_subdir_path)
            processed_series_dict[ctscan.type][series_uuid] = deid_dicom_subdir_path

        return deid_dicom_subdir_path

    def validate_ct_protocol(dicom: Dataset, scan_type: str):
        ct_protocol = dicom.SeriesDescription.upper()
        if scan_type == ScanTypeEnum.IN:
            for validate_protocol_substring in ValidProtocolEnum.IN.value:
                if validate_protocol_substring in ct_protocol:
                    return True
        else:
            for validate_protocol_substring in ValidProtocolEnum.EX.value:
                if validate_protocol_substring in ct_protocol:
                    return True

        return False

    def deidentify_dicom_slice(
        ctscan: CTScan,
        deid_dicom_dir_path: Path,
        dicom_slice_path: Path,
        processed_series_dict: Dict,
    ):
        dicom: Dataset = dcmread(dicom_slice_path)
        if validate_ct_protocol(dicom, ctscan.type):
            deid_dicom_subdir_path = prepare_deid_dicom_subdir(
                ctscan, dicom, deid_dicom_dir_path, processed_series_dict
            )
            try:
                print(ctscan.mrn)
                if not ctscan.mrn:
                    ctscan.mrn = dicom.patientID
                    print(ctscan.mrn)
                dicom.PatientID = dicom.PatientName = ctscan.subj
                dicom.PatientBirthDate = dicom.PatientBirthDate[:-4] + "0101"
                # Record proj at 'DeidentificationMethod' tag
                dicom.add_new([0x0012, 0x0063], "LO", ctscan.proj)
                # Remove PHI, private tags
                for tag in TAGS_TO_ANONYMIZE:
                    if tag in dicom:
                        delattr(dicom, tag)
                dicom.remove_private_tags()
                deid_dicom_slice_path = os.path.join(
                    deid_dicom_subdir_path, basename(dicom_slice_path)
                )
                dicom.save_as(deid_dicom_slice_path)
            except:
                print("Error occurred while de-identifying dicom images")

    def get_deid_path(scan_type: ScanTypeEnum, processed_series_dict: Dict) -> Path:

        return list(processed_series_dict[scan_type].values())[0]

    def calc_fu(project: str, subject: str, gsheets_dal: GSheetsDAL):
        subjects = gsheets_dal.get_all_subjects(project, subject)
        fu = len(subjects) - 1

        if fu < 0:
            print("Error: Entry did not exist in QCTWorksheet")
            return 0

        return fu

    def update_ctscan(ctscan: CTScan, processed_series_dict: Dict) -> CTScan:
        if processed_series_dict[ScanTypeEnum.IN]:
            ctscan.deid_in_path = get_deid_path(ScanTypeEnum.IN, processed_series_dict)
        if processed_series_dict[ScanTypeEnum.EX]:
            ctscan.deid_ex_path = get_deid_path(ScanTypeEnum.EX, processed_series_dict)
        ctscan.subj = re.sub("[^a-zA-Z0-9]", "", ctscan.study_id)
        ctscan.fu = calc_fu(ctscan.proj, ctscan.subj, gsheets_dal)
        print(ctscan)
        return ctscan

    # need to update later: Both -> look at either IN or EX path, otherwise look at specific path
    dicom_paths = get_dicom_paths(ctscan.dcm_in_path)
    deid_dicom_dir_path = prepare_deid_dicom_dir(ctscan.dcm_in_path)

    processed_series_dict = create_processed_series_dict(ctscan.type)
    for dicom_slice_path in dicom_paths:
        deidentify_dicom_slice(
            ctscan, deid_dicom_dir_path, dicom_slice_path, processed_series_dict
        )

    ctscan = update_ctscan(ctscan, processed_series_dict)
    gsheets_dal.update_scan_on_deidentification(ctscan)
