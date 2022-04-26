import os
import string
from os.path import basename, dirname
from pathlib import Path
from typing import Dict, List
from pydicom import Dataset, dcmread

from app.api.v1.gapi.dal import GSheetsDAL
from app.api.v1.gapi.enums import ScanTypeEnum, ValidProtocolEnum
from app.api.v1.gapi.models import CTScan
from .tags import TAGS_TO_ANONYMIZE


def deidentify_ctscan(
    ctscan: CTScan, in_ex: ScanTypeEnum, gsheets_dal: GSheetsDAL
) -> None:
    if in_ex == ScanTypeEnum.IN:
        ctscan.in_ex = ScanTypeEnum.IN.value
        ctscan_path = ctscan.dcm_in_path
    elif in_ex == ScanTypeEnum.EX:
        ctscan.in_ex = ScanTypeEnum.EX.value
        ctscan_path = ctscan.dcm_ex_path
    else:
        print("Exception: Invalid scantype input")
        return []

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
        if series_uuid in processed_series_dict[ctscan.in_ex]:
            deid_dicom_subdir_path = processed_series_dict[ctscan.in_ex][series_uuid]
        else:
            deid_dicom_subdir = ("_").join(
                [
                    "DCM",
                    ctscan.proj,
                    ctscan.subj.replace("-", ""),
                    ctscan.in_ex + ctscan.fu,
                ]
            )
            # Check if there are multiple IN or EX in one set
            num_of_duplicate_IN_EX_series = len(processed_series_dict[ctscan.in_ex])
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
            processed_series_dict[ctscan.in_ex][series_uuid] = deid_dicom_subdir_path

        return deid_dicom_subdir_path

    def validate_ct_protocol(dicom: Dataset, in_ex: str):
        ct_protocol = dicom.SeriesDescription.upper()
        # print(ct_protocol, in_ex)
        if in_ex == ScanTypeEnum.IN.value:
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
        if validate_ct_protocol(dicom, ctscan.in_ex):
            deid_dicom_subdir_path = prepare_deid_dicom_subdir(
                ctscan, dicom, deid_dicom_dir_path, processed_series_dict
            )
            try:
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

    def get_deid_dicom_destination(in_ex: str, processed_series_dict: Dict) -> Path:
        return list(processed_series_dict[in_ex].values())[0]

    def update_qctworksheet(
        ctscan: CTScan,
        deid_dicom_destination: Path,
        gsheets_dal: GSheetsDAL,
    ):
        if ctscan.in_ex == ScanTypeEnum.IN.value:
            gsheets_dal.qctworksheet.worksheet("New Template").update_cell(
                ctscan.qctworksheet_row, 8, deid_dicom_destination
            )
        else:
            gsheets_dal.qctworksheet.worksheet("New Template").update_cell(
                ctscan.qctworksheet_row, 9, deid_dicom_destination
            )

    dicom_paths = get_dicom_paths(ctscan_path)
    deid_dicom_dir_path = prepare_deid_dicom_dir(ctscan_path)

    processed_series_dict = {ScanTypeEnum.IN.value: {}, ScanTypeEnum.EX.value: {}}
    for dicom_slice_path in dicom_paths:
        deidentify_dicom_slice(
            ctscan, deid_dicom_dir_path, dicom_slice_path, processed_series_dict
        )

    deid_dicom_destination = get_deid_dicom_destination(
        ctscan.in_ex, processed_series_dict
    )
    update_qctworksheet(ctscan, deid_dicom_destination, gsheets_dal)
