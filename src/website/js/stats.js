// Statistics page functionality
const baseUrl = 'https://pretty-games.github.io/latinxroots/';

// DOM elements
const tagsLoading = document.getElementById('tags-loading');
const tagsList = document.getElementById('tags-list');
const countriesLoading = document.getElementById('countries-loading');
const countriesList = document.getElementById('countries-list');

// Initialize statistics page
document.addEventListener('DOMContentLoaded', async () => {
    await loadAndDisplayStats();
});

// Load people data and display statistics
async function loadAndDisplayStats() {
    try {
        // Fetch the list of people
        const listResponse = await fetch(`${baseUrl}people/list.json`);
        if (!listResponse.ok) {
            throw new Error(`Failed to fetch people list: ${listResponse.status}`);
        }
        const peopleList = await listResponse.json();

        // Fetch all individual person data
        const peoplePromises = peopleList.map(async (filename) => {
            try {
                const response = await fetch(`${baseUrl}people/${filename}`);
                if (!response.ok) {
                    console.warn(`Failed to fetch ${filename}: ${response.status}`);
                    return null;
                }
                return await response.json();
            } catch (error) {
                console.warn(`Error fetching ${filename}:`, error);
                return null;
            }
        });

        // Wait for all requests to complete and filter out failed ones
        const peopleResults = await Promise.all(peoplePromises);
        const allPeople = peopleResults.filter(person => person !== null);

        console.log(`Loaded ${allPeople.length} people for statistics`);

        // Generate and display statistics
        displayTagsStats(allPeople);
        displayCountriesStats(allPeople);

    } catch (error) {
        console.error('Error loading statistics:', error);
        tagsLoading.textContent = 'Error loading tags statistics';
        countriesLoading.textContent = 'Error loading countries statistics';
    }
}

// Display tags statistics
function displayTagsStats(people) {
    const tagCounts = {};

    // Count all tags
    people.forEach(person => {
        const tags = person.info.tags || [];
        tags.forEach(tag => {
            tagCounts[tag] = (tagCounts[tag] || 0) + 1;
        });
    });

    // Sort tags alphabetically
    const sortedTags = Object.entries(tagCounts)
        .sort(([a], [b]) => a.localeCompare(b));

    if (sortedTags.length === 0) {
        tagsLoading.textContent = 'No tags found';
        return;
    }

    // Generate HTML for tags list
    const tagsHtml = sortedTags.map(([tag, count]) => `
        <li class="stats-item">
            <span class="stats-name">${escapeHtml(tag)}</span>
            <span class="stats-count">${count}</span>
        </li>
    `).join('');

    tagsList.innerHTML = tagsHtml;
    tagsLoading.style.display = 'none';
    tagsList.style.display = 'block';
}

// Display countries statistics
function displayCountriesStats(people) {
    const countryCounts = {};

    // Count countries from birth locations
    people.forEach(person => {
        const bornLocation = person.info.bornlocation;
        if (bornLocation) {
            const country = extractCountryFromLocation(bornLocation);
            if (country) {
                countryCounts[country] = (countryCounts[country] || 0) + 1;
            }
        }
    });

    // Sort countries alphabetically
    const sortedCountries = Object.entries(countryCounts)
        .sort(([a], [b]) => a.localeCompare(b));

    if (sortedCountries.length === 0) {
        countriesLoading.textContent = 'No countries found';
        return;
    }

    // Generate HTML for countries list
    const countriesHtml = sortedCountries.map(([country, count]) => `
        <li class="stats-item">
            <span class="stats-name">${escapeHtml(country)}</span>
            <span class="stats-count">${count}</span>
        </li>
    `).join('');

    countriesList.innerHTML = countriesHtml;
    countriesLoading.style.display = 'none';
    countriesList.style.display = 'block';
}

// Extract country name from birth location string
function extractCountryFromLocation(location) {
    if (!location || typeof location !== 'string') {
        return null;
    }

    // Common patterns for location strings:
    // "City, Country"
    // "City, State, Country"
    // "Country"

    // Split by comma and take the last part as country
    const parts = location.split(',').map(part => part.trim());

    if (parts.length === 0) {
        return null;
    }

    // Take the last part as the country
    let country = parts[parts.length - 1];

    // Clean up common patterns
    country = country.replace(/^(in\s+|of\s+)/i, ''); // Remove "in " or "of " prefixes
    country = country.replace(/\s+(empire|colony|territory)$/i, ''); // Remove political designations

    // Handle special cases and normalize country names
    const countryMappings = {
        'usa': 'United States',
        'us': 'United States',
        'united states of america': 'United States',
        'uk': 'United Kingdom',
        'britain': 'United Kingdom',
        'great britain': 'United Kingdom',
        'ussr': 'Soviet Union',
        'soviet union': 'Soviet Union',
        'russia': 'Russia',
        'brasil': 'Brazil',
        'méxico': 'Mexico',
        'perú': 'Peru',
        'panamá': 'Panama',
        'república dominicana': 'Dominican Republic',
        'puerto rico': 'Puerto Rico',
        'costa rica': 'Costa Rica',
        'el salvador': 'El Salvador'
    };

    const normalizedCountry = country.toLowerCase();
    const mappedCountry = countryMappings[normalizedCountry];

    if (mappedCountry) {
        return mappedCountry;
    }

    // Capitalize first letter of each word
    return country.split(' ')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
        .join(' ');
}

// Utility function to escape HTML
function escapeHtml(text) {
    if (typeof text !== 'string') return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}