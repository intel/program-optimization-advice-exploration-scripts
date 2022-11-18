import React from 'react';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import { Link } from 'react-router-dom'

export default function WelcomePage() {
    return (
        <div style={{ marginTop: 80 }}>
            <Box sx={{ width: '100%' }}>

                <Typography variant="h2" align="center" gutterBottom>
                    Welcome to QaaS (Quality as a Service):
                    <Typography variant="h3" gutterBottom>

                        Users submit codes – QaaS returns results; nothing further is required of users.
                    </Typography>

                </Typography>
                <Typography variant="h6" gutterBottom>
                    <p>
                        QaaS provides automatic and manual services for novice and expert application developers. Our focus is currently on HPC applications and includes results on several multicore architectures (GPUs in future). Quality includes performance (time, rate), power and energy, etc. Initially we focus only on performance.

                    </p>
                    <p>

                        QaaS contains several unique features that aid SW developers. Most importantly, the system is designed to avoid false positive and negative recommendations, and by automating performance enhancement steps, provides direct proof of the results. We also inform users of any measurement difficulties and tool weaknesses encountered – so users can trust the results. Our analyses cover source code, binary code, and dynamic HW counters, so most conclusions are drawn from several points of view.


                    </p>
                    <p>

                        The process of using QaaS is designed to minimize the user’s work; just submit your code, some data sets, and describe your normal running environment and list desired architectures/compilers/etc. QaaS approximates your environment as a baseline, and then explores many ways of improving the style of your code and HW setup, and applies feedback directed autotuning. It then tells you if you are already getting good performance, or if not, what needs changing to get measured gains.


                    </p>

                    <p>


                        You can click here to see a
                        <Link to={`/browseresult`}>
                            <strong> catalog </strong>
                        </Link>

                        of typical results from a range of applications and miniapps (X).


                    </p>
                </Typography>
                <Typography variant="h6" align="center" gutterBottom>
                    <div>

                        Our turnaround time is 24 hours max for jobs submitted through the menu found here (X).


                    </div>

                    <div>

                        Our
                        <Link to={`/submitservice`}>
                            <strong> tool background </strong>
                        </Link>

                        documents can be found here (X).


                    </div>
                    <div>

                        For details of our <strong>legal and security policy</strong>, click here (X).


                    </div>
                </Typography>
            </Box>
        </div>
    )
}