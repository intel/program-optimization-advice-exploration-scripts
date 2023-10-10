import React from 'react';
import WinLoseImage from '../imgs/win_lose_compiler_compare.png';

export default function MultiCompilerGains() {
    return (
        <div className="textPageContainer">
            <h1>Multi-Compiler Gains</h1>

            <p>
                The counts of QaaS wins by use of a multi-compiler (Mcompiler [ref Aniket]) and flag search for wins vs. defaults can be compared for gain factors,
                see Table sept8. For gains of at least 2X, we see 7 cases among the 42 contests, or 17% of the time, assuming all choices are equally likely among a
                large set of developers. Similarly, 12/42 = 29% gain between 10% and 2X. The remaining 23 cases (&lt;10% gain) represent 55% of the cases.
                So we can conclude that in nearly half the cases using QaaS guarantees at least a 10% performance benefit on the ICL architecture.
                (YUE make 10% slider bar to try 9, 8, … , 5%, below which we can define noise or uninteresting results). Compiler developers may want to
                slide down to smaller gains to test flag choices. Bring in summary by each compiler and click down to table compare
            </p>





            <div className='imageContainer'>
                <img src={WinLoseImage} alt="WinLose Description" />
            </div>

            <p>
            QaaS seeks the best overall performance for each application, on each architecture,
             by searching through many plausibly best cases.  To see a detailed expansion of Table sept8, click down to level 3, otherwise please return to Level 1 for apps discussion.
            </p>

        </div>
    );


}