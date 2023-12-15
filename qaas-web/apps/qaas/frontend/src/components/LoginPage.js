import React from 'react';
import Box from '@mui/material/Box';
import TextField from '@mui/material/TextField';
import Button from '@mui/material/Button';
import { useNavigate } from 'react-router-dom'

import ArrowForwardIcon from '@mui/icons-material/ArrowForward';
export default function LoginPage() {
    const navigate = useNavigate();
    const navigateToQaas = () => {
        navigate('/qaas');
    };

    return (
        <div style={{ marginTop: 80 }}>
            <Box>
                <div>Username</div>
                <TextField sx={{ width: '55ch', pr: '5px' }} label="Username" variant="outlined"/>
                <div>Password</div>
                <TextField sx={{ width: '55ch', pr: '5px' }} label="Password" variant="outlined"/>
                <Button sx={{ ml: 3 }} variant="contained" onClick={navigateToQaas} endIcon={<ArrowForwardIcon />}>Log In</Button>
            </Box>
        </div>


    )

}