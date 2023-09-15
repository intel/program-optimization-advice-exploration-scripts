import React from 'react';
import { Link } from 'react-router-dom';
import './css/TopBar.css';

const pages = ['input', 'result', 'system_config'];
const pages_labels = ['Job Submission', 'Result', 'System Configuration'];

function TopBar() {
    return (
        <div className="top-bar">

            <div className="home">
                <Link to="/" style={{ textDecoration: 'none', color: 'inherit' }}>
                    QaaS: Quality as a Service
                </Link>
            </div>
            <div className="nav-links">
                {pages.map((page, index) => (
                    <Link to={`/${page}`} key={page} className="nav-link">
                        {pages_labels[index]}
                    </Link>
                ))}
            </div>

            <div className="right-section">
                <input type="text" className="search-bar" placeholder="Search..." />
                <Link to="/login" className="nav-link">Log In</Link>
                <Link to="/signup" className="nav-link">Sign Up</Link>
            </div>

        </div>
    );
}

export default TopBar;
