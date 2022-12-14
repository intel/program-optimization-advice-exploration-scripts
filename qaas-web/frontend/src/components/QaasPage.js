import React from 'react';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import { useNavigate } from 'react-router-dom'
import Button from '@mui/material/Button';
import ArrowForwardIcon from '@mui/icons-material/ArrowForward';

export default function QaasPage() {
    const navigate = useNavigate();
    const navigateToInput = () => {
        navigate('/input');
    };
    const navigateToResult = () => {
        navigate('/result');
    };

    return (
        <div style={{ marginTop: 80 }}>
            <Box sx={{ width: '100%' }}>

                
                <Typography variant="h6" align="center" gutterBottom>
                    
                    <div>

                        Our turnaround time is 24 hours max for jobs submitted through the menu found here
                        <Button sx={{ ml: 3 }} variant="contained" onClick={navigateToInput} endIcon={<ArrowForwardIcon />}>Input</Button>


                    </div>

                     <div>

                        Browse old submission results here
                        <Button sx={{ ml: 3 }} variant="contained" onClick={navigateToResult} endIcon={<ArrowForwardIcon />}>Result</Button>


                    </div>

                </Typography>
            </Box>
        </div>
    )
}
