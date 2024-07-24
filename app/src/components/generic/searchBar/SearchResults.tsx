import React, { useState, useEffect } from 'react';
import Highlighter from 'react-highlight-words';

type Props = {
    searchTerm: string;
    text: string;
};

const SearchResults = ({ searchTerm, text }: Props) => {
    const [currentMatchIndex, setCurrentMatchIndex] = useState<number>(0);

    const matches = Array.from(text.matchAll(new RegExp(searchTerm, 'gi')));
    const matchCount = matches.length;

    useEffect(() => {
        setCurrentMatchIndex(0);
    }, [searchTerm]);

    const goToNextMatch = () => {
        setCurrentMatchIndex((prevIndex) => (prevIndex + 1) % matchCount);
    };

    const goToPreviousMatch = () => {
        setCurrentMatchIndex((prevIndex) => (prevIndex - 1 + matchCount) % matchCount);
    };

    return (
        <div className="content">
            <Highlighter
                highlightClassName="highlight"
                searchWords={[searchTerm]}
                autoEscape={true}
                textToHighlight={text}
            />
            {searchTerm && matchCount > 0 && (
                <div>
                    <button onClick={goToPreviousMatch}>Previous</button>
                    <button onClick={goToNextMatch}>Next</button>
                    <span>
                        {currentMatchIndex + 1} / {matchCount}
                    </span>
                </div>
            )}
        </div>
    );
};

export default SearchResults;
