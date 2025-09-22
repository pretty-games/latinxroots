// Global variables
let allPeople = [];
let displayedPeople = [];
const baseUrl = 'https://pretty-games.github.io/latinxroots/';

// DOM elements
const peopleGrid = document.getElementById('people-grid');
const modal = document.getElementById('person-modal');
const modalBody = document.getElementById('modal-body');
const closeModal = document.querySelector('.close');

// Initialize the application
document.addEventListener('DOMContentLoaded', async () => {
    await loadPeople();
    displayPeople(allPeople);
});

// Load all people data
async function loadPeople() {
    try {
        // Show loading state
        peopleGrid.innerHTML = '<div class="loading">Loading people...</div>';

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
                const person = await response.json();
                person._filename = filename; // Store filename for reference
                return person;
            } catch (error) {
                console.warn(`Error fetching ${filename}:`, error);
                return null;
            }
        });

        // Wait for all requests to complete and filter out failed ones
        const peopleResults = await Promise.all(peoplePromises);
        allPeople = peopleResults.filter(person => person !== null);

        console.log(`Loaded ${allPeople.length} people`);

    } catch (error) {
        console.error('Error loading people:', error);
        peopleGrid.innerHTML = '<div class="loading">Error loading people. Please try again later.</div>';
    }
}

// Display people in the grid
function displayPeople(people) {
    displayedPeople = people;

    if (people.length === 0) {
        peopleGrid.innerHTML = '<div class="loading">No people found matching your search.</div>';
        return;
    }

    peopleGrid.innerHTML = people.map(person => createPersonCard(person)).join('');

    // Add click event listeners to cards
    document.querySelectorAll('.person-card').forEach((card, index) => {
        card.addEventListener('click', () => openPersonModal(people[index]));
    });
}

// Create a person card HTML
function createPersonCard(person) {
    const birthDate = person.info.birthdate ? formatDate(person.info.birthdate) : '';
    const deathDate = person.info.deathdate ? formatDate(person.info.deathdate) : '';
    const dateRange = deathDate ? `${birthDate} - ${deathDate}` : `${birthDate} - Present`;

    const knownForText = person.knownFor && person.knownFor.length > 0
        ? person.knownFor[0].substring(0, 150) + (person.knownFor[0].length > 150 ? '...' : '')
        : 'No description available';

    const tags = person.info.tags || [];
    const tagsHtml = tags.map(tag => `<span class="tag">${escapeHtml(tag)}</span>`).join('');

    const imageUrl = person.image ? `${baseUrl}${person.image}` : `${baseUrl}people/images/person-image-template.png`;

    return `
        <div class="person-card">
            <img src="${imageUrl}" alt="${escapeHtml(person.preferredName)}" class="person-image"
                 onerror="this.src='${baseUrl}people/images/person-image-template.png'">
            <div class="person-name">${escapeHtml(person.preferredName)}</div>
            <div class="person-dates">${escapeHtml(dateRange)}</div>
            <div class="person-known-for">${escapeHtml(knownForText)}</div>
            <div class="person-tags">${tagsHtml}</div>
        </div>
    `;
}

// Open person detail modal
function openPersonModal(person) {
    const birthDate = person.info.birthdate ? formatDate(person.info.birthdate) : 'Unknown';
    const deathDate = person.info.deathdate ? formatDate(person.info.deathdate) : 'Present';
    const dateRange = deathDate !== 'Present' ? `${birthDate} - ${deathDate}` : `${birthDate} - Present`;

    const imageUrl = person.image ? `${baseUrl}${person.image}` : `${baseUrl}people/images/person-image-template.png`;

    // Build info grid
    const infoItems = [
        { label: 'Full Name', value: person.info.fullname || person.preferredName },
        { label: 'Born', value: person.info.bornlocation || 'Unknown' },
        { label: 'Origin', value: person.info.origin || 'Unknown' },
        { label: 'Birth Date', value: birthDate },
        { label: 'Death Date', value: deathDate === 'Present' ? 'Still alive' : deathDate }
    ];

    const infoGridHtml = infoItems.map(item => `
        <div class="info-item">
            <div class="info-label">${item.label}</div>
            <div class="info-value">${escapeHtml(item.value)}</div>
        </div>
    `).join('');

    // Build tags
    const tags = person.info.tags || [];
    const tagsHtml = tags.map(tag => `<span class="tag">${escapeHtml(tag)}</span>`).join('');

    // Build known for section
    const knownForHtml = person.knownFor && person.knownFor.length > 0
        ? `<ul>${person.knownFor.map(item => `<li>${escapeHtml(item)}</li>`).join('')}</ul>`
        : '<p>No information available.</p>';

    // Build impact section
    const impactHtml = person.impact && person.impact.length > 0
        ? `<ul>${person.impact.map(item => `<li>${escapeHtml(item)}</li>`).join('')}</ul>`
        : '<p>No information available.</p>';

    // Build sources section
    const sourcesHtml = person.sources && person.sources.length > 0
        ? `<ul class="sources-list">${person.sources.map(source =>
            `<li><a href="${source.url}" target="_blank" rel="noopener noreferrer">${escapeHtml(source.description)}</a></li>`
          ).join('')}</ul>`
        : '<p>No sources available.</p>';

    modalBody.innerHTML = `
        <div class="modal-header">
            <img src="${imageUrl}" alt="${escapeHtml(person.preferredName)}" class="modal-image"
                 onerror="this.src='${baseUrl}people/images/person-image-template.png'">
            <div class="modal-name">${escapeHtml(person.preferredName)}</div>
            <div class="modal-dates">${escapeHtml(dateRange)}</div>
            <div class="person-tags" style="justify-content: center; margin-top: 1rem;">${tagsHtml}</div>
        </div>

        <div class="info-grid">
            ${infoGridHtml}
        </div>

        <div class="section">
            <div class="section-title">Known For</div>
            <div class="section-content">${knownForHtml}</div>
        </div>

        <div class="section">
            <div class="section-title">Impact (to society and latino community)</div>
            <div class="section-content">${impactHtml}</div>
        </div>

        <div class="section">
            <div class="section-title">Sources</div>
            <div class="section-content">${sourcesHtml}</div>
        </div>
    `;

    modal.style.display = 'block';
    document.body.style.overflow = 'hidden'; // Prevent background scrolling
}

// Close modal when clicking the X or outside the modal
closeModal.addEventListener('click', closePersonModal);
modal.addEventListener('click', (e) => {
    if (e.target === modal) {
        closePersonModal();
    }
});

// Close modal with escape key
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && modal.style.display === 'block') {
        closePersonModal();
    }
});

function closePersonModal() {
    modal.style.display = 'none';
    document.body.style.overflow = 'auto'; // Restore background scrolling
}

// Utility functions
function formatDate(dateString) {
    if (!dateString) return 'Unknown';

    try {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    } catch (error) {
        return dateString; // Return original if parsing fails
    }
}

function escapeHtml(text) {
    if (typeof text !== 'string') return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Export functions for use in other scripts
window.mainApp = {
    allPeople,
    displayedPeople,
    displayPeople,
    loadPeople
};