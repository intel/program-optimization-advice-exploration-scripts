import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Dropdown, Menu, Space } from 'antd';
import './css/TopBar.css';
import { DownOutlined, CheckOutlined, HomeOutlined } from '@ant-design/icons';
import PageSearchBar from './search/PageSearchBar';
import TableOfContents from './TableOfContents';
const pageGroups = {
    'Quality content explanations': [
        { page: 'overview', label: 'QaaS Content Overview' },
        { page: 'system_config', label: 'System Configurations' },
        { page: 'definitions', label: 'Definitions' },
        { page: 'ref', label: 'References' },
        { page: 'table_of_contents', label: 'Table of Contents' },

    ],
    'About QaaS': [
        // { page: 'login', label: 'Login' },
        // { page: 'signup', label: 'Sign Up' },
        { page: 'catalog', label: 'Catalog' },

        { page: 'contributors', label: 'Contributors' },
        { page: 'legal', label: 'Legal' },
    ],
    'Use QaaS': [
        { page: 'input', label: 'Job Submission' },
        { page: 'result', label: 'Results' },

    ]
};

function TopBar() {
    const [selectedPage, setSelectedPage] = useState('');
    const location = useLocation();

    //this is to get all the text pages under / to be under qaas content overview unless specify in page groups
    const allPages = Object.values(pageGroups).flat().map(({ page }) => page);
    // console.log(allPages)
    //listen to path change
    useEffect(() => {
        const currentPage = location.pathname.replace('/', '').split('/')[0];
        // console.log(currentPage)
        // check if currentPage is a predefined page, if not set it to under home page
        if (allPages.includes(currentPage)) {
            setSelectedPage(currentPage);
        } else {
            setSelectedPage("");
        }
    }, [location]);


    const handleTabClick = (page) => {
        setSelectedPage(page);
    };

    const buildMenuItems = (pages) => {
        return pages.map(({ page, label }) => ({
            key: page,
            label: (
                <Link to={`/${page}`} onClick={() => handleTabClick(page)}>
                    {label} {page === selectedPage ? <CheckOutlined /> : null}
                </Link>
            ),
            className: page === selectedPage ? 'selected' : ''
        }));
    };
    const isGroupSelected = (groupName) => {
        return pageGroups[groupName].some(({ page }) => page === selectedPage);
    };

    return (
        <div className="top-bar">
            <div className="home">
                <Link onClick={() => handleTabClick('')} to="/" className="home-link">
                    <HomeOutlined /> QaaS: Quality as a Service
                </Link>
            </div>
            <div className="nav-links">

                {Object.keys(pageGroups).map((groupName) => (
                    <Dropdown key={groupName} placement="bottom" menu={{ items: buildMenuItems(pageGroups[groupName]) }}>
                        <a
                            onClick={(e) => e.preventDefault()}
                            className={`nav-group ${isGroupSelected(groupName) ? 'selected' : ''}`}
                        >
                            <Space>
                                {groupName}
                                <DownOutlined />

                            </Space>

                        </a>
                    </Dropdown>
                ))}

            </div>
            <div className="right-section">
                {/* <input type="text" className="search-bar" placeholder="Search..." /> */}
                <PageSearchBar />

                <Link to="https://docs.google.com/document/d/1_H7ySm_HwrwR5xhBd4amI-CWN_n6fKYcdVMHb6vDaF4/edit?usp=sharing" className="nav-link">Google Doc Link</Link>

            </div>

        </div>
    );
}

export default TopBar;
