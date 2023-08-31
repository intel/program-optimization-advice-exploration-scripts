import React, { useState } from 'react';
import Drawer from '@mui/material/Drawer';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemText from '@mui/material/ListItemText';
import ListItemButton from '@mui/material/ListItemButton';
import { useNavigate } from 'react-router-dom';
import './css/drawer.css'
// Define your styles as a JavaScript object

const DrawerItem = ({ level, text, path, navigateToSection, selectedItem }) => {
    const isSelected = selectedItem === path;
    console.log(text, level, `level${level}`)
    return (
        <ListItem>
            <ListItemButton
                className={`level level${level} ${isSelected ? 'highlight-color' : ''} hover-color`}

                onClick={() => navigateToSection(path)}
            >
                <ListItemText primary={text} />
            </ListItemButton>
        </ListItem>
    );
};


const WelcomePageTableOfContentsDrawer = () => {
    const navigate = useNavigate();
    const [selectedItem, setSelectedItem] = useState(null);
    const navigateToSection = (path) => {
        navigate(path);
        setSelectedItem(path);
    };

    const drawerItems = [
        { level: 1, text: 'Overview', path: '/' },

        { level: 1, text: 'A. Quality definitions', path: '/quality_definitions' },
        { level: 1, text: 'B. Constraints and Scope', path: '/constraints_and_scope' },
        { level: 1, text: 'C. Initial QaaS offerings', path: '/initial_qaas_offerings' },
        { level: 2, text: 'C1. CQ Overview', path: '/cq_overview' },
        { level: 2, text: 'C2. Automatic application analysis', path: '/automatic_application_analysis' },
        { level: 2, text: 'C3. Manual Interactive Mode', path: '/manual_interactive_mode' },
        { level: 3, text: 'C3.1 Subsection', path: '/c3_1_subsection' },
        { level: 2, text: 'C4. Quality 10-year trend realities', path: '/quality_10_year_trend_realities' },
        { level: 3, text: 'C4.1 Conclusions', path: '/conclusions' },
    ];
    return (
        <div >
            <Drawer
                className="drawer"
                anchor="left"
                variant="permanent"

                ModalProps={{
                    hideBackdrop: true,
                }}

                sx={{
                    '& .MuiDrawer-paper': {
                        marginTop: '64px',
                        alignItems: 'center',
                        minWidth: '250px',

                    },

                }}
            >
                <List>
                    {drawerItems.map((item) => (
                        <DrawerItem
                            key={item.path}
                            level={item.level}
                            text={item.text}
                            path={item.path}
                            navigateToSection={navigateToSection}
                            selectedItem={selectedItem}
                        />
                    ))}
                </List>
            </Drawer>
        </div>
    );
};

export default WelcomePageTableOfContentsDrawer;
