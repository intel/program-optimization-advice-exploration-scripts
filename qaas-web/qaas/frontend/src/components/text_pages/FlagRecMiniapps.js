import React from 'react';

import { Link } from 'react-router-dom';

export default function FlagRecMiniapps() {
    return (
        <div className="textPageContainer">
            <h1>Developer flag recommendations</h1>
            <h2>Miniapps</h2>
            <p>

                Only 2 of the miniapps had developer-generated compiler flag recommendations: MiniQMC and Kripke.
                Using M-compiler searches, QaaS found a 10% gain for MiniQMC, and a 2.5X gain for Kripke.
                This indicates that while developers try to help users, in some cases their advice is not up to date,
                or they may have used somewhat different HW versions, or HW settings.
                For example, after a few compiler releases, the recommendations may become stale.
                In this regard, QaaS will always be able to give advice that is fresh with respect to current
                compiler releases, as well as architecture variations.

                {' '}
                <Link className='link'
                    to="/qaas/overview/multiprocessor_comp_contents"
                > click back </Link>
                .
                to Compiler comparisons.


            </p>



        </div>
    );


}