import React, { useState } from 'react';

type Props = {
    setSearchTerm: React.Dispatch<React.SetStateAction<string>>;
    resultsCount: number;
};

const SearchBar = ({ setSearchTerm, resultsCount }: Props) => {
    const [searchValue, setSearchValue] = useState<string>('');
    const [emptyResults, setEmptyResults] = useState<boolean>(true);

    const handleSearch = (event: React.FormEvent<HTMLFormElement>) => {
        event.preventDefault();
        setSearchTerm(searchValue);
        if (!searchValue) {
            setEmptyResults(true);
        } else {
            setEmptyResults(false);
        }
    };

    const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        setSearchValue(event.target.value);
    };

    return (
        <div>
            <form onSubmit={handleSearch} className="search-form">
                <div className="nhsuk-form-group">
                    <label className="nhsuk-hint" id="search-input--hint">
                        Search a word, date or file in the records
                    </label>
                    <input
                        className="nhsuk-input"
                        type="text"
                        autoComplete="off"
                        value={searchValue}
                        onChange={handleInputChange}
                    />
                    <button
                        className="nhsuk-button"
                        aria-disabled="false"
                        type="submit"
                        id="search-content-submit"
                        data-testid="search-content-submit-btn"
                    >
                        Search records
                    </button>
                    {!emptyResults && (
                        <input
                            className="nhsuk-input"
                            type="text"
                            autoComplete="off"
                            value={
                                !emptyResults ? `${resultsCount} results found` : '0 results found'
                            }
                            disabled
                        />
                    )}
                </div>
            </form>
        </div>
    );
};

export default SearchBar;
