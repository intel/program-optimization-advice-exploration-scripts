import React from 'react';
import { Slider } from 'antd';

const HistogramBinSlider = ({ onChange, min = 1.0, max = 1.1, defaultValue = 1.1, step = 0.01 }) => {
    return (
        <Slider
            min={min}
            max={max}
            step={step}
            defaultValue={defaultValue}
            onChange={onChange}
        />
    );
};

export default HistogramBinSlider;
