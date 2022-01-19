# -*- coding: utf-8 -*-
"""
Created on Sat May 25 23:47:57 2019

@author: Olivier
"""
from ctypes import cdll, c_int, c_double, c_bool, create_string_buffer
import numpy as np
import os
import pathlib2 as pathlib
from copy import deepcopy


class EDLines:
    def __init__(self, processedSignal=None, _paramFree=True, _line_error=1.0, _min_line_len=-1,
                 _max_distance_between_two_lines=6.0, _max_error=1.3, _tempFolder="tempFilesEDLines"):

        self.dll = cdll.LoadLibrary("C:/Users/moras/OneDrive/Documents/Uni/Maitrise/Project/GIT"
                                    "/Mat_Stef_QDot_Autotuning/Autotuning/EDLines/EDLines_bin.dll")
        self.tempFolder = _tempFolder
        self.wd = os.getcwd()
        self.in_fname = "tempImage_input.bin"
        self.out_fname = "tempImage_output.bin"
        self.in_fpath = os.path.join(self.wd, self.tempFolder, self.in_fname)
        self.out_fpath = os.path.join(self.wd, self.tempFolder, self.out_fname)

        self.matType = {0: np.uint8, 4: np.uint32, 5: np.float32}

        self.parameterFree = _paramFree
        self.line_error = _line_error
        self.min_line_len = _min_line_len
        self.max_distance_between_two_lines = _max_distance_between_two_lines
        self.max_error = _max_error

        if processedSignal:
            self.lineRecognition(processedSignal)

    def matread(self, fpath):
        metaData = np.fromfile(fpath, np.uint32, 3)
        f = open(fpath, "rb")
        f.seek(12, os.SEEK_SET)
        binData = np.fromfile(f, self.matType[metaData[2]])
        npMat = binData.reshape(metaData[0], metaData[1])
        return npMat

    def matwrite(self, fpath, npMat):
        nRow, nCol = npMat.shape
        metaData = np.array([nRow, nCol, 0], dtype=int)
        binData = npMat.ravel().astype(np.uint8)

        newFile = open(fpath, "wb")  # wb pour write binary
        newFile.write(metaData)
        newFile.write(binData)
        newFile.close()

    def lineDetection(self, input_fpath, output_fpath):
        self.dll.lineDetection(create_string_buffer(input_fpath.encode('utf-8')),
                               create_string_buffer(output_fpath.encode('utf-8')),
                               c_bool(self.parameterFree), c_double(self.line_error),
                               c_int(self.min_line_len), c_double(self.max_distance_between_two_lines),
                               c_double(self.max_error))

    def lineRecognition(self, img, keepFiles=False):
        """
        Takes a transition image as input and output lines detected in an image format.
        :param img: Values should be 0 or 255
        :param keepFiles: if you want to keep the temp files sent/received to/from the DLL.
        """

        pathlib.Path(self.tempFolder).mkdir(parents=True, exist_ok=True)

        try:
            self.matwrite(self.in_fpath, img)
            self.lineDetection(self.in_fpath, self.out_fpath)
            self.lineSegmentsImage = self.matread(self.out_fpath)
            self.clusterList = [np.array(np.where(self.lineSegmentsImage == i))
                                for i in np.unique(self.lineSegmentsImage[self.lineSegmentsImage > 0])]
            self.transition = self.lineSegmentsImage.astype(int)
            self.transition[self.transition > 0] = -1.
            if not keepFiles:  # Delete the temp files
                os.remove(self.in_fpath)
                os.remove(self.out_fpath)
        finally:
            pass


def applyEDLines(processedSignal, ed):
    newSignal = deepcopy(processedSignal)
    ed.lineRecognition(newSignal, keepFiles=False)
    newSignal.transition.zData = ed.transition
    return newSignal

