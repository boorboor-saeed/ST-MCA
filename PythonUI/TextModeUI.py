
import matplotlib.pyplot as plt
import numpy as np
import time
import sys
from scipy.optimize import curve_fit

from DeviceClass import Responds
from DeviceClass import STATES
from DeviceClass import DeviceClass
from DeviceClass import OperationModes


def gaussian(x, amplitude, mean, sigma, offset=0):
        return offset + amplitude * np.exp(-(x - mean)**2 / (2 * sigma**2))

def GaussianFit(x_data, y_data):
    p0 = [max(y_data), np.mean(x_data), np.std(x_data), min(y_data)]
    params, covariance = curve_fit(gaussian, x_data, y_data, p0=p0)
    print(params)
    return params

def UI():
    # # Create an instance of DeviceClass
    obj = DeviceClass("COM4")

    res = obj.SetAcqTime(1)
    print(res)
    res = obj.SetOperationMode(OperationModes.CH1VSCH2)
    print(res)
    res = obj.Start()
    print(res)

    if(res == Responds.OK):
        time.sleep(1)
        state = obj.GetState()
        
        while state != STATES.FREE:
            time.sleep(1)
            state = obj.GetState()
            report = obj.GetReport()
            print(report)
        
        if False:
            Avebuffer1 = obj.GetADCBuffer(1)
            Avebuffer2 = obj.GetADCBuffer(2)
            NoPulses1 = obj.GetNoPulses(1)
            Edges1 = obj.GetPulseEdges(1, NoPulses1)
            NoPulses2 = obj.GetNoPulses(2)
            Edges2 = obj.GetPulseEdges(2, NoPulses2)
            print("NoPulses1:",NoPulses1)
            print("Edges1:",Edges1)
            print("NoPulses2:",NoPulses2)
            print("Edges2:",Edges2)

            fig, ax = plt.subplots()
            plt.plot(Avebuffer1, label='Channel 1')
            plt.plot(Avebuffer2, label='Channel 2')
            plt.xlabel('time(#)')
            plt.ylabel('ADC')
            plt.title('ADC buffer')
            plt.show()

        if False:
            spectrum1 = obj.GetSpectrum(1)
            spectrum2 = obj.GetSpectrum(2)
            matrix = obj.GetMatrix()
            NP_Matrix = np.array(matrix)
            

            print("Total counts in Ch1: ", sum(spectrum1))
            print("Total counts in Ch2: ", sum(spectrum2))

            fig, ax = plt.subplots()
            plt.plot(spectrum1, label='Channel 1')
            plt.plot(spectrum2, label='Channel 2')

            # peak_value = max(spectrum1)
            # peak_index = spectrum1.index(peak_value)
            # minInd = peak_index - 200
            # maxInd = peak_index + 200
            # xdata  = list(range(minInd,maxInd))
            # ydata1 = spectrum1[minInd:maxInd]
            # ydata2 = spectrum2[minInd:maxInd]
            # xArr = np.array(xdata)
            # y1Arr = np.array(ydata1)
            # y2Arr = np.array(ydata2)
            # params1 = GaussianFit(xArr, y1Arr)
            # params2 = GaussianFit(xArr, y2Arr)
            # plt.plot(xdata, gaussian(xdata, *params1), label='Fitted Channel 1')
            # plt.plot(xdata, gaussian(xdata, *params2), label='Fitted Channel 2')

            plt.xlabel('energy bin (#)')
            plt.ylabel('count/bin')
            plt.title('Spectra')
            ax.legend()
            plt.show()

        if True:
            
            matrix = obj.GetMatrix()
            NP_Matrix = np.array(matrix)
            
            plt.imshow(NP_Matrix, cmap='viridis', origin='lower') 
            # 'viridis' is a common colormap, 'origin='upper'' sets the origin at the top-left

            # Add a colorbar to indicate the mapping of values to colors
            plt.colorbar(label='Value')
                    

            plt.xlabel('Ch1')
            plt.ylabel('Ch2')
            plt.title('Matrix')
            
            plt.show()