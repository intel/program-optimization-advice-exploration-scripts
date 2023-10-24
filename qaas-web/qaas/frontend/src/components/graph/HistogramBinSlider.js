import React from 'react';
import { Slider } from 'antd';

const HistogramBinSlider = ({ onChange }) => {
    return (
        <Slider
            min={1.0}
            max={1.1}
            step={0.01}
            defaultValue={1.1}
            onChange={onChange}
        />
    );
};

export default HistogramBinSlider;
