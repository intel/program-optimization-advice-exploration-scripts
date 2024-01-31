import React from 'react';

import bestcompImage2 from '../imgs/bestcomp2.png';

export default function Apps() {
    return (
        <div className="textPageContainer">
            <h1>C1.1.2 Applications</h1>
            <p>
                Here we show Gromacs, QMCpack, Trex Champ and Turbo RVB,  etc. Kevin is building QMCkl version for Cmake – to Hafid.
                Also be ready for duplicated tables for SPR, and then compare ICL with SPR side by side.Sept 13
                Table apptop shows …
            </p>
            <p>
                Because most of these codes are produced by developers skilled in performance tuning for reuse by others,
                many are set up with different compiler-specific flags per architecture. So, we set the QaaS gain thresholds
                lower than for miniapps. Here we use 5 quintiles: 0 –  &lt;2.5% (which can be regarded as a tie), 2.5 –
                &lt;5%, 5-  &lt;7.5%, 7.5 to  &lt; 10%, and  &gt; 10%, which we expect to be rare. This is in contrast to
                gains as high as over 4X for miniapps, which represent average codes developed mostly for functionality,
                and less for performance. This shows another face of the QaaS benefits, even for top developers who need
                QaaS automation for continuous development/release testing over many systems.

            </p>
            <div className='imageContainer'>
                <img src={bestcompImage2} alt="BestComp Description" />
            </div>

        </div>
    );


}