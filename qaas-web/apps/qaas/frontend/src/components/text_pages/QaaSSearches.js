import React from 'react';
import CompilerComparisonHistogram from '../graph/histogram/CompilerComparisonHistogram'

import UnicorePerfGFlopsLineGraph from '../graph/line/UnicorePerfGFlopsLineGraph';
export default function QaaSSearches() {
    return (
        <div className="textPageContainer">
            <h1>QaaS Searches</h1>


            <p>Click down to level 3 somewhere</p>
            <p>
                The contest we are staging for each app compares the performance results for each potential compiler choice (3 currently) and its default flag settings,
                with all other compilers and their flag settings. For each compiler, we use a good default setting, together with 16 expert-chosen flag candidates.
                As default flags, we use the flags specified by the app developers for each compiler, or if none is specified, we use -03 march native as
                a generally-effective default for all compilers. Table compare shows the compiler-centric value of QaaS by comparing 2 pairs of results
                MORE paragraphs from pp 10-11. Sept 30 UX  for each compiler; the default chosen by experts, and the winner of the search done by QaaS.
                So with 2 results per compiler, and considering 3 compilers, we have 6 results per code. And for 7 miniapps, we have 42 cases total.
                Table compare shows 32 boxes because of two 3-way ties. Because these each represent 6 results, 32 – (two tie boxes) + (12 total tie cases) = 42 contest results, confirming the above count.


            </p>
            <p>
                Another way of thinking about this is that for each code, we have 3 default compiler comparisons, plus one QaaS best result. So we are examining 4 numbers pairwise,
                for a total of 4 choose 2, or 3 + 2 + 1 =  6 cases. Then, times 7 miniapps again yields 42 outcomes.

            </p>
            <p>
                To explain the value of QaaS, we must realize that two kinds of searches are being
                carried out: one is a Multi-compiler search using expert-chosen flags; here we use -O3 march native for all 3 compilers,
                but it’s user-selectable for the QaaS website. The other is a search among 16 generally effective flags per compiler.

            </p>
            <p>
                In addition, QaaS examines the default setting, for a total of 17 runs of each app for each compiler. Thus 17 runs * 3 compilers,
                for 7 apps here, totals 357 runs which requires relatively short jobs for fast turnaround. However, we have determined that
                optimal unicore compiler settings and single socket SMP runs usually require the same compilation choices. So, QaaS running times are done in parallel on single socket MP systems.

            </p>
            <p>
                Thus, there are a total of 3 compilers * 16 flags = 48 runs per code, which constitute one best QaaS result being considered in the previous paragraphs.

            </p>


            <p>For the full details about table compare, see level 3.</p>
            <p>
                End Oct 4 Miniapps compiler Low level outline - pop back up.. Note we come down later for Apps
            </p>
            <h2>
                QaaS overall performance benefit analysis

            </h2>
            <p>
                Table compare is a histogram that counts all wins by default runs, as shown in Table win-lose, as well as the details of QaaS wins.
                Each cell here contains the name of a code and 2 compilation runs x/y, which means that for this contest, option x led to better performance than option y.
                Its column then tells by how much it won the contest. The legend on the far right shows the color code for which compiler won or tied in each contest.
                So, in the second column (1.1 - 1.2X) we see that 5 contests led to small performance gains, and 2 were won by GCC, 3 by ICX. the top case listed in
                this range is miniqmc, for which ICX QaaS run beat the default ICX run. In the 1.5 - 2X column, we see that for miniqmc, ICX default beat GCC default.
            </p>

            <p>
                Consider the number of entries in Table compare.  For each code, we have 3 default compiler comparisons (all pairs),
                plus one QaaS best result. So we are examining 4 numbers pairwise, for a total of 4 choose 2, or 3 + 2 + 1 =  6 cases.
                Then, times 7 miniapps again yields 42 outcomes. The table has 32 cells marked, but HACC and AMG represent ties, so subtracting them,
                we have 5 miniapps X 6 cases = 30 cells.

            </p>

            <p>
                There is one more important consideration – the magnitude of the gains.
                If we consider the last 3 columns to examine all wins greater than 50%, we can see that ICC is a clear winner,
                with 5/10 cases. But if we drop the threshold to 20% wins, then ICC has 5/14 wins, but so does ICX. At 10% gains,
                ICC wins 5/19, GCC wins 6/14, and ICX wins 8/14 cases. Furthermore the following two figures show the effects of lowering
                the 1.1X bar to 3% gains (which in some cases is of interest). For that case, ICX dominates in wins for 8/19 cases.

            </p>


            <CompilerComparisonHistogram />
            <UnicorePerfGFlopsLineGraph />


            <p>
                For the full details about table compare, see level 3. In particular explain how counts of wins here and in Table sept8 differ.
            </p>


        </div>
    );


}