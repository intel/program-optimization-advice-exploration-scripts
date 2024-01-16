import React from 'react';

import { Link } from 'react-router-dom';

export default function FlagRecMiniapps() {
    return (
        <div className="textPageContainer">
            <h1>Developer flag recommendations</h1>
            <h2>Miniapps</h2>
            <p>

                QaaS attemps to improve on the best performance settings suggested by applicaiton developers. Only two of the miniapps had compiler flags recommended by developers: MiniQMC and Kripke.
                Using multi-compiler searches, QaaS found a modest 10% gain for MiniQMC, but a major 2.5X gain for Kripke.
                This indicates that while developers try to help users, in some cases their advice may not be up to date, or the developers may have used somewhat different system configuations or hardware/software settings.
                For example, after a few compiler releases, the recommendations may become stale.
                In this regard, QaaS will always be able to give advice that is fresh with respect to current
                compiler releases, as well as architecture variations.

                {' '}
                <Link className='link'
                    to="/qaas/overview/compiler_comparison"
                >Click back</Link>{' '}
                to Compiler comparisons.


            </p>



        </div>
    );


}