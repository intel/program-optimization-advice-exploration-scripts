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


            <p>
                Oct. 17 QaaS seeks the best overall performance for each application, on each architecture, by searching through many plausibly-best cases.
                These include default flags and alternative QaaS flags. Table win-lose is default centric, while Table compare extends the focus to include all QaaS options.
                In Table win-lose, each compiler i has a default flag performance result, and another result obtained by QaaS (in testing a number of good options for compiler i).
                Thus, for each default setting for compiler i, there are 3 comparison contests, one with each of the other 2 compiler default settings,
                and one with the QaaS result for compiler i itself. Table win-lose shows 7 apps, so there are 21 total contests.
            </p>

            <h2>
                Compiler default-flag analysis
            </h2>

            <p>
                Table win-lose has a row for each compiler being considered and columns for wins and 2-way ties, one for 3-way ties, and one for losses and tied losses.
                The number of cases for each is listed, along with the number of big wins (defined as 2X or more), and the % of all cases. Note that each row sums to 21,
                representing the 21 contests described above. From this we can conclude that relative to default choices for compilers for this set of codes
                and ICL architecture,, ICC is the best compiler. In other words, if a compiler contest included developers choosing compilers at random,
                each with a given default, the best outcome for all developers would arise from ICC use. 62% of the time ICC would lead to a tie or best performance,
                with 38% losses to other compilers. The details of QaaS search wins are ignored here, but discussed below (see Table compare)

            </p>

            <p>
                The net of this allows a CSP or other provider of services to conclude that ICC is a good universal choice for this very limited set of miniapps because
                it wins more than the others and loses less. The total population of clients would generally benefit maximally, unless of course they already know which
                compiler they need. Note that QaaS provides the above as an automatic procedure for CSPs and the results could be shared with users to underpin the choices
                of compilers offered.
            </p>

            {/* <p>
            all the contests QaaS automates. Ties represent 3-way ties in which no compiler exceeds another by &gt; 10%. But 2-way ties and clear wins are shown on the right, where a big win refers to a gain &gt; 2X over the default. Similarly the loss column represents cases where each compiler produces clear losses or tied losses. 
            </p> */}





            <div className='imageContainer'>
                <img src={WinLoseImage} alt="WinLose Description" />
            </div>

            <p>
                To see a detailed expansion of Table win, click down to level 3, otherwise please return to Level 1 for apps discussion.
            </p>

        </div>
    );


}