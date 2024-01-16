import React from 'react';
import '../css/navigation.css'
import LinkBox from './LinkBox';
export default function NavigationPage() {
    return (
        <div className="navigation-page-container">
            <h1 >Welcome to QaaS (Quality as a Service):</h1>
            <div>
                <LinkBox path={'/overview'} text={'See Past Analyses'} />
                <LinkBox path={'/input'} text={'Submit An Automatic Job'} />
                <LinkBox path={'/input'} text={'Submit An Manual Job'} />

            </div>

        </div>
    );


}