from resippy.utils import string_utils
import numpy as np
from numpy import ndarray
from pyproj import Proj
import gdal
import resippy.utils.proj_utils as proj_utils
import os

ENVI_DTYPES_TO_NUMPY = {"1": np.uint8,
                        "2": np.int16,
                        "3": np.int32,
                        "4": np.float32,
                        "5": np.float64,
                        "6": None,
                        "7": None,
                        "8": None,
                        "9": np.complex64,
                        "10": None,
                        "11": None,
                        "12": np.uint16,
                        "13": np.uint32,
                        "14": np.int64,
                        "15": np.uint64,
                        }


class EnviUtils:
    @classmethod
    def envi_dtype_to_numpy_dtype(cls,
                                  envi_dtype,       # type: int
                                  ):
        return ENVI_DTYPES_TO_NUMPY[str(int(envi_dtype))]

    @classmethod
    def numpy_dtype_to_envi_dtype(cls,
                                  envi_dtype,       # type: int
                                  ):
        for key, val in ENVI_DTYPES_TO_NUMPY.items():
            if val == envi_dtype:
                return int(key)

    @classmethod
    def read_envi_header(cls,
                         header_fname,      # type: str
                         ):                 # type:(...)-> dict
        valid_entries = ['acquisition time',
                         'band names',
                         'bands',
                         'bbl',
                         'byte order',
                         'class lookup',
                         'class names',
                         'classes',
                         'cloud cover',
                         'complex function',
                         'coordinate system string',
                         'data gain values',
                         'data ignore value',
                         'data offset values',
                         'data reflectance gain values',
                         'data reflectance offset values',
                         'data type',
                         'default bands',
                         'default stretch',
                         'dem band',
                         'dem file',
                         'description',
                         'file type',
                         'fwhm',
                         'geo points',
                         'header offset',
                         'interleave',
                         'lines',
                         'map info',
                         'pixel size',
                         'projection info',
                         'read procedures',
                         'reflectance scale factor',
                         'rpc info',
                         'samples',
                         'security tag',
                         'sensor type',
                         'solar irradiance',
                         'spectra names',
                         'sun azimuth',
                         'sun elevation',
                         'wavelength',
                         'wavelength units',
                         'x start',
                         'y start',
                         'z plot average',
                         'z plot range',
                         'z plot titles']

        with open(header_fname, 'r') as content_file:
            header_text = content_file.read()

        header_text = string_utils.cleanup_newlines(header_text)

        envi_header_dict = {}

        def is_equals_entry(all_text):
            bracket_index = all_text.find("{")
            equals_index = all_text.find("=")
            newline_index = all_text.find(os.linesep)
            if equals_index == -1:
                return False
            if bracket_index < newline_index and bracket_index != -1:
                return False
            elif equals_index < newline_index:
                return True

        def is_bracket_entry(all_text):
            bracket_index = all_text.find("{")
            newline_index = all_text.find(os.linesep)
            if bracket_index == -1:
                return False
            elif bracket_index < newline_index:
                return True
            else:
                return False

        def entry_has_newline(all_text):
            newline_index = all_text.find(os.linesep)
            if newline_index != -1:
                return True

        while header_text is not "":

            key = ""
            val = ""

            if is_bracket_entry(header_text):
                right_brace_index = header_text.find('}')
                entry_text = header_text[0:right_brace_index+1]
                key, val = str.split(entry_text, '=', 1)
                val = val.strip()
                header_text = header_text[right_brace_index + 1:]

            elif is_equals_entry(header_text):
                linesep_index = header_text.find(os.linesep)
                entry_text = header_text[0:linesep_index]
                key, val = entry_text.split('=')
                header_text = header_text[linesep_index + 1:]

            elif entry_has_newline(header_text):
                newline_index = header_text.find(os.linesep)
                header_text = header_text[newline_index+1:]

            else:
                header_text = header_text[1:]

            key = str.rstrip(key)
            key = str.lstrip(key)
            envi_header_dict[key] = str.strip(val)

        if "" in envi_header_dict.keys():
            del envi_header_dict[""]

        bracket_ndarr_entries = ['fwhm', 'wavelength']
        equals_int_entries = ['samples', 'lines', 'bands', 'header offset', 'data type', 'byte order', 'x start',
                                'y start']

        for header_key in envi_header_dict:
            header_val = envi_header_dict[header_key]
            if str.lower(header_key) in bracket_ndarr_entries:
                header_val = cls.bracket_entry_to_ndarray(header_val)
                envi_header_dict[header_key] = header_val
            if str.lower(header_key) in equals_int_entries:
                header_val = header_val.replace(' ', '')
                header_val = int(header_val)
                envi_header_dict[header_key] = header_val
        return envi_header_dict

    @classmethod
    def write_envi_header(cls,
                          header_dict,      # type: dict
                          header_fname,     # type: str
                         ):                 # type:(...)-> None
        with open(header_fname, "w") as f:
            f.write("ENVI" + "\n")
            for key, val in header_dict.items():
                if type(val) == np.ndarray:
                    val = cls.ndarray_to_bracket(val)
                f.write(key + " = " + str(val))
                f.write("\n")

    # TODO: add more interleave formats, only BIP is currently supported
    @classmethod
    def write_envi_image(cls,
                         image_cube,                    # type: np.ndarray
                         output_fname,                  # type: str
                         output_header_fname=None,      # type: str
                         interleave='bil',              # type: str
                         ):                             # type: (...) -> None
        if output_header_fname is None:
            output_header_fname = output_fname + ".hdr"
        ny, nx, nbands = image_cube.shape
        raw_data = np.zeros(ny*nx*nbands, dtype=image_cube.dtype)
        if interleave == 'bil':
            raw_data_counter = 0
            for l in range(ny):
                for b in range(nbands):
                    data_chunk = image_cube[l, :, b]
                    raw_data[raw_data_counter:raw_data_counter+nx] = data_chunk
                    raw_data_counter = raw_data_counter+nx
        raw_data.tofile(output_fname)

        envi_dtype = cls.numpy_dtype_to_envi_dtype(image_cube.dtype)

        envi_header = {}
        envi_header['samples'] = int(nx)
        envi_header['lines'] = int(ny)
        envi_header['bands'] = int(nbands)
        envi_header['data type'] = int(envi_dtype)
        envi_header['interleave'] = interleave
        cls.write_envi_header(envi_header, output_header_fname)

    @classmethod
    def read_envi_image(cls,
                        image_file,             # type: str
                        header_file=None,       # type: str
                        ):                      # type: (...) -> np.ndarray
        if header_file is None:
            try:
                header_guesses = [image_file[:-4] + ".hdr", image_file + ".hdr"]
                for header_guess in header_guesses:
                    if os.path.exists(header_guess):
                        header_file = header_guess
            except FileNotFoundError:
                print("Can't find a corresponding header file for this ENVI image.")
        envi_header = cls.read_envi_header(header_file)
        nx = int(envi_header['samples'])
        ny = int(envi_header['lines'])
        nbands = int(envi_header['bands'])
        envi_dtype = envi_header['data type']
        interleave = envi_header['interleave']
        envi_image_data = cls.read_all_image_data_to_numpy_array(image_file, envi_dtype)
        image_cube = cls.construct_image_cube_from_raw_data(envi_image_data, nx, ny, nbands, interleave)
        return image_cube

    @classmethod
    def read_all_image_data_to_numpy_array(cls,
                                           envi_image_path,     # type: str
                                           envi_dtype,          # type: int
                                           ):                   # type: (...) -> np.ndarray
        numpy_dtype = cls.envi_dtype_to_numpy_dtype(envi_dtype)
        numpy_data = np.fromfile(envi_image_path, numpy_dtype)
        return numpy_data

    @classmethod
    def construct_image_cube_from_raw_data(cls,
                                           raw_envi_data,       # type: np.ndarray
                                           nx,                  # type: int
                                           ny,                  # type: int
                                           nbands,              # type: int
                                           interleave,          # type: str
                                           ):                   # type: (...) -> np.ndarray
        image_cube = np.zeros((ny, nx, nbands), dtype=raw_envi_data.dtype)
        if interleave == 'bil':
            raw_data_counter = 0
            for l in range(ny):
                for b in range(nbands):
                    data_chunk = raw_envi_data[raw_data_counter:raw_data_counter+nx]
                    image_cube[l, :, b] = data_chunk
                    raw_data_counter = raw_data_counter+nx
        return image_cube

    @classmethod
    def bracket_entry_to_ndarray(cls,
                                 bracket_text  # type: str
                                 ):
        bracket_text = bracket_text.replace(os.linesep, "").replace(" ", "").replace('{', "").replace('}', "")
        bracket_strs = bracket_text.split(",")
        bracket_floats = [float(s) for s in bracket_strs]
        return np.array(bracket_floats)

    @classmethod
    def ndarray_to_bracket(cls,
                           arr,      # type: ndarray
                           ):        # type: (...) -> str
        str_arr = np.array2string(arr)
        str_arr = str.strip(string_utils.remove_repeating_spaces(str_arr)[1:-1])
        str_arr = str_arr.replace(' ', ', ')
        str_arr = '{' + str_arr + '}'
        return str_arr

    @classmethod
    def map_info_to_geot_and_proj(cls,
                        envi_map_info_string,       # type: str
                        ):                          # type: (...) -> str
        """

        :param envi_map_info_string:
        :return:
        """
        # remove brackets if we need to
        if envi_map_info_string[0] == '{':
            envi_map_info_string = envi_map_info_string[1:-1]
        envi_map_info_list = str.split(envi_map_info_string, ",")

        projection_name = envi_map_info_list[0]
        reference_pixel_x_tie_point = envi_map_info_list[1]
        reference_pixel_y_tie_point = envi_map_info_list[2]
        pixel_easting = envi_map_info_list[3]
        pixel_northing = envi_map_info_list[4]
        x_pixel_size = envi_map_info_list[5]
        y_pixel_size = envi_map_info_list[6]
        projection_zone = envi_map_info_list[7]
        north_or_south = envi_map_info_list[8]
        datum = envi_map_info_list[9]
        units = envi_map_info_list[10]

    @classmethod
    def get_proj_wkt_from_fname(cls,
                            fname,          # type: str
                            ):              # type: (...) -> str
        dset = gdal.Open(fname, gdal.GA_ReadOnly)
        proj_wkt = dset.GetProjection()
        dset = None
        return proj_wkt

    @classmethod
    def get_proj_from_fname(cls,
                            fname,          # type: str
                            ):              # type: (...) -> Proj
        wkt = cls.get_proj_wkt_from_fname(fname)
        proj = proj_utils.wkt_to_proj(wkt)
        return proj

    @classmethod
    def get_geotransform_from_fname(cls,
                                    fname,          # type: str
                                    ):              # type: (...) -> tuple
        dset = gdal.Open(fname, gdal.GA_ReadOnly)
        geot = dset.GetGeoTransform()
        dset = None
        return geot