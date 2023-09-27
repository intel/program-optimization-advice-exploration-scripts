import React, { useState, useEffect } from 'react';
import axios from "axios";
import CompilerComparisonHistogram from './graph/CompilerComparisonHistogram';
export default function BrowseResult({ isLoading, shouldLoadHTML, setIsLoading, setShouldLoadHTML }) {


    return (
        <div style={{ marginTop: 80 }}>

            <CompilerComparisonHistogram />


        </div>
    )
}