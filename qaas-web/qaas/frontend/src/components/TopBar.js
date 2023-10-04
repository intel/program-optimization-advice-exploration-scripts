import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import './css/TopBar.css';

const pages = ['input', 'result', 'system_config', 'definitions', 'legal', 'catalog'];
const pages_labels = ['Job Submission', 'Results', 'System Configuration', "Definitions", 'Legal', 'Catalog'];

function TopBar() {
    const [selectedPage, setSelectedPage] = useState('');
    useEffect(() => {
        const handleHashChange = () => {
            const currentPage = window.location.hash.replace('#/', '').split('/')[0];
            setSelectedPage(currentPage);
        };

        // Initial setting
        handleHashChange();

        // Listen for hash changes
        window.addEventListener('hashchange', handleHashChange);

        // Cleanup
        return () => {
            window.removeEventListener('hashchange', handleHashChange);
        };
    }, []);
    const handleTabClick = (page) => {
        setSelectedPage(page);
    };
    return (
        <div className="top-bar">

            <div className="home">
                <Link onClick={() => handleTabClick("")} to="/" style={{ textDecoration: 'none', color: 'inherit' }}>
                    QaaS: Quality as a Service
                </Link>
            </div>
            <div className="nav-links">
                {pages.map((page, index) => (
                    <Link
                        to={`/${page}`}
                        key={page}
                        className={`nav-link ${page === selectedPage ? 'selected' : ''}`}
                        onClick={() => handleTabClick(page)}
                    >
                        {pages_labels[index]}
                    </Link>
                ))}
            </div>

            <div className="right-section">
                {/* <input type="text" className="search-bar" placeholder="Search..." /> */}
                <Link to="/login" className="nav-link">Log In</Link>
                <Link to="/signup" className="nav-link">Sign Up</Link>
                <a href="https://docs.google.com/document/d/1_H7ySm_HwrwR5xhBd4amI-CWN_n6fKYcdVMHb6vDaF4/edit?usp=sharing">Google doc link</a>

            </div>

        </div>
    );
}

export default TopBar;
