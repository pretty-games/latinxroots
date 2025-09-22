// Search functionality
const searchInput = document.getElementById('search-input');

// Initialize search
document.addEventListener('DOMContentLoaded', () => {
    searchInput.addEventListener('input', debounce(handleSearch, 300));
    searchInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            handleSearch();
        }
    });
});

// Debounce function to limit search frequency
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Handle search input
function handleSearch() {
    const query = searchInput.value.trim();

    // Check if data is loaded
    if (!window.mainApp || !window.mainApp.allPeople || window.mainApp.allPeople.length === 0) {
        console.log('Data not loaded yet, skipping search');
        return;
    }

    if (!query) {
        // If no search query, show all people
        window.mainApp.displayPeople(window.mainApp.allPeople);
        return;
    }

    console.log('Searching for:', query);
    const filteredPeople = searchPeople(window.mainApp.allPeople, query);
    console.log('Found:', filteredPeople.length, 'results');
    window.mainApp.displayPeople(filteredPeople);
}

// Search people based on query
function searchPeople(people, query) {
    // Check if it's a field-scoped search (field:value format)
    const fieldMatch = query.match(/^(\w+):(.+)$/);

    if (fieldMatch) {
        const [, field, value] = fieldMatch;
        return searchByField(people, field.toLowerCase(), value);
    } else {
        // General search across all fields
        return searchGeneral(people, query);
    }
}

// Search by specific field
function searchByField(people, field, value) {
    const isRegex = isValidRegex(value);
    const searchRegex = isRegex ? new RegExp(value, 'i') : null;

    console.log(`Searching field '${field}' for '${value}' (regex: ${isRegex})`);

    const results = people.filter(person => {
        let fieldValue = '';

        switch (field) {
            case 'tags':
                fieldValue = (person.info.tags || []).join(' ');
                break;
            case 'origin':
                fieldValue = person.info.origin || '';
                break;
            case 'bornlocation':
            case 'born':
                fieldValue = person.info.bornlocation || '';
                break;
            case 'name':
            case 'preferredname':
                fieldValue = person.preferredName || '';
                break;
            case 'fullname':
                fieldValue = person.info.fullname || '';
                break;
            case 'knownfor':
                fieldValue = (person.knownFor || []).join(' ');
                break;
            case 'impact':
                fieldValue = (person.impact || []).join(' ');
                break;
            case 'birthdate':
                fieldValue = person.info.birthdate || '';
                break;
            case 'deathdate':
                fieldValue = person.info.deathdate || '';
                break;
            default:
                console.log(`Unknown field: ${field}`);
                return false;
        }

        const matches = searchRegex ? searchRegex.test(fieldValue) : fieldValue.toLowerCase().includes(value.toLowerCase());

        if (matches) {
            console.log(`Match found in ${person.preferredName}: field='${field}', value='${fieldValue}', query='${value}'`);
        }

        return matches;
    });

    console.log(`Field search results: ${results.length} matches`);
    return results;
}

// General search across all fields
function searchGeneral(people, query) {
    const isRegex = isValidRegex(query);
    const searchRegex = isRegex ? new RegExp(query, 'i') : null;
    const lowerQuery = query.toLowerCase();

    console.log(`General search for '${query}' (regex: ${isRegex})`);

    const results = people.filter(person => {
        // Create a searchable text string from all person data
        const searchableText = [
            person.preferredName,
            person.info.fullname,
            person.info.origin,
            person.info.bornlocation,
            person.info.birthdate,
            person.info.deathdate,
            ...(person.info.tags || []),
            ...(person.knownFor || []),
            ...(person.impact || [])
        ].join(' ').toLowerCase();

        const matches = searchRegex ? searchRegex.test(searchableText) : searchableText.includes(lowerQuery);

        if (matches) {
            console.log(`General match found in ${person.preferredName}`);
        }

        return matches;
    });

    console.log(`General search results: ${results.length} matches`);
    return results;
}

// Check if a string is a valid regex
function isValidRegex(str) {
    // Don't treat simple strings as regex
    if (!/[.*+?^${}()|[\]\\]/.test(str)) {
        return false;
    }

    try {
        new RegExp(str);
        return true;
    } catch (e) {
        return false;
    }
}

// Export search functions
window.searchApp = {
    searchPeople,
    searchByField,
    searchGeneral,
    handleSearch
};