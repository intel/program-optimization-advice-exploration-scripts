import React from 'react';
import CompareImage from '../imgs/compare.png';

export default function QaaSSearches() {
    return (
        <div className="textPageContainer">
            <h1>QaaS Searches</h1>


           
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

            <div className='imageContainer'>
                <img src={CompareImage} alt="Compare Image Description" />
            </div>
            <p>
                End Oct 4 Miniapps compiler Low level outline - pop back up.. Note we come down later for Apps
            </p>
        </div>
    );


}