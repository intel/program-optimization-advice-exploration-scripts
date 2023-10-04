import React, { useEffect, useRef } from 'react';

export default function DefinitionsTab() {

    useEffect(() => {
        const handleScrollToHash = () => {
            const hash = window.location.hash.split('#').pop();
            const element = document.getElementById(hash);
            if (element) {
                element.scrollIntoView({ behavior: 'smooth' });
                element.style.backgroundColor = 'yellow';
            }
        };

        handleScrollToHash();

        window.addEventListener('hashchange', handleScrollToHash);

        return () => {
            window.removeEventListener('hashchange', handleScrollToHash);
        };

    }, []);

    return (
        <div className="textPageContainer">
            <p>
                PORTABILITY/AVAILABILITY/RELIABILITY/VARIABILITY/SENSITIVITY/STABILITY/etc…
                All of the notions listed above are very often used but often lack a precise/clear definition.
                The following aims to fill this gap and provide QaaS-implemented definitions.

            </p>
            <div>
                <h2>ACTORS</h2>
                <div className='container-next-to-paragraph'>
                    <p>sameple summary text here sameple summary text here sameple summary text here sameple summary text here.</p>
                </div>
                <p>The 4 main actors on the stage are independent variables:</p>
                <p>
                    <ul>
                        <li>Applications: this covers algorithms, mini apps, full apps and libraries. An application per se is not sufficient to make a run, a data set also has to be given.</li>
                        <li>Compilers: this does not cover only compiler but also flags used.</li>
                        <li>Parallel Runtime: this has a major impact on parallel runs. This includes the two common cases: OpenMP and MPI.</li>
                        <li>Hardware/low level runtime: this refers at the whole system (CPU, Memory) as well as some low level settings (OS, BIOS, frequency, etc,…).</li>
                        <li>For simplicity we will bundle together applications and data sets, and also compilers and parallel runtimes, leaving only 3 classes of actors to track. For each actor we will define attributes and methods to quantify the attributes. So, we are dealing with:</li>
                        <ul>
                            <li>Nap: Number of applications (Apps with different data sets will be counted separately).</li>
                            <li>Ncomp: Number of compilers used.</li>
                            <li>Nflags: Number of compiler flags used. For sake of simplicity, we will assume that across compliers, the same set of flags (or equivalent ones) will be used.</li>
                            <li>Nhard: Number of different hardware platforms. As for the other categories, the same hardware using two different memory systems (DDR5 versus HBM) will be considered as two distinct entities.</li>
                        </ul>
                        <li>All in all, following these definitions QaaS has a total of Nap x Ncomp x Nflags x Nhard basic experiments to be carried out (cartesian product of elementary parameter space). For reasonable coverage, this totals at least several hundred combinations and can escalate due to further parameters like # data sets, # cores used, etc.</li>
                    </ul>
                </p>

            </div>
            <div>
                <h2>Metrics</h2>
                <div>

                    <p>
                        Users want consistently high performance for their codes, which requires compilers that can match every app to each architecture of interest; the same can be said for other aspects of Computational Quality (CQ).
                        All the attributes we discuss are system-level aspects of CQ, but some are Level 1 issues, while others are properties of Level 1 (Level 2), or of the tools themselves (Level 3).
                    </p>
                    <p>Level 1: 		               Performance, Energy, System Cost (QaaS + user knowledge)</p>
                    <p>Level 2 – Level 1 properties:     Portability, Availability, Reliability, Sensitivity, Scalability, Efficiency</p>
                    <p>Level 3 - Tool properties: 	     Measurement Accuracy, Precision, and Stability</p>
                    <p>The top-level properties are not totally independent of one another; for example, top performance generally require more energy
                        (cost of operation) than lower performance. Similarly, portability to the very fastest machine may not be possible without an entire code rewrite,
                        e.g. to a GPU with a proprietary language/library and higher upfront cost (which we cannot include due to unknowable price negotiations). 3 …
                        Section x discusses performance variations across compilers and architectures; here we discuss the reasons for these variations.
                        First is the failure of compilers to generate code that runs at all (Reliability), and second is the variability of performance across
                        the code generated (Sensitivity). We choose these names because compile-time and run-time crashes can be counted in Reliability failure rates,
                        without much explanation of why failures occur (beyond compiler warnings and crash messages (e.g. segfault).
                        Performance variations within one compiler can be caused by Sensitivity to flags specifying particular transformations and instruction set generation
                        (which we can control), as well as cost models built into the compiler (whose decisions may be documented in compiler reports per code).
                        Portability, Availability, Reliability and Sensitivity are all defined and discussed in the system context of a set of applications, compilers,
                        compiler flags, runtime libraries, and hardware. Portability, reliability, and sensitivity are defined as continuous 0 to1 variables,
                        whereas availability is a binary 0 or 1 variable.
                    </p>
                </div>
            </div>
            <div id="portability" className="definition">
                <h2>A. Portability</h2>
                <p>
                    <div>Historically the term has been used to qualify applications capable of running on multiple systems,
                        with little importance given to the compiler and flags used. Traditionally,
                        the main intent of claiming that an application is portable,
                        has been to demonstrate that the application is capable of running on different hardware with an appropriate software environment.
                        Often, “portability” is coupled with “performance” as performance portability when seeking good performance on multiple HW systems.
                        We address this topic in several steps.</div>
                    <div>
                        <div>PORTABILITY DEFINITION:</div>
                        Portability is an attribute of an application. Full portability means that the application is satisfactorily running on any element of the context. Limited portability will indicate that the application is running on all hardware of the context but only for a limited for a limited set of compiler and compiler options.
                        In the case of limited portability, we can define the portability index as the ratio of number of “system configurations” (hardware, compiler, compiler options) for which the application runs satisfactorily divided by the total number of available configurations under study. If a computation fails to complete for any reason, it is not runnable. This assumes expert skills are
                        0 Portability index = # runnable system configs/ # systems available  1
                        available to set up and run each job.
                    </div>

                </p>
            </div>

            <div id="availability" className="definition">
                <h2>B. Availability</h2>
                <p>
                    <div>
                        Availability is a binary property [0 or 1] of technology; either a system and human are available to produce a given computation, or not.
                        Without technology availability, portability is impossible, so availability is necessary for portability.
                        It means that the technology designers claim it works, and someone has paid for access. Even if it is available, the technology may
                        produce poor quality results, e.g. poor performance.
                    </div>
                    <div>
                        For example, availability as a compiler attribute means that a specific compiler and its set of options for a given app can
                        be used to generate code compatible with target hardware.
                    </div>
                    QaaS has reportable availability options: NAtech, NA$, and NAQ, meaning,
                    respectively lack of availability due to technology, not purchased, or a QaaS failure.
                    Such classifications can be extended as needed.

                </p>
            </div>

            <div id="reliability" className="definition">
                <h2>C. Reliability</h2>
                <p>
                    <div>
                        Reliability is compiler or architecture attribute: A compiler will be declared as reliable over a context,
                        if all applications run satisfactorily with any context &lt;compiler, flag&gt; and &lt;hardware,flag&gt; pairings.
                    </div>
                    <div>Definition </div>
                    <div>
                        The Portability section discusses how successful each compiler is, across all apps; here we discuss the details of the failures. Failure rates, e.g. as in cases for which a compilation works or not, we can count specific failures over compilers, flag setting choices, apps or languages used, etc. It can be based simply on the total number of cases tried. Eq. rel defines Reliability.
                        Reliability = rel = 1 – failure count/tot. cases tried = 1 – failure rate			rel
                        where			0  failure rate  1, and 0  rel  1
                        Thus, if rel = 1 there are no failures and if rel = 0, every case fails.
                    </div>
                    <div>Similarly, as the portability index, we can define the reliability index as ratio of the number of configurations for which execution is correct over the total number of configurations within the context</div>
                    <div>

                    </div>
                    <div>Performance Sensitivity Definition</div>
                    Performance Sensitivity is defined in Eq. ps, where PS = 0 means there is no sensitivity, e.g. max time = min time. This can be applied to the compiler used, system used, library used, etc. in a computation.
                    Perf sensitivity = PS = (max value – min value)/ max value		 PS
                    0  PS  1
                </p>
            </div>

            <div id="sensitivity" className="definition">
                <h2>D.	Sensitivity to named factor F</h2>
                <p>

                    Sensitivity is a continuous [0 to 1] function of factor F, measuring how much a given metric (time, GFLOPS, energy) varies
                    over the whole set of system configurations. F can represent compiler flags, HW flags, etc.
                </p>
            </div>

            <div id="stability " className="definition">
                <h2>E.	STABILITY, Accuracy, and Precision </h2>
                <p>
                    <div>
                        Stability and accuracy are quality properties of the QaaS tools themselves, used to capture “differences” between multiple runs
                        of the same binary on the same hardware configuration. High Stability implies reproducibility of measurements from run to run.
                        Explain Accuracy implies that the numbers obtained from our tools truly represent facts about inside the running computation.
                        Accuracy is not possible for small numbers, e.g. a short running program, or too few samples. Both give us confidence in the numbers measured.
                        If we cannot obtain accurate, stable numbers QaaS cannot vouch for the quality of a computation – good or bad.
                    </div>
                    <div>
                        Precision denotes the number of bits to which a computation represents reality. Input precision can be affected my measurement errors and output precision can
                        be eroded by floating-point roundoff errors. Verificarlo is an example of an effective floating-point precision tool (QaaS plans to offer in future).
                    </div>

                    <div>STABILITY DEFINITION</div>
                    <div>
                        For a given portion of code (whole application, function or loop), the stability will capture the differences between multiple executions (instances).
                        Typically, stability will be associated with a metric (time, page faults, etc…) and will be quantified by
                        Stability = (Median value – Minimum value)/Minimum value
                        Stability differs from sensitivity because we cannot pin a stability variation to a specific cause for measurements varying,
                        whereas sensitivity is defined with respect to factor F.

                    </div>


                </p>
            </div>

            <div>
                <h2>Summary </h2>
                <p>
                    Using these definitions, we can separate all the quality issues that may arise inherently,
                    plus the human/external issues of getting the truth out of a system. It clarifies how messy this topic is,
                    and how concerned a user should be that he is not getting misled.
                    It forces us to be pedantic and sometimes we really can’t go into all the details at a high level.
                    We need to say that these nbrs are taken as stable and we aren’t going to say more about it – usual case.
                    In the depths of OV, it is used to good advantage. So we don’t want to lose that.

                </p>


            </div>

        </div>
    );
}
