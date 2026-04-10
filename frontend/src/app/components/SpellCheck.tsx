import { useState } from "react";
import { SearchBar } from "./SearchBar";

export default function SearchPage() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [suggestion, setSuggestion] = useState("");

  const handleSearch = async () => {
    const res = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
    const data = await res.json();

    setResults(data.results);

    // Extract spellcheck suggestion
    const collations = data.spellcheck?.collations;
    if (collations && collations.length > 1) {
      setSuggestion(collations[1]);
    } else {
      setSuggestion("");
    }
  };

  return (
    <div>
      <SearchBar
        searchQuery={query}
        onSearchChange={setQuery}
        showAdvanced={false}
        onToggleAdvanced={() => {}}
        onSearch={handleSearch}
      />

        {suggestion && (
        <p>
            Did you mean:{" "}
            <button onClick={() => {
            setQuery(suggestion);
            handleSearch();
            }}>
            <b>{suggestion}</b>
            </button>
        </p>
        )}

      <ul>
        {results.map((r: any, i) => (
          <li key={i}>{r.title}</li>
        ))}
      </ul>
    </div>
  );
}