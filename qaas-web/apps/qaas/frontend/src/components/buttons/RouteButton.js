import React from 'react';
import { useNavigate } from 'react-router-dom';
import Button from '@mui/material/Button';
import ArrowForwardIcon from '@mui/icons-material/ArrowForward';
import '../css/button.css'

export default function RouteButton({ destination, label }) {
    const navigate = useNavigate();

    const navigateToDestination = () => {
        navigate(destination);
    };

    return (
        <button
            onClick={navigateToDestination}
            className="route-button"
        >
            {label}
            <ArrowForwardIcon className="route-button-icon" />

        </button>
    );
}