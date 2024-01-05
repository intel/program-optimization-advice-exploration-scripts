import React from 'react';
import { Link } from 'react-router-dom';
import QaaSValueImage from '../imgs/qaas_value.png';

export default function OverViewQaaS() {
    return (
        <div className="textPageContainer">
            <h1>Overview of QaaS: Summaries of past runs   </h1>
            <p>
                This section uses key views of performance results to orient new QaaS users.

                See {' '}
                <Link className='link'
                    to="/qaas/overview/perf_improve"
                > philosophical background </Link>

                else proceed with the discussion of QaaS typical results. As examples, QaaS can search across architectures and compilers to find the best performance
                results per code, and we present unicore, compiler and multicore comparisons.


            </p>




            <h2>Unicore performance comparisons</h2>
            <p>
                We begin with

                <Link className='link'
                    to="/qaas/overview/unicore_perf_contents"
                >  introductory unicore results</Link>,
                because they reveal many basic ideas that can be useful in understanding HPC multicore
                results on the fastest parallel machines available. This is also an introduction to the QaaS service of Section 2
                (Automatic Application Improvement).

            </p>

            <h2>Compiler Comparison</h2>
            <p>
                Most computers have multiple processors/cores today, and applications can take advantage of them in various ways.
                {' '}
                <Link className='link'
                    to="/qaas/overview/multiprocessor_comp_contents"
                >Compilers</Link>
                {' '}
                play larger roles as computations become more complex, so we continue the discussion of these topics here.
            </p>

            <h2>
                Multicore performance comparisons
            </h2>

            <p>
                This extends the unicore introduction above, and introduces some
                <Link className='link'
                    to="/qaas/overview/multiprocessor_perf_contents"
                > introductory multicore system comparison metrics.</Link>
            </p>

            <h2>
                Application Portability
            </h2>
            <p>
                Porting an application involves sets of architectures, compilers and runtime libraries.
                The causes of portability failure across architectures may be weak compilers or runtime libraries,
                but detecting failure and clarifying its details can be extremely elusive. In its most vicious form,
                poor portability can be confused with poor performance and go undetected. Poor performance, however,
                can be quantified and measured in various terms, so in practice, performance must be the starting point.
            </p>


            <p>
                The combination “performance portability” is a topic promoted by the DOE and other government agencies, but the Wikipedia article states correctly upfront that “there is no universal or agreed upon way to measure it.
                ” It is a qualitative topic, best avoided in favor of two separate quantitative discussions: defining high relative performance on any machine, and then dealing with code porting and performance per system.
            </p>

            <p>
                Thus, QaaS focuses on each topic separately, quantifying and measuring portability in several ways per system:
            </p>
            <ol>
                <li>Compiling executable code</li>
                <li>Executing the code “successfully,” i.e without a crash.</li>
                <li>Obtaining “correct” results – several definitions of correctness may be acceptable. </li>
                <li>Obtaining relatively high performance. </li>

            </ol>
            <p>
                High performance execution depends on the programmer having chosen and correctly used high-quality runtime libraries – for application-specific algorithms,
                to support parallelism of various types, etc.
            </p>

            <p>
                Runtime libraries can defeat portability on step 2. above – for example the interaction of MPI libraries with applications and architectures.
                QaaS experience shows that Intel MPI is the most portable, whereas MPICH, OpenMPI, and others can be much more difficult to port.
                See examples in text. Ironically, the DOE promotes “performance portability” but confounds portability by supporting the development of several conflicting dialects,
                instead of standardizing MPI.
            </p>
            <p>
                Similarly, step 1 requires a high-quality compiler, per architecture. QaaS has found that there are no universally highest-quality compilers for
                any machine tested – multi-compilation and result comparison is always required for best results, as discussed in the
                {' '}
                <Link className='link'
                    to="/qaas/overview/multiprocessor_comp_contents"
                >compilation section</Link>
                .
            </p>

            <h2>
                QaaS added value
            </h2>

            <p>
                By making comparative runs, QaaS can be very effective in analyzing portability. Each of the 4 steps outlined above can be dealt with separately in QaaS. Thus, it can help pin down portability issues in detail.
            </p>

            <div className='imageContainer'>
                <img src={QaaSValueImage} alt="QaaSValueImage Description" />
            </div>
            <h2>
                Next steps
            </h2>


            <p>
                Above, we have covered unicore and MP architectural basics, as well as compilation basics. We used a few simple mini-applications to show
                some factual statements about these computations. We have not given many details about the codes, how QaaS works,
                or why it can be regarded as a reliable tool.

                <div className='container-next-to-paragraph'>
                    <p>If QaaS judges a computation as high-quality, it is. <br />
                        → Believe it and move on. </p>
                </div>
                The QaaS goal is to find performance improvements automatically,
                and show users how to take advantage of our findings. At a high level, results are more important than detailed explanations.
                Furthermore, because QaaS contains many tools, explanations can become intricate.
            </p>

            <p>
                This brief introduction to QaaS has covered many topics that are expanded to fuller explanations in the Broad QaaS Introduction [BQI].
                If your main interest is in submitting your own job to run, you may proceed to Section 2
                <Link className='link'
                    to="/input"
                > click job submission</Link>
                .

                <Link className='link'
                    to="/qaas/cq_overview"
                >   Broad QaaS Introduction </Link>
                {' '}
                should serve as a reference document to further questions that may arise about QaaS analyses, as you proceed.
                Otherwise for a continuation of the QaaS discussion, BQI will expand on many of the topics and include whole applications,
                more systems, and some performance explanations.

            </p>











        </div>
    );


}