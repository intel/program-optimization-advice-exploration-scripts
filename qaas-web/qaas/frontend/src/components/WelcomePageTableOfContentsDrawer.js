import React, { useState } from 'react';
import Drawer from '@mui/material/Drawer';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemText from '@mui/material/ListItemText';
import ListItemButton from '@mui/material/ListItemButton';
import { useNavigate } from 'react-router-dom';
import ArrowForwardIosIcon from '@mui/icons-material/ArrowForwardIos';

import './css/drawer.css'
const DrawerItem = ({ level, text, path, children, navigateToSection, selectedItem, hasChildren }) => {
    const isSelected = selectedItem === path;
    return (
        <ListItem>
            <ListItemButton
                className={`level level${level} ${isSelected ? 'highlight-color' : ''} hover-color`}
                onClick={() => navigateToSection(path, children)}
            >
                <ListItemText primary={text} />
                {hasChildren && <ArrowForwardIosIcon fontSize="small" />}

            </ListItemButton>
        </ListItem>
    );
};



const WelcomePageTableOfContentsDrawer = () => {

    const navigate = useNavigate();
    const [selectedItem, setSelectedItem] = useState(null);
    const [expandedSections, setExpandedSections] = useState([]);


    function renderItems(items) {
        return items.map((item) => {
            const hasChildren = item.children && item.children.length > 0;
            return (
                <React.Fragment key={item.path}>
                    <DrawerItem
                        level={item.level}
                        text={item.text}
                        path={item.path}
                        children={item.children}
                        navigateToSection={navigateToSection}
                        selectedItem={selectedItem}
                        hasChildren={hasChildren}
                    />
                    {expandedSections.includes(item.path) && hasChildren && renderItems(item.children)}
                </React.Fragment>
            );
        });
    }

    const navigateToSection = (path, children) => {
        if (children) {
            if (!expandedSections.includes(path)) {
                setExpandedSections(prevSections => [...prevSections, path]);
            } else {
                setExpandedSections(prevSections => prevSections.filter(section => section !== path));
            }
        } else {
            navigate(path);
            setSelectedItem(path);
        }
    };




    const drawerItems = [
        { level: 1, text: 'Overview', path: '/' },
        { level: 1, text: 'A. Quality definitions', path: '/quality_definitions' },
        { level: 1, text: 'B. Constraints and Scope', path: '/constraints_and_scope' },
        {
            level: 1, text: 'C. Initial QaaS offerings', path: '/initial_qaas_offerings', children: [
                {
                    level: 2, text: 'C1. CQ Overview', path: '/c1', children: [
                        { level: 3, text: 'Overview', path: '/cq_overview' },
                        { level: 3, text: 'C1.1 Performance', path: '/cq_overview_performance' },
                        { level: 3, text: 'C1.2 Portability', path: '/cq_overview_portability' },
                        { level: 3, text: 'C1.3 Energy', path: '/cq_overview_energy' },

                    ]
                },
                { level: 2, text: 'C2. Automatic application analysis', path: '/automatic_application_analysis' },
                { level: 2, text: 'C3. Manual Interactive Mode', path: '/manual_interactive_mode' },
                {
                    level: 2, text: 'C4. Quality 10-year trend realities', path: '/c4', children: [
                        { level: 3, text: 'Overview', path: '/quality_10_year_trend_realities' },
                        { level: 3, text: 'C4.1 Conclusions', path: '/quality_10_year_trend_conclusions' },
                    ]
                },
            ]
        },
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
                        marginTop: '50px',
                        alignItems: 'center',
                        minWidth: '250px',

                    },

                }}
            >
                <List>
                    {renderItems(drawerItems)}
                </List>
            </Drawer>
        </div>
    );
};

export default WelcomePageTableOfContentsDrawer;
