import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Dropdown, Menu, Space } from 'antd';
import './css/TopBar.css';
import { DownOutlined, CheckOutlined } from '@ant-design/icons';

const pageGroups = {
    'Quality content explanations': [
        { page: '', label: 'QaaS Content Overview' },
        { page: 'system_config', label: 'System Configurations' },
        { page: 'definitions', label: 'Definitions' },
        { page: 'ref', label: 'References' },
    ],
    'About QaaS': [
        { page: 'login', label: 'Login' },
        { page: 'signup', label: 'Sign Up' },
        { page: 'catalog', label: 'Catalog' },
        { page: 'input', label: 'Job Submission' },
        { page: 'result', label: 'Results' },
        { page: 'contributors', label: 'Contributors' },
        { page: 'legal', label: 'Legal' },
    ]
};

function TopBar() {
    const [selectedPage, setSelectedPage] = useState('');

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
                    QaaS: Quality as a Service
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
                            </Space>
                        </a>
                    </Dropdown>
                ))}
            </div>
            <div className="right-section">
                {/* <input type="text" className="search-bar" placeholder="Search..." /> */}

                <Link to="https://docs.google.com/document/d/1_H7ySm_HwrwR5xhBd4amI-CWN_n6fKYcdVMHb6vDaF4/edit?usp=sharing" className="nav-link">Google Doc Link</Link>

            </div>

        </div>
    );
}

export default TopBar;
