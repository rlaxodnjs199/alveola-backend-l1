import os
from os.path import dirname, basename
import string
from typing import List, Set, Dict
from pathlib import Path

from pydicom import dcmread

from app.config import config
from app.core.gapi.models import QCTScan
from .series_filter import SeriesFilter


class DeidScan:
    def __init__(self, qct_scan: QCTScan) -> None:
        self.qct_scan = qct_scan
        self.dcm_path: Path = self.get_dcm_path()
        self.deid_path: Path = self.get_deid_path()
        self.series_to_deidentify: Set = set()
        self.series_to_deidentify_dict: Dict[str, Dict[str, DeidSeries]] = {}
        self.series_not_to_deidentify: Set = set()

    def get_dcm_path(self) -> Path:
        return os.path.join(config.p_drive_path_prefix, self.qct_scan.dcm_path)

    def get_deid_path(self) -> Path:
        try:
            root_dir = dirname(self.dcm_path)
            deid_root_dir_components = basename(root_dir).split("_")[:3]
            deid_root_dir_components.extend(["deid", basename(root_dir).split("_")[-1]])
            deid_root_dir = ("_").join(deid_root_dir_components)
            deid_root_dir_path = os.path.join(dirname(root_dir), deid_root_dir)
            deid_scan_path = os.path.join(deid_root_dir_path, basename(self.dcm_path))
        except:
            print("Error: Check Original CT scan folder naming convetion.")

        if not os.path.exists(deid_root_dir_path):
            os.mkdir(deid_root_dir_path)
        if not os.path.exists(deid_scan_path):
            os.mkdir(deid_scan_path)

        return deid_scan_path

    def construct_deid_scan(self, dicom_slice_paths: List[Path]) -> None:
        series_filter = SeriesFilter()

        for dicom_slice_path in dicom_slice_paths:
            dicom_slice = dcmread(dicom_slice_path)
            series_uuid = dicom_slice.SeriesInstanceUID
            scan_type = series_filter.validate(dicom_slice, self.qct_scan.proj)

            if series_uuid in self.series_to_deidentify:
                self.series_to_deidentify_dict[scan_type][
                    series_uuid
                ].slice_paths.append(dicom_slice_path)
            elif series_uuid in self.series_not_to_deidentify:
                continue
            else:
                if scan_type:
                    self.series_to_deidentify.add(series_uuid)
                    if scan_type not in self.series_to_deidentify_dict:
                        self.series_to_deidentify_dict[scan_type] = {}
                    self.series_to_deidentify_dict[scan_type][series_uuid] = DeidSeries(
                        series_uuid, scan_type, self
                    )
                    self.series_to_deidentify_dict[scan_type][
                        series_uuid
                    ].slice_paths.append(dicom_slice_path)
                else:
                    self.series_not_to_deidentify.add(series_uuid)


class DeidSeries:
    def __init__(self, uuid: str, type: str, deid_scan: DeidScan) -> None:
        self.uuid = uuid
        self.type = type
        self.qct_scan = deid_scan.qct_scan
        self.deid_scan = deid_scan
        self.deid_path: Path = self.get_deid_path()
        self.slice_paths: List[Path] = []

    def get_deid_path(self) -> Path:
        deid_series_dir = ("_").join(
            [
                "DCM",
                self.qct_scan.proj,
                self.qct_scan.subj,
                self.type + self.qct_scan.fu,
            ]
        )
        # Multiple same type of scans avaialbe: Need to attach postfix to the dirname
        num_of_scans_with_same_type = len(
            self.deid_scan.series_to_deidentify_dict[self.type]
        )
        if num_of_scans_with_same_type > 0:
            postfix_list = string.ascii_lowercase
            postfix = postfix_list[num_of_scans_with_same_type - 1]
            deid_series_dir = deid_series_dir + postfix
        deid_series_path = os.path.join(self.deid_scan.deid_path, deid_series_dir)

        if not os.path.exists(deid_series_path):
            os.mkdir(deid_series_path)

        return deid_series_path
