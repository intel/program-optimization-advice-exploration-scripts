import React from 'react';
import WinLoseImage from '../imgs/win_lose_compiler_compare.png';
import CompareImage from '../imgs/compare.png';

export default function CompilerDetails() {
    return (
        <div className="textPageContainer">
            <h1>C1.1.1.A Compiler Details</h1>
            <p>
                Thus, QaaS saves application developers from deciding which compiler and which flags are best, and we frame the above contest as one between an expert,
                but lazy developer who uses just one default flag on all 3 compilers for miniapps
                (we will change this for whole apps). So Table compare can be viewed in several ways:
            </p>
            <p>
                <ul>
                    <li>
                        The counts of QaaS wins by Mcompiler and flag search for wins vs. defaults can be compared for gain factors,
                        see Table sept8. For gains of at least 2X, we see 7 cases among the 42 contests, or 17% of the time,
                        assuming all choices are equally likely among a large set of developers. Similarly, 12/42 = 29% gain between 10% and 2X. The remaining 23 cases
                        (&lt;10% gain) represent 55% of the cases. So we can conclude that in nearly half the cases using QaaS guarantees at
                        least a 10% performance benefit on the ICL architecture. (make 10% slider bar to try 9, 8, … , 5%,
                        below which we can define noise or uninteresting results). Compiler developers may want to slide down
                        to smaller gains to test flag choices.  Bring in summary by each compiler and click down to table compare
                    </li>

                </ul>
            </p>

            <div className='imageContainer'>
                <img src={WinLoseImage} alt="WinLose Description" />
            </div>
            <p>
                QaaS seeks the best overall performance for each application, on each architecture, by searching through many plausibly best cases.
            </p>
            <p>
                The contest we are staging for each app compares the performance results for each potential compiler choice (3 currently)
                and its default flag settings, with all other compilers and their flag settings.
            </p>
            <p>
                For each compiler, we use a good default setting, together with 16 expert-chosen
            </p>
            <p>
                16 flag candidates (the same set here for all compilers). As default flags,
                we use the flags specified by the app developers for each compiler,
                or if none is specified, we use -03 march native as a generally- effective default.
            </p>
            <p>
                Table compare shows the compiler-centric value of QaaS by comparing 2 pairs of results
            </p>
            <div className='imageContainer'>
                <img src={CompareImage} alt="Compare Image Description" />
            </div>
        </div>
    );


}