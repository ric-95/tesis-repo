import numpy as np
from abc import ABC, abstractmethod


class XCorrelationFunction(ABC):
    @abstractmethod
    def __call__(self, x_asterisk):
        pass

    @staticmethod
    @abstractmethod
    def _compute_xcorr_function(signal, index_length):
        pass


class SignalStackXCorrelationFunction(XCorrelationFunction):

    def __init__(self, signal_stack, index_length=1, zero_padded=True):
        self.__xcorr_func = self._compute_xcorr_function(signal_stack,
                                                         index_length)

    def __call__(self, x_asterisk):
        x_asterisk = np.asarray(x_asterisk)
        if x_asterisk.shape:
            return np.stack([self.__xcorr_func(x_ast) for x_ast in x_asterisk])
        return self.__xcorr_func(x_asterisk)

    @staticmethod
    def _compute_xcorr_function(signal_stack: np.ndarray,
                                index_length=1,
                                zero_padded=True):
        variance = (signal_stack**2
                    ).reshape(-1, signal_stack.shape[-1]).mean(axis=0)
        pad_value = np.nan
        if zero_padded:
            pad_value = 0

        def xcorr_func(x_asterisk):
            cov_array_list = []
            for signal in signal_stack:
                signal_ast = np.full_like(signal, pad_value)
                index_shift = int(x_asterisk/index_length)
                if index_shift:
                    signal_ast[index_shift:] = signal[:-index_shift]
                else:
                    signal_ast = signal
                cov_array = signal*signal_ast
                cov_array_list.append(cov_array)
            cov_arrays = np.stack(cov_array_list)
            return np.nanmean(cov_arrays, axis=(0, 1))/variance
        return xcorr_func

