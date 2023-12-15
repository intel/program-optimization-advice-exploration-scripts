import React from 'react';
import { Accordion, AccordionSummary, AccordionDetails, Typography } from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';


const AccordionComponent = ({ title, children }) => {

    return (
        <Accordion sx={{
            width: '100%',
            marginBottom: '2px',
            backgroundColor: '#dddddd',
            boxShadow: 'none',
            '&:hover': {
                backgroundColor: '#e0e0e0',
            },
        }}
        >
            <AccordionSummary
                expandIcon={<ExpandMoreIcon />}
                aria-controls="panel1a-content"
                id="panel1a-header"
            >
                <Typography sx={{
                    color: '#505260',
                    '&:hover': {
                        color: '#277383',
                    },
                }}>{title}</Typography>
            </AccordionSummary>
            <AccordionDetails sx={{ backgroundColor: '#f2f5f7' }}>
                {children}
            </AccordionDetails>
        </Accordion>
    );
};

export default AccordionComponent;