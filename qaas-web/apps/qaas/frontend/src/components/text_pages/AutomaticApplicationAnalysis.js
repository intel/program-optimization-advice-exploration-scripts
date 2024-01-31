import React from 'react';
import { Link } from 'react-router-dom';


export default function AutomaticApplicationAnalysis() {
    return (
        <div className="textPageContainer">
            <h1>C2. Automatic application analysis</h1>
            <p>
                The other half of the website contains more detailed information, and is provided on demand by users for their specific computations.
                For this, the same tools used for the encyclopedic comparative overviews, are used to dig deeply into quality issues for single computations,
                i.e., user-submitted jobs. This requires 2-way interactions in the form of a QaaS Menu and Results display.
            </p>
            <p>

                To submit a job, application developers must let QaaS know many details of their normal computational methods.
                These include their Golden HW architecture, compiler (and settings for each), MP settings, Data sets, etc.
                We then apply many changes to these, attempting to reproduce their runs and then perform many quality-improving variations.
                If QaaS automatically finds good gains, the user is satisfied because we report actionable results, so the user is guaranteed of the improvement potentials.
                If we find little, the user can be relatively happy to see that the computation is already high-quality, and little can be done to improve the situation.
            </p>

            <p>
                To submit a job,
                {' '}
                <Link className='link'
                    to="/input"
                > click here </Link>
                .
            </p>
        </div>
    );


}