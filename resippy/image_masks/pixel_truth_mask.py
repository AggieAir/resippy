import h5py
from numpy import ndarray
import numpy as np
import imageio
import h5py
import csv
import json


class PixelTruthMask:
    def __init__(self):
        self._truth_mask_data = None      # type: ndarray
        self._truth_dictionary = {}       # type: dict

    def init_from_h5_file(self,
                          fname,  # type: ndarray
                          ):
        h5f = h5py.File(fname, 'r')
        self._truth_mask_data = h5f['truth_mask'].value
        self._truth_dictionary = json.loads(h5f['truth_dictionary'].value)
        h5f.close()
        stop = 1

    def init_from_numpy_arr_and_dict(self,
                                     numpy_arr,         # type: ndarray
                                     truth_dict,        # type: dict
                                     ):
        self._truth_mask_data = numpy_arr
        self._truth_dictionary = truth_dict

    def init_from_image_file_and_csv(self,
                                     image_fname,       # type: str
                                     csv_fname=None,    # type: str
                                     ):
        self._truth_mask_data = imageio.imread(image_fname)
        if csv_fname is None:
            csv_fname = str.split(image_fname, '.')[0] + ".csv"
        with open(csv_fname) as csv_file:
            csv_reader = csv.reader(csv_file)
            for row in csv_reader:
                self._truth_dictionary[row[0]] = np.int16(row[1])

    def write_to_h5_file(self,
                         fname,
                         ):
        hf = h5py.File(fname, 'w')
        hf.create_dataset('truth_mask', data=self.get_truth_mask_data(), compression='gzip', compression_opts=9)

        dictionary_json = json.dumps(self.get_truth_dictionary())
        hf.create_dataset('truth_dictionary', data=dictionary_json)
        hf.close()

    def write_to_image_file_and_csv(self,
                                     image_fname,           # type: str
                                     csv_fname=None,        # type: str
                                     ):
        imageio.imsave(image_fname, self.get_truth_mask_data())
        if csv_fname is None:
            csv_fname = str.split(image_fname,'.')[0] + ".csv"
        with open(csv_fname, 'w') as csv_file:
            writer = csv.writer(csv_file)
            for key, value in self.get_truth_dictionary().items():
                writer.writerow([key, value])

    def get_truth_mask_data(self):
        return self._truth_mask_data.astype('uint16')

    def get_truth_dictionary(self):
        return self._truth_dictionary

    def get_truth_pixel_locations_by_name(self,
                                          name,  # str
                                          ):
        truth_pixel_val = self._truth_dictionary[name]
        pixel_locs = np.where(self.get_truth_mask_data() == truth_pixel_val)
        return pixel_locs
