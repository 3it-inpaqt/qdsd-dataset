# -*- coding: utf-8 -*-
"""
Created on Tue Sep 15 10:43:45 2020

@author: Mathieu Moras
"""

import numpy as np
import matplotlib.pyplot as plt
import os
import processing_scripts.EDLines.EDLines_bin as edlines


def peak_detection(dataz, datax, treshold_multiplicator, noise_calibration_data, alpha_init=0.1, alpha_filter=0.2, Transconductance=False):
    
    # data list intitialisation
    x = []
    x_filtered = []
    v = []
    
    # data processing list intialisation
    derivative = []
    standard_deviation = []
    std_data = []
    sigma = treshold_multiplicator
    signal = [0, 0, 0, 0]
    
    for i in range(len(noise_calibration_data)-1):
        std_data.append(noise_calibration_data[i])
        
    # ewma_init parameters initialisation
    ewma_init = []
    s1_t = dataz[0]    
    alpha1 = alpha_init
    
    ewma_init.append(s1_t)
    
    # ewma_filter parameters initialisation
    ewma_filter = []
    s2_t = 0
    alpha2 = alpha_filter

    # peak detection algorithm 
    n = 0
    data_l = len(dataz)
    
    while n < data_l:
        if not Transconductance:
            if len(x) < 3:
                x.append(dataz[n])
                v.append(datax[n])
                n += 1
            else:
                x.append(dataz[n])
                s1_t = (alpha1 * x[-2]) + ((1 - alpha1) * s1_t)
                ewma_init.append(s1_t)
                direction = ewma_init[-1] - ewma_init[-2]
                
                if direction >= 0:
                    dy = (x[-1] - x[-2]) / (v[-1] - v[-2])
                    derivative.append(dy)
                else:
                    dy = (x[-1] - x[-2]) / (v[-1] - v[-2])
                    derivative.append(dy)
                
                if len(derivative) == 1:
                    s2_t = derivative[0]
                    ewma_filter.append(s2_t)
    
                else:
                    s2_t = (alpha2 * derivative[-1] + ((1 - alpha2) * s2_t))
                    ewma_filter.append(s2_t)
                
                if len(ewma_filter) >= 2:
                    x_filtered.append(derivative[-1] - ewma_filter[-2])
                    
                    std = np.sqrt(np.mean(abs(np.power(std_data,2))))
                    standard_deviation.append(std)                    
                        
                    treshold_up = sigma * np.array(standard_deviation)
                    treshold_down = -1 * np.array(treshold_up)
                    
                    if len(treshold_up) > 2 and x_filtered[-1] > treshold_up[-1]:
                        if len(ewma_filter) > 0:
                            if 3 < len(ewma_filter) <= 30:
                                trend = sum(ewma_filter[:-2])/len(ewma_filter[:-2])
                            elif len(ewma_filter) <= 3:
                                trend = sum(ewma_filter[:-2])/len(ewma_filter[:-2])
                            elif len(ewma_filter) > 30:
                                trend = sum(ewma_filter[-30:-2])/len(ewma_filter[-30:-2])
                            
                            if derivative[-1] > 0 and trend < 0:
                                signal.append(1)
                            else :
                                signal.append(0)
                                std_data.append(x_filtered[-1])
                        else:
                            signal.append(0)
                            std_data.append(x_filtered[-1])
                                
                    elif len(treshold_down) > 2 and x_filtered[-1] < treshold_down[-1]: 
                        if len(ewma_filter) > 0:
                            if 3 < len(ewma_filter) <= 30:
                                trend = sum(ewma_filter[:-2])/len(ewma_filter[:-2])
                            elif len(ewma_filter) <= 3:
                                trend = sum(ewma_filter[:-2])/len(ewma_filter[:-2])       
                            elif len(ewma_filter) > 30:
                                trend = sum(ewma_filter[-30:-2])/len(ewma_filter[-30:-2])
        
                            if derivative[-1] < 0 and trend > 0:
                                signal.append(1)
                            else :
                                signal.append(0)
                                std_data.append(x_filtered[-1])
                        else:
                            signal.append(0)
                            std_data.append(x_filtered[-1])
                    else:
                        signal.append(0)
                        std_data.append(x_filtered[-1])
                             
                n += 1
        else:
            if len(x) < 2:
                x.append(dataz[n])
                v.append(datax[n])
                n += 1
            else:
                x.append(dataz[n])
                v.append(datax[n])
                
                if len(derivative) == 1:
                    s2_t = x[0]
                    ewma_filter.append(s2_t)
    
                else :    
                    s2_t = (alpha2 * x[-1] + ((1 - alpha2) * s2_t))
                    ewma_filter.append(s2_t)
                if len(ewma_filter) >= 2:
                    x_filtered.append(x[-1] - ewma_filter[-2])
                    
                    std = np.sqrt(np.mean(abs(np.power(std_data,2))))
                    standard_deviation.append(std)
                                      
                    treshold_up = sigma * np.array(standard_deviation)
                    treshold_down = -1 * np.array(treshold_up)
                    
                    if len(treshold_up) > 2 and x_filtered[-1] > treshold_up[-1]:
                        if len(ewma_filter) > 0:
                            if 3 < len(ewma_filter) <= 30:
                                trend = sum(ewma_filter[:-2])/len(ewma_filter[:-2])
                            elif len(ewma_filter) <= 3:
                                trend = sum(ewma_filter[:-2])/len(ewma_filter[:-2])
                            elif len(ewma_filter) > 30:
                                trend = sum(ewma_filter[-30:-2])/len(ewma_filter[-30:-2])
                            
                            if x[-1] > 0 and trend < 0:
                                signal.append(1)
                            else :
                                signal.append(0)
                                std_data.append(x_filtered[-1])
                        else:
                            signal.append(0)
                            std_data.append(x_filtered[-1])
                                
                    elif len(treshold_down) > 2 and x_filtered[-1] < treshold_down[-1]: 
                        if len(ewma_filter) > 0:
                            if 3 < len(ewma_filter) <= 30:
                                trend = sum(ewma_filter[:-2])/len(ewma_filter[:-2])
                            elif len(ewma_filter) <= 3:
                                trend = sum(ewma_filter[:-2])/len(ewma_filter[:-2])       
                            elif len(ewma_filter) > 30:
                                trend = sum(ewma_filter[-30:-2])/len(ewma_filter[-30:-2])
        
                            if x[-1] < 0 and trend > 0:
                                signal.append(1)
                            else :
                                signal.append(0)
                                std_data.append(x_filtered[-1])
                        else:
                            signal.append(0)
                            std_data.append(x_filtered[-1])
                    else:
                        signal.append(0)
                        std_data.append(x_filtered[-1])
                         
                n += 1
                
    return signal#, derivative, ewma_filter, standard_deviation, x_filtered


def derive(y, x):
    
    derivative = []
    
    for i in range(1, len(y)):
        dx = (y[i] - y[i - 1]) / (x[i] - x[i - 1])
        derivative.append(dx)
    
    return np.array(derivative)


def calibration_noise(dataz, datax, Transconductance=False):
    if len(dataz.shape) == 2:
        x_dim = len(dataz[0, :])
        y_dim = len(dataz[:, 0])
        calibration_data = dataz[(int(0.8 * y_dim)), :int(0.5 * x_dim)]
        xdata_cut = datax[:int(0.5 * x_dim)]
    else:
        x_dim = len(datax)
        xdata_cut = datax[:int(0.5 * x_dim)]
        calibration_data = dataz[:int(0.5 * x_dim)]
        
    if not Transconductance:
        gradient = derive(calibration_data, xdata_cut)
        
        ewma = []
        alpha = 0.1
        s_t = gradient[0]
        ewma.append(s_t)
        for i in range(len(gradient)-1):
            s_t = (alpha * gradient[i] + ((1-alpha) * s_t))
            ewma.append(s_t)
                
        noise_data = np.array(gradient) - np.array(ewma)
        return noise_data#, ewma, gradient
    
    else:
        return calibration_data


def extract_transition(diagram_data, x, sigma):

    noise_calibration = calibration_noise(diagram_data, x)
    transition_diagram = []

    for j in range(len(diagram_data[:, 0])):
        trace = diagram_data[j, :]
        trace_transition = peak_detection(trace, x, sigma, noise_calibration, Transconductance=False)
        transition_diagram.append(trace_transition)

    ed = edlines.EDLines()
    ed.lineRecognition(np.array(transition_diagram) * -1)
    data = ed.lineSegmentsImage
    data[np.nonzero(data)] = 1
    return data
