import React from 'react';
import Typography from '@mui/material/Typography';
import './css/welcome_page.css'
export default function WelcomePage() {


    return (
        <div style={{ display: 'flex', marginTop: 20 }}>

            <div style={{ flexGrow: 1, marginLeft: '10px' }}>
                <Typography variant="h3" align="center" gutterBottom>
                    Welcome to QaaS (Quality as a Service):
                    <Typography variant="h5" gutterBottom>

                        Users submit codes – QaaS returns results; nothing further is required of users.
                    </Typography>

                </Typography>
                <Typography variant="h6" gutterBottom>
                    <p>

                        Welcome to the QaaS Computational Quality (CQ) overview. The website focuses on comparing CQ results across computer systems and application areas, both current and over the past ten years. Our first goal is to allow users to understand both the state of the art in HPC, as well as recent progress trends. Our major goals are to provide automatic analyses and improvement of developer submitted apps, followed by manual interactive advice.
                    </p>



                </Typography>


            </div>
        </div>
    )
}