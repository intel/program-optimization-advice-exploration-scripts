import React from 'react';
import { Typography } from '@mui/material';
import mut_base_speedup from '../images/mut_base_speedup.png'
import mut_least_speedup from '../images/mut_least_speedup.png'
import base_speedup from '../images/base_speedup.png'
import least_speedup from '../images/least_speedup.png'

const SpeedupFormula = ({ level }) => {
    let imgContainerStyle = {
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        height: '100px',
        margin: '10px'
    };

    let imgStyle = {
        maxWidth: '100%',
        maxHeight: '100%',
        objectFit: 'contain'
    };

    let imageUrlR, imageUrlM;

    // Check if level prop is 'mutation' or 'loop', then set the image URLs accordingly
    if (level === 'mutation') {
        imageUrlR = mut_base_speedup;
        imageUrlM = mut_least_speedup;

    } else if (level === 'loop') {
        imageUrlR = base_speedup;
        imageUrlM = least_speedup;

    }




    return (
        <div className='component-background component-spacing'>
            <div style={imgContainerStyle}>
                <img style={imgStyle} src={imageUrlR} alt="Speedup R formula" />
            </div>
            <div style={imgContainerStyle}>
                <img style={imgStyle} src={imageUrlM} alt="Speedup M formula" />
            </div>
        </div>
    );
};

export default SpeedupFormula;
