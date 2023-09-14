import React from 'react';

import comparisonsGainsImage from '../imgs/10year_comparisons_gains_across_contests.png';

export default function Quality10YearTrendRealities() {
    return (
        <div className="textPageContainer">
            <h1>Quality 10-year trend realities</h1>
            <p>

                What performance gains have been achieved historically with different types of independent variables? What really improves performance the most for a given app?
                How does performance in general improve across apps? Consider 3 long running public displays of related ideas: the SPEC benchmarks, Top 500 HPC systems,
                and the Bell HPC award. Each uses different rules, allowing us to make some interesting comparisons, as in Table bmkvar. Fix: approximate values only.
            </p>
            <div className='imageContainer'>
                <img src={comparisonsGainsImage} alt="comparisonsGainsImage" />
            </div>
            <p>

                It is easy to see that constraints in contest rules constrain annualized gains. For relatively narrow rules, neither SPEC or Top 500 gets above 20% gains per year,
                while the wide-open Bell rules allow anything, including picking a new problem/algorithm and data size to fit a given new machine.
                When all constraints are dropped, gains jump from 15-20% to the unconstrained situation, 2X annual gains are possible.
            </p>

            <p>
                QaaS miniapp runs use 7 (expanding) apps with similar diversity to SPEC, and probably lower diversity than Bell.
                Thus, the QaaS Demo gains of over 2X for compiler and arch flags are quite impressive. QaaS achieves this by using several top compilers and expert-chosen flag
                options on new compilers. Note that SPEC is limited to unicore, while our MP variation is over shared memory sizes (up to 2 sockets, 100+ cores),
                so more limited than Top 500. However, compiler gains are relatively equivalent on uni and MP systems. We use apps whose age varies, up to 10 years perhaps,
                but perhaps are more aggressive with flags and compiler choices than allowed by SPEC rules. Need to refine discussion – look at rules for spec and top 500.
            </p>

            <p>
                In Table bmkvar, we see that when the algorithm is fixed, gains are much more constrained than when the app chosen is open ended – Bell is the most liberal set of rules.
                SPEC is the most constrained and Fig. spec  shows the contributions of each SPEC benchmark to the 3.25X decade-long total performance gain. These ranged from &lt;2x to &gt;20x,
                so there is gains depend dramatically on the algorithms involved.

            </p>

            <p>
                It is very difficult to separate the gains due to architectural change and compiler change,
                because each new system comes with a compiler tuned to that system. However, QaaS is able to distinguish compiler gains from HW/arch gains,
                by holding the HW/arch fixed and varying compilers at a moment in time. Figs. histw and defC show that among 3 compilers, over 7 codes,
                there are ~3 compiler ties, but wins for one or another compiler by &lt;2x in 3 cases. So up to half of the gains across these miniapps is due entirely to compiler gains
                (i.e. the HW/arch is invariant).  Fig. histw shows that the apps and compilers vary for modest and big wins.
                This indicates that a developer never can assume much about where gain will arise for any given app.
            </p>

            <p>
                MP results depend substantially in keeping up with the latest architectural changes.
                Fig. MP shows a 10^6 Bell gain over 30 years, or 100X in 10 years. Note that there are approximately 7 plateaus of a few years in Fig.
                MP, which  imply a given system that reigned for a few years in the Bell competition.
            </p>
        </div>
    );


}