import React from 'react';

import MPminiappPerfVarTable from '../graph/table/MPminiappPerfVarTable';
import { Link } from 'react-router-dom';
import { useHighlightNavigation } from '../hooks/useHighlightNavigation';
export default function CQOverview() {
    useHighlightNavigation();

    return (
        <div className="textPageContainer">
            <h1>Computational Quality Overview [Broad QaaS Introduction]</h1>
            <p>
                This initial QaaS implementation illustrates the recent history (&lt; 10 years) of important but limited parts of the entire Computational Quality (CQ) picture.
                We believe it covers enough to show the value of the approach, serving as a continuously updated encyclopedia of the factors contributing
                to CQ, their relative magnitudes and their variations. It will continue to expand in response to user interest.
            </p>
            <p>
                As outlined in

                {' '}<Link className='footnote-link'
                    to="/qaas/constraints_and_scope"
                >Constraints and Scope</Link>,{' '}
                we expose quality problems of specific compilers, architectures,
                multiprocessor performance and across a broad set of system types. The results are illustrated using
                various kinds of application SW examples: numerical libraries, HPC-type benchmarks, mini-applications,
                and whole applications. Wherever practical, we use multiple data sets to expose quality variations.
            </p>
            <p>

                QaaS has the ability to answer many subtle variations of simple quality questions by consulting its extensive database of measurements and analyses.
                On the topic of how to achieve “best performance,” QaaS can deal with various nuances. If one seeks the very best time for one application on one or more systems,
                a clear answer is easy. But there are many nuanced variations on this:
            </p>
            <p>
                <ul>
                    <li>Is time really the <em>preferred</em> or <em>only</em> performance metric; domain-specific rates (e.g. Gf) or application figure of merit (FOM) may give alternative answers.</li>
                    <li>If there are is a suite of several apps in question, then is the question about which system = &lt; compiler, arch&gt;
                        combination is best for each app, or instead, which compiler/system gets the most wins (or definitive wins), across the whole application suite.
                    </li>
                    <li>If one plans to use the best compiler/system for a set of apps, is maximizing top perf the question, or really avoiding perf losses (or big losses).</li>
                    <li>In all such inquiries, wins or losses may be best stated with some fuzziness. The real question may be about finding "pretty good” systems, by including
                        narrow losses in the process of counting, to determine the most robust systems.</li>
                </ul>

                Even for our current set of just a dozen codes, a great deal of variety arises, a great deal of rises showing the relevence of these questions. <span className='check-color'>Fig. 1</span> otherdoc shows absolute performance,
                while <span className='check-color'>Fig. 2</span> appgain shows winning compiler statistics. <span className='check-color'>Table sept8</span> opens the door to considering second best but "pretty good" solutions; note that ICC looks weak when avoiding losses becomes a focus. Tablecompare shows an overall comparison of these questions.

                Table port? Here or port section.. also points out that beyond performance:
                <ul>
                    <li>
                        Overall-quality must consider <em>portability</em> and <em>cost</em>, together with performance. For example, on ARM systems, compilation or execution may fail on the apps we have studied
                        (a rare experience on Intel compilers),
                        which in some situations is disastrous. As another example, the closed ecosystem of Nvidia also prevents portability to or from what are often winning performance
                        numbers, but on very expensive HW.
                    </li>

                </ul>
            </p>

            <h2>Ice Lake Multicore Performance Details</h2>
            <p>
                Ever-present questions in parallel computing concern scalability: how well-matched is a code to a multicore architecture
                and what performance levels proceed from this?
                {' '} <Link className='link'
                    to="/qaas/cq_overview#figparvar"
                >Fig. parvar</Link> {' '}

                shows these latter relevant characteristics for the 7 miniapps
                running on ICL. The compilers used are documented in Fig. bestcomp (see compiler section). Considering the number of cores
                leads to a 4th type of QaaS graphs for scalability.
            </p>
            <MPminiappPerfVarTable />

            <p>
                The scalability of codes has two points of focus: the number of processors used effectively, and scaling type in terms of code & data replication factors.
                Fig. parvar shows that excellent scalability can result from diverse SW approaches: MiniQMC and its data are replicated 32 times, while HACC executes 48 OpenMP
                threads simultaneously on one data set, and yet both achieve high Gf rates (12.8 and 16.6 Gf/core, respectively).
                Note that the best affinities for these two codes also differ substantially.
                Lower Gf results are achieved for the other 5 miniapps, using various kinds of SW scaling and HW configurations.
            </p>

            <p>
                Throughout this discussion we show results that maintain parallel efficiency above .5. This is intuitively desirable,
                but individual machine users may have more or less aggressive attitudes. Some may prefer satisfying an efficiency-knee
                criterion that considers HW cost, below which efficiency falls sharply. Others with more concern about raw speed than
                about cost will prefer to focus on a speedup knee, above which performance gains drop sharply with core increase.
                In the following we will introduce two types of scalability graphs that represent these ideas.
            </p>
            <p>
                Finally, total operating cost includes energy, and we will discuss several tradeoffs between performance and energy.
                Again, slopes and knees dominate the discussion. No one wants to minimize energy (by turning off the machine),
                but everyone has some form of constrained optimization in mind - minimal energy subject to pretty good performance
                (which includes many personal views of “good”). We will see that clock frequency, instruction set used (vector length),
                and number of cores used interact to influence several metrics that include time, rate and energy.
            </p>
            <p>
                Note to reader: this ends the current demo. We will soon add compiler details and portability detials at this level.
            </p>



        </div>
    );


}