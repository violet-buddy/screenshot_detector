import os
from multiprocessing import Pool

import numpy as np
import pandas as pd
from loguru import logger
from PIL import Image
from scipy import signal


def check_row(line):
    """
    Scan the elements on a row of image and check if they form a line.
    The return value is maximum length of line in th row.
    """
    max_length = 0
    cur_length = 0
    last_value = 0
    for v in line:
        if v > 0:
            if v == last_value:
                cur_length += 1
                if cur_length > max_length:
                    max_length = cur_length
            else:
                last_value = v
                cur_length = 1
    return max_length


def check_img(arr):
    """
    Scan all rows in the image and returns the number of row as a line.
    The row is a line if check_row value of the line = 1/3 length of the row.
    """
    res_index = []
    zeros = np.zeros(arr.shape)
    row_length = arr.shape[1]
    ones = np.ones(row_length)
    for idx, row in enumerate(arr):
        line_length = check_row(row)
        if 3 * line_length > row_length:
            zeros[idx] = ones
            res_index.append(idx)
    return res_index


def horizontal_filter(tuple_input):
    index, path, type_file = tuple_input
    kernel = np.array([[-1, -1, -1], [0, 0, 0], [+1, +1, +1]])
    try:
        if type_file in ["link", "path"]:
            img = np.array(Image.open(path).convert("L"))
        else:
            raise Exception('The type_file must be "link" or "path"')
        dst = signal.convolve2d(img, kernel, boundary="symm", mode="same")
        dst = np.absolute(dst)
        dst2 = np.interp(dst, (dst.min(), dst.max()), (0, 10)).astype(int)
        list_index = check_img(dst2)
        return (index, path, len(list_index))
    except Exception as e:
        logger.error(e)
        pass
    return (index, path, 0)


def detect(list_image, nprocess=40, output="output.tsv"):
    """
    Compute the number of horizontal edge of each image.

    Apply kernel computing gradient of image.

    Parameters
    ----------
    list_image: list of tuple (index, image_path, type) with
                + index is index of the image.
                + image_path is path or url to the image we need to process.
                + type is type of image_path. The type must be "link" or "path".
    nprocess: int, default = 40
                Number of the processors.
    output: str, default = "output.tsv"
                Path to output file, default is output.tsv.
                The output file with 3 columns and seperate by a tab ('\t').
                The first column is index.
                The second column is image_path.
                The third column is number of horizontal line in this image.
    Examples
    --------
    >>> import screenshot_detector
    >>> input = [(1, 'images/test/img1.jpg', 'path'), (2, 'images/test/img2.png', 'path')]
    >>> screenshot_detector.detect(list_image=input, nprocess=4, output="output_path.tsv")
    >>>
    """
    p = Pool(nprocess)
    data = p.map(horizontal_filter, list_image)
    df = pd.DataFrame(data)
    df.to_csv(output, sep="\t", index=False)
    return df


def detect_folder(folder_path, nprocess=40, output="output.tsv"):
    """
    Compute the number of horizontal edge of each image in a folder and its subfolders.
    Apply kernel computing gradient of image.

    Parameters
    ----------
    folder_path: str
                Path to the folder containing images.
    nprocess: int, default = 40
                Number of the processors.
    output: str, default = "output.tsv"
                Path to output file with detection results.
    """
    list_image = []
    idx = 0

    for root, dirs, files in os.walk(folder_path):
        for file in sorted(files):
            file_path = os.path.join(root, file)
            list_image.append((idx, file_path, "path"))
            idx += 1

    if not list_image:
        logger.warning(f"No image files found in {folder_path} or its subdirectories")
        return

    logger.info(f"Found {len(list_image)} image files to process")
    result = detect(list_image, nprocess, output)
    logger.info(f"Done! The result is saved in {output}")
    return result
