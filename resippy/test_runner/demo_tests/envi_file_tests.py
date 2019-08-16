import unittest
from resippy.utils import file_utils
from resippy.utils.envi_utils import EnviUtils
from resippy.test_runner import demo_data_base_dir, demo_data_save_dir
from resippy.utils import proj_utils
import os

radiance_cube_fname = file_utils.get_path_from_subdirs(demo_data_base_dir, ["image_data",
                                                                            "hyperspectral",
                                                                            "cooke_city",
                                                                            "self_test",
                                                                            "HyMap",
                                                                            "self_test_rad.img"])


class TestChipper(unittest.TestCase):
    print("ENVI HEADER TESTS")
    print("")

    def test_get_projection(self):
        print("")
        print("Testing the ability to get projection information from an envi file")
        proj = EnviUtils.get_proj_from_fname(radiance_cube_fname)
        assert proj.srs == '+proj=utm +zone=12 +datum=WGS84 +units=m +no_defs '
        print("test passed!")

    def test_get_geotransform(self):
        print("")
        print("Testing the ability to get a geotransform from an envi file")
        geot = EnviUtils.get_geotransform_from_fname(radiance_cube_fname)
        assert geot[0] == 583171.5
        assert geot[1] == 3.0
        assert geot[2] == -0.0
        assert geot[3] == 4986234.5
        assert geot[4] == -0.0
        assert geot[5] == -3.0
        print("test passed!")


if __name__ == '__main__':
    unittest.main()
