import React from 'react';


export default function ManualInteractiveMode() {
    return (
        <div className="textPageContainer">
            <h1>C3. Manual Interactive Mode</h1>
            <p>
                In any case, QaaS may make general comments about the quality of the source or binary code that could improve quality through manual work.
                This means work for the user and may require specific types of expertise, so is not as generally useful as the QaaS Automatic mode.
                Thus, QaaS offers 3 possible forms of advice. Here much detail is exposed about a computation, including causally determined specific weaknesses in the source or binary code.
                Using heuristics that span multiple tools, we make observations that include limiting situations that may not be physically achievable.
            </p>
            <p>

                In other words, QaaS is capable of: simulating a computation, making extreme changes to a computation that help understand effects of the microarchitecture,
                the compiler, or the data sizes used. These functions use many tools including the well-established OneView Maqao toolset [refs],
                as well as traditional manufacturer’s tools [Intel, others], and HW counter-based tools [Cape].
                For compilation studies we use any available manufacturer’s compilers and open source compilers [GCC].
                We study various available RTLs [MKL, ROC, CUBlas] for math functions.
            </p>
        </div>
    );


}