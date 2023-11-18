import React from 'react';
import { Link } from 'react-router-dom';
import IntroLink from './IntroLink';
export default function OverViewQaaS() {
    return (
        <div className="textPageContainer">
            <h1>Overview of QaaS: Summaries of past runs   </h1>
            <p>
                This section uses key views of performance results to orient new QaaS users.
                For a philosophical background of our approach,
                {' '}
                <Link className='link'
                    to="/qaas/overview/perf_improve"
                > click here </Link>
                .

                To proceed with the discussion of QaaS typical results,
                please continue. As examples, QaaS can search across architectures and compilers to find the best performance
                results per code, and we present unicore, compiler and multicore comparisons.


            </p>



            <h2>Unicore performance comparisons</h2>
            <p>
                For an introductory unicore discussion
                {' '}
                <Link className='link'
                    to="/qaas/overview/unicore_perf_contents"
                > click here </Link>
                .

                This is also an introduction to the QaaS service of Section 2 (Automatic Application Improvement).
            </p>

            <h2>Compiler Comparison</h2>
            <p>
                Most computers have multiple processors/cores today, and applications can take advantage of them in various ways.
                Compilers play larger roles as computations become more complex, so we continue the discussion on these topics
                {' '}
                <Link className='link'
                    to="/qaas/overview/multiprocessor_comp_contents"
                > click here </Link>
                .
            </p>

            <h2>
                Multicore performance comparisons
            </h2>

            <p>
                For an introductory multicore system comparison,
                {' '}
                <Link className='link'
                    to="/qaas/overview/multiprocessor_perf_contents"
                > click here </Link>
                .
                This extends the unicore introduction above, and introduces some basic multicore metrics.
            </p>
            <h2>
                Summary points
            </h2>


            <p>
                Above, we have covered unicore and MP architectural basics, as well as compilation basics. We used only a few simple miniapplications.
                The BQI will expand on many of these topics and include whole applications, as well as more systems. Here we have shown only some factual
                statements about these computations, but have not given many details about the codes, how QaaS works, or why it can be regarded as a reliable tool.
            </p>

            <p>
                Our orientation is to find performance improvements and show users how to take advantage of our findings. We view as less important
                a detailed explanation of why we come to certain conclusions. The main reason for this is that because QaaS contains many tools,
                explanations can become intricate. However, in BQI, we do cover some explanations.
            </p>
            <IntroLink />



        </div>
    );


}