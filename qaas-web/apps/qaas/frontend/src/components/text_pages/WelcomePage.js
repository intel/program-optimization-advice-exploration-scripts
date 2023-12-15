import React from 'react';
export default function WelcomePage() {
    return (
        <div className="textPageContainer">
            <h1 >Welcome to QaaS (Quality as a Service):</h1>
            <h2>Why computational quality services are important  this is good for the opening = covers all 3 : intro, automatic jobs,manual OV work. </h2>

            <p>
                A. QaaS importance and introduction.  Oct. 7, 2023

            </p>
            <p>
                The necessity of computation in science and engineering a few decades ago has extended across finance, entertainment, medicine, sports,
                robotics and supply-chain management has extended to “everything” via AI, which was once a label for anything thought to be too hard for
                computers to do. While computing was originally entirely numerically quantitative, it has become mostly qualitative in value for the
                public consumption of computation. This process is covered in three steps: technology production, provision, and consumption.
            </p>
            <p>
                While the quality of computation may have once seemed mostly a side issue, it is now an important subject. Because so many aspects of life depend on computation,
                its quality factors – speed, cost, correctness, and reliability – are essential now. The complexity of these factors and their interaction makes the topic overwhelming, unless computers themselves
                are employed to ensure high-quality results. QaaS automation of computational quality improvement takes several steps in that direction by providing an online service.
            </p>
            <p>
                To follow the above naming conventions would be to call QaaS a “computational, computational-quality” tool; to avoid syntactic ugliness,
                we use the name computational quality automation (CQA [overused?]or ACQ= automated CQ?: call it CompQual or Qually?? Koala??).
                Just as solving problems from the list above, like quark confinement, arbitrage trading, movie animation, treatments for disease diagnoses,
                winning the World Series, getting subassemblies together and assembling a car, or recognizing family photos and writing captions,
                CQA is a collection of algorithms that replace the intuition of application developers, system and compiler designers, and performance engineers.

            </p>
            <p>
                Successful computer use in the process of solving hard problems in any area is open ended.
                There will always be room to modify algorithms and add new ones to an effective collection of techniques.
                In all attempts to solve real-world problems, the computational results only approximate optimal solutions (whose definition may not even be easy to formulate).
                This first version of QaaS delivers CQA methods in an automated, on-line manner, that attempts via menus to allow various types of users to exploit the assembled tools.
                QaaS provides good solutions and has the self-awareness to know when it is missing required information or skills, so it may end up making suggestions to users for further manual work.

            </p>
            <p>
                This introduction explains QaaS by showing various examples of its effectiveness on some simple codes. We also discuss tradeoffs that may be of more or less interest
                and importance to each constituency in the 3 computational community steps listed above. When QaaS fails to mitigate seemingly anomalous situations,
                it offers (continuously improving) explanations of where the underlying mismatches lie. These may be in algorithms, languages, libraries, architectures, or settings and options chosen for their use.
            </p>
            <p>
                Yue paste 1/
            </p>
            <p>
                This first version of QaaS delivers CQA methods in an automated, on-line manner, that attempts via menus to allow various types of users to exploit the assembled tools – MultiView.
                As in all attempts to solve hard problems, the computational results only approximate optimal solutions (whose definition may not even be easy to formulate). QaaS provides good solutions and has the self-awareness to know when it is missing required skills, so it may end up with suggestions to users for further manual work per application via OneView.
            </p>
            <p>
                Yue paste 2.
            </p>
            <h2>Roadmap Oct 10</h2>
            <h2>1.      Introduction</h2>
            <p>
                This website explains computational quality by decomposing its complexity into a hierarchy of interrelated text and graphics.
                The left sidebar is a Table of Contents with a multi-level hierarchy spanning QaaS topics. The top bar consists of meta-statements about the contents,
                allowing users to navigate according to their current interests. It has two main divisions: topics about QaaS including its main funtions,
                contributors (by organization), legal, etc., and QaaS content explanations including references, definitions, figure directory, etc.
            </p>
            <p>Each is clickable to other sections and back.</p>
            <p>The content hierarchy expands the Table of Contents to 4 levels:</p>
            <p>
                <strong>Level 1</strong> allows people of many backgrounds to skim the technical material to gain easy, summary understanding of each topic.
                Just as news stories keep people  generally informed, Level 1 informs but does not give much explanation.

            </p>
            <p>
                <strong>Level 2</strong> explains the how and why of Level 1, skipping the complex details, which to some readers are essential.
                This includes more detailed discussions, with figures and tables giving more data to explain Level 1.

            </p>
            <p>
                <strong>Level 3</strong> gives necessary background information to clarify the details about the higher-level discussions and conclusions.
                The idea is to allow experts to be clear about the data, reasoning, and assumptions built into QaaS analyses.
            </p>
            <p>
                <strong>Level 4</strong> is a database documenting all the details of run made. This is restricted to use by QaaS developers,
                but it provides the ability to validate the system runs. QaaS also provides for proprietary use of particular databases.
            </p>
            <h2>2.      Navigating the website</h2>
            <p>
                [WORK ON All QaaS developers need to contribute ideas here, suggesting what naïve and expert users – developers of apps, compilers, and architectures might want to do with ManyView
                – also when to switch to OneView for the deepest analyses of each app.]
            </p>
            <h2>3.      Overview of Contents</h2>
            <p>
                The primary subjects covered in the Table of Contents are the contributions to quality of compilation, the range of uniprocessor to MP or GPU architectural issues,
                HW/SW performance scaling, and energy consumption. The cost of purchase is included indirectly, by allowing users to enter cost estimates to allow the tool to make comparative tradeoffs.
            </p>
            <p>
                <strong>Compilation </strong>(Section x) includes the choice of compiler by manufacturer (e.g. Intel ICX, Gnu GCC, AMD AOCC??, ARM clang, LLVM clang)
                and then the flags used per system. These control the transformation of input code (via a cost model) as well as the selection of an instruction set
                (e.g. vector length) for code generation. How these choices are made per app and system can have major performance effects, but choices may be
                constrained in practice, leading to quality tradeoffs. So the conclusions are not always straightforward.

            </p>
            <p>
                <strong>Architecture  </strong> (Section Y) choices are basic determiners of quality offering diverse paths. General vs.
                special purpose system choices arose in the 1960s with the IBM 360 family and stirrings of supercomputing, followed by accelerators and minicomputers in the 1970s.
                Cost, programming difficulties, and application appropriateness all arose quickly to complicate the industry. These differentiators continue among various kinds of
                uniprocessors used in MP (multiprocessor) systems, e.g. X86, ARM, and on to combinations with GPUs – Nvidia, AMD, Intel, etc. Even restricting our attention to HPC-like computing,
                application-driven frenzies continue to churn the industry from games to AI. QaaS provides deep analyses of application,
                compiler, and architectural tradeoffs for MPU systems, and extends to GPUs by comparing common functionalities.

            </p>
            <p>
                <strong>Scalability   </strong>(Section xx) is an extension of architecture to MP and GPU performance for various types of application SW and data sizes. For example,
                MP systems are sensitive to efficiency vs. number of processors, which in turn depends on SW scheduling algorithms and pinning apps to the architecture.
                Replication factors for code and data define throughput and parallel computation models. These entail several tradeoffs, which QaaS defines and analyzes.

            </p>
            <p>
                <strong>Energy    </strong>consumed (Section E) is a function of the HW and SW architectures and per-run settings. For example, both speed and heating increase as clock speed increases.
                Also, energy consumption raises operating cost.  Tradeoffs vary across these factors, as well as the instruction set used (vector lengths compiled).
                And, course performance generally increases with $ spent, but QaaS analyses, together with user-provided $ estimates allows one to examine many tradeoffs.
                Costs are impossible for QaaS to automate because of long-standing price flexibilities, recently extending to supply-driven pricing.


            </p>
            <h2>New number level</h2>
            <h2>Users submit codes – QaaS returns results; nothing further is required of users.</h2>
            <p>Welcome to the QaaS Computational Quality (CQ) overview. The website focuses on comparing CQ results across computer systems and application areas,
                both current and over the past ten years. Our first goal is to allow users to understand both the state of the art in HPC, as well as recent progress trends.
                Our major goals are to provide automatic analyses and improvement of developer submitted apps, followed by manual interactive advice.</p>





        </div>
    );


}
