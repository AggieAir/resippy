import unittest
from resippy.utils import file_utils
from resippy.utils.envi_utils import EnviUtils
from resippy.test_runner import demo_data_base_dir, demo_data_save_dir
import numbers
import numpy as np
import os

BASE_TEST_DIR = file_utils.get_path_from_subdirs(demo_data_base_dir, ["test_data", "envi_header_tests"])
SAVE_BASE_DIR = file_utils.get_path_from_subdirs(demo_data_save_dir, ['envi_header_demo_tests'])
file_utils.make_dir_if_not_exists(SAVE_BASE_DIR)


class TestChipper(unittest.TestCase):
    print("ENVI HEADER TESTS")
    print("")

    def test_read_write(self):
        print("CHECKING TO ENSURE ENVI HEADERS ARE EQUIVALENT AFTER READING / WRITING AND READING IN AGAIN.")
        test_dir = os.path.join(BASE_TEST_DIR, "test_read_write")
        all_fnames = file_utils.get_all_files_in_dir(test_dir)
        for fname in all_fnames:
            print("testing envi header: " + os.path.basename(fname))
            header_1 = EnviUtils.read_envi_header(fname)
            header_save_fname = os.path.join(SAVE_BASE_DIR, 'self_test_reflectance_saved.hdr')
            EnviUtils.write_envi_header(header_1, header_save_fname)
            header_2 = EnviUtils.read_envi_header(header_save_fname)

            # make sure the original and new envi headers have all the same keys
            assert header_1.keys() == header_2.keys()

            # make sure all the values are the same.
            for header_key in header_1.keys():
                header1_val = header_1[header_key]
                header2_val = header_2[header_key]
                if type(header1_val) == str:
                    assert header1_val == header2_val
                elif isinstance(header1_val, numbers.Number):
                    assert header1_val == header2_val
                elif type(np.array([1.0, 2.0, 3.0])) == type(header1_val):
                    assert (header1_val == header2_val).all()
                else:
                    print("encountered uknown data type")
                    assert False

        print("Header fields after reading, writing and reading back in passed.")

    def test_map_info(self):
        test_dir = os.path.join(BASE_TEST_DIR, "test_read_write")
        test_fname = os.path.join(test_dir, "blind_test_rad.hdr")
        header = EnviUtils.read_envi_header(test_fname)
        map_info_string = header['map info']
        EnviUtils.map_info_to_wkt(map_info_string)


if __name__ == '__main__':
    unittest.main()
