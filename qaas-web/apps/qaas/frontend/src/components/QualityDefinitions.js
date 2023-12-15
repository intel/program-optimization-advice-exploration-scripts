import React from 'react';
import { useNavigate } from 'react-router-dom'
import Button from '@mui/material/Button';
import ArrowForwardIcon from '@mui/icons-material/ArrowForward';
import Typography from '@mui/material/Typography';

import RouteButton from './buttons/RouteButton';

export default function QualityDefinitions() {
    const navigate = useNavigate();
    const navigateToHome = () => {
        navigate('/');
    };
    return (
        <div style={{ margin: 80 }}>
            <Typography variant="h4" gutterBottom>
                We define quality to include performance, portability, reliability, cost of operation, and related topics. Each of these has important aspects clarified and quantified by QaaS:


            </Typography>

            <ol>
                <Typography variant="h5" gutterBottom>
                    <li>Performance is shown in various units, including time, Gflops, domain- or app-specific figures of merit (FoMs), etc. QaaS is also sensitive to measuring the confidence one can have in performance (and other) metrics, an aspect of Reliability.</li>
                    <li>Portability refers to the ability to run an app across various systems. Missing technology dependencies can prevent porting a code, and even worse prevent performance portability e.g. a compiler that doesn’t work on some machine. We regard this as another aspect of Reliability.</li>
                    <li>Operating costs for HPC can be substantial, so choosing the right number of processors, and using low power cores can be important, as is running in minimal time. So high performance at low power defines a challenging balance-optimization.</li>


                </Typography>

            </ol>


            <RouteButton destination="/" label="Go back" />

        </div>
    );
}