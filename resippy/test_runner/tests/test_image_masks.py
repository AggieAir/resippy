from resippy.utils.image_utils import image_utils
from resippy.image_masks.pixel_truth_mask import PixelTruthMask
import numpy as np
import unittest
import os

home_dir = os.path.expanduser("~")
tmp_h5_fname = os.path.join(home_dir, "tmp_mask.h5")
tmp_png_fname = os.path.join(home_dir, "tmp_mask.png")

ny = 960
nx = 1280


class TestCrsTools(unittest.TestCase):

    truth_numpy_arr = np.zeros((ny, nx))
    truth_numpy_arr[5:20, 5:20] = 1
    truth_numpy_arr[60:100, 60:100] = 2
    truth_dict = {
        "background": 0,
        "material1": 1,
        "material2": 2,
    }

    truth_mask = PixelTruthMask()

    truth_mask.init_from_numpy_arr_and_dict(truth_numpy_arr, truth_dict)
    truth_mask.write_to_image_file_and_csv(tmp_png_fname)
    truth_mask.write_to_h5_file(tmp_h5_fname)

    truth_mask_hd5 = PixelTruthMask()
    truth_mask_hd5.init_from_h5_file(tmp_h5_fname)

    truth_mask_image_and_csv = PixelTruthMask()
    truth_mask_image_and_csv.init_from_image_file_and_csv(tmp_png_fname)

    stop = 1