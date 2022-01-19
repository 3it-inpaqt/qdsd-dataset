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
from cv2 import FileStorage, FILE_STORAGE_READ, FILE_STORAGE_WRITE


class EDLines:
    def __init__(self, processedSignal=None, _paramFree=True, _line_error=1.0, _min_line_len=-1,
                 _max_distance_between_two_lines=6.0, _max_error=1.3, _tempFolder="tempFilesEDLines"):

        self.dll = cdll.LoadLibrary(os.path.join(os.getcwd(),"EDLines_FileStorage.dll"))
        self.tempFolder = _tempFolder
        self.wd = os.getcwd()
        self.in_fname = "tempImage_input.yaml"
        self.out_fname = "tempImage_output.yaml"
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

    def writeMatrix(self, fpath, img, matrixName="mat"):
        cv_file = FileStorage(fpath, FILE_STORAGE_WRITE)
        cv_file.write(matrixName, img.astype(np.uint8))

    def readMatrix(self, fpath, matrixName="mat"):
        cv_file = FileStorage(fpath, FILE_STORAGE_READ)
        matrix = cv_file.getNode(matrixName).mat()
        cv_file.release()

        return matrix

    def lineDetection(self, input_fpath, output_fpath):
        self.dll.lineDetection(create_string_buffer(input_fpath.encode('utf-8')),
                               create_string_buffer(output_fpath.encode('utf-8')),
                               c_bool(self.parameterFree), c_double(self.line_error),
                               c_int(self.min_line_len), c_double(self.max_distance_between_two_lines),
                               c_double(self.max_error))

    def lineRecognition(self, img, keepFiles=False):

        pathlib.Path(self.tempFolder).mkdir(parents=True, exist_ok=True)
        os.chdir(self.tempFolder)  # Set wd to temp one to save files from edlines
        try:
            self.writeMatrix(self.in_fpath, img)
            #            print("Wrote the mat in bin file")
            self.lineDetection(self.in_fpath, self.out_fpath)
            #            print("Line detection is done")
            #            self.lineSegmentsParameters = self.matread(tempFileName)
            #            print("Line segments Parameters imported")
            # ('Slope', 'Intercept', 'sx','sy','ex','ey','segNo','len')

            self.lineSegmentsImage = self.readMatrix(self.out_fpath)
            #            print("Line Segments image imported")
            self.clusterList = [np.array(np.where(self.lineSegmentsImage == i)) \
                                for i in np.unique(self.lineSegmentsImage[self.lineSegmentsImage > 0])]
            self.transition = self.lineSegmentsImage.astype(np.uint8)
            self.transition[self.transition > 0] = -1.
            if not keepFiles:  # Delete the temp files
                os.remove(self.in_fpath)
                os.remove(self.out_fpath)

        finally:
            os.chdir(self.wd)


def applyEDLines(processedSignal, ed):
    newSignal = deepcopy(processedSignal)
    ed.lineRecognition(newSignal, keepFiles=False)
    newSignal.transition.zData = ed.transition
    return newSignal
