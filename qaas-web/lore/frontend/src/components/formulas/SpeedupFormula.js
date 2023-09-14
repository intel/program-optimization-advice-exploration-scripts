import React from 'react';
import { Typography } from '@mui/material';

const SpeedupFormula = ({ level }) => {
    let imageUrlR, imageUrlM;

    // Check if level prop is 'mutation' or 'loop', then set the image URLs accordingly
    if (level === 'mutation') {
        imageUrlR = process.env.PUBLIC_URL + '/images/mut_base_speedup.png';
        imageUrlM = process.env.PUBLIC_URL + '/images/mut_least_speedup.png';

    } else if (level === 'loop') {
        imageUrlR = process.env.PUBLIC_URL + '/images/base_speedup.png';
        imageUrlM = process.env.PUBLIC_URL + '/images/least_speedup.png';

    }

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
