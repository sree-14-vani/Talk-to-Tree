// Talk to a Tree - JavaScript
document.addEventListener('DOMContentLoaded', function() {
    const demoMode = window.demoMode === true || window.demoMode === 'true';

    // Initialize plant data if available
    let allPlants = window.allPlants || [];

    // Check if we're on the explore page
    const exploreGrid = document.getElementById('plants-grid');
    if (exploreGrid) {
        initExplorePage();
    }

    // Check if we're on the plant page
    const plantNameEl = document.querySelector('.plant-name');
    if (plantNameEl) {
        initPlantPage();
    }

    // Search suggestion chips
    initSuggestionChips();

    // Filter functionality
    initFilters();

    // Mobile menu toggle
    initMobileMenu();

    // Demo mode handling
    if (demoMode) {
        updateDemoModeUI();
    }

    // Initialize search functionality
    initSearch();
});

function initSuggestionChips() {
    const chips = document.querySelectorAll('.suggestion-chip');
    chips.forEach(chip => {
        chip.addEventListener('click', function() {
            const plantName = this.getAttribute('data-plant');
            if (plantName) {
                window.location.href = `/plant/${plantName}`;
            }
        });
    });
}

function initExplorePage() {
    attachPlantCardListeners();
}

function initFilters() {
    const typeFilter = document.getElementById('type-filter');
    const habitatFilter = document.getElementById('habitat-filter');
    const clearFilters = document.getElementById('clear-filters');
    const plantCards = document.querySelectorAll('.plant-card');
    const resultsCount = document.getElementById('results-count');
    const activeFiltersEl = document.getElementById('active-filters');

    if (!typeFilter || !habitatFilter || !clearFilters) return;

    function applyFilters() {
        const typeValue = typeFilter.value;
        const habitatValue = habitatFilter.value;
        let visibleCount = 0;

        plantCards.forEach(card => {
            const plantType = card.getAttribute('data-type');
            const plantHabitat = card.getAttribute('data-habitat');
            const shows = (!typeValue || plantType.includes(typeValue)) &&
                         (!habitatValue || plantHabitat.includes(habitatValue));
            card.style.display = shows ? 'block' : 'none';
            if (shows) visibleCount++;
        });

        if (resultsCount) {
            resultsCount.textContent = `${visibleCount} plants found`;
        }
        if (activeFiltersEl) {
            activeFiltersEl.hidden = !(typeValue || habitatValue);
        }
    }

    typeFilter.addEventListener('change', applyFilters);
    habitatFilter.addEventListener('change', applyFilters);

    if (clearFilters) {
        clearFilters.addEventListener('click', function() {
            typeFilter.value = '';
            habitatFilter.value = '';
            applyFilters();
        });
    }

    applyFilters();
}

function initFiltersExplore() {
    const typeFilter = document.getElementById('type-filter');
    const habitatFilter = document.getElementById('habitat-filter');
    const clearFilters = document.getElementById('clear-filters');
    const plantCards = document.querySelectorAll('.plant-card');
    const resultsCount = document.getElementById('results-count');
    const activeFiltersEl = document.getElementById('active-filters');

    if (!typeFilter || !habitatFilter || !clearFilters || !resultsCount) return;

    function applyFilters() {
        const typeValue = typeFilter.value;
        const habitatValue = habitatFilter.value;
        let visibleCount = 0;

        plantCards.forEach(card => {
            const plantType = card.getAttribute('data-type');
            const plantHabitat = card.getAttribute('data-habitat');
            const shows = (!typeValue || plantType.includes(typeValue)) &&
                         (!habitatValue || plantHabitat.includes(habitatValue));
            card.style.display = shows ? 'block' : 'none';
            if (shows) visibleCount++;
        });

        resultsCount.textContent = `${visibleCount} plants found`;
        activeFiltersEl.hidden = !(typeValue || habitatValue);
    }

    typeFilter.addEventListener('change', applyFilters);
    habitatFilter.addEventListener('change', applyFilters);

    clearFilters.addEventListener('click', function() {
        typeFilter.value = '';
        habitatFilter.value = '';
        applyFilters();
    });

    applyFilters();
}

function initPlantPage() {
    const plantName = window.plantName || 'Banyan';
    updatePlantPageUI(plantName);
    initNarrator(plantName);

    // Story button
    const storyBtn = document.getElementById('story-btn');
    if (storyBtn) {
        storyBtn.addEventListener('click', function() {
            generateStory(plantName);
        });
    }

    // Fact button
    const factBtn = document.getElementById('fact-btn');
    if (factBtn) {
        factBtn.addEventListener('click', function() {
            getRandomFact(plantName);
        });
    }

    // Chat form
    const chatForm = document.getElementById('chat-form');
    if (chatForm) {
        chatForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const input = document.getElementById('chat-input');
            if (input && input.value.trim()) {
                sendChatMessage(plantName, input.value.trim());
                input.value = '';
            }
        });
    }

    // Suggestion buttons
    const suggestionBtns = document.querySelectorAll('.info-node');
    suggestionBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const target = this.getAttribute('data-target');
            if (target) {
                scrollToSection(target);
            }
        });
    });

    // Chat suggestion buttons
    const chatSuggestionBtns = document.querySelectorAll('.suggestion-btn');
    chatSuggestionBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const question = this.getAttribute('data-question');
            if (question && window.sendChatMessage) {
                sendChatMessage(plantName, question);
            }
        });
    });

    // Compare form
    const compareForm = document.getElementById('compare-form');
    if (compareForm) {
        compareForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const plant1 = document.getElementById('compare-plant1').value;
            const plant2 = document.getElementById('compare-plant2').value;
            if (plant1 && plant2 && plant1 !== plant2) {
                comparePlants(plant1, plant2);
            }
        });
    }
}

function initNarrator(plantName) {
    const playButton = document.getElementById('narrator-play');
    const pauseButton = document.getElementById('narrator-pause');
    const stopButton = document.getElementById('narrator-stop');
    const status = document.getElementById('narrator-status');
    const transcript = document.getElementById('narrator-transcript-text');
    const languageSelect = document.getElementById('narrator-language');
    const cartoonStage = document.querySelector('.plant-cartoon-stage');

    if (!playButton || !pauseButton || !stopButton || !status || !transcript || !languageSelect) return;

    const profile = window.plantProfile || {};
    const sections = Object.entries(profile.sections || {})
        .map(([title, content]) => `${title}. ${content}`)
        .join(' ');
    const narration = [
        `Hello, I am ${plantName}.`,
        profile.scientific_name ? `My scientific name is ${profile.scientific_name}.` : '',
        profile.plant_type ? `I am a ${profile.plant_type} in the ${profile.family || 'plant'} family.` : '',
        profile.native_distribution ? `I am native to ${profile.native_distribution}.` : '',
        profile.habitat ? `My habitat is ${profile.habitat}.` : '',
        sections,
        profile.safety_note ? `A note for your safety: ${profile.safety_note}` : ''
    ].filter(Boolean).join(' ');

    transcript.textContent = narration;

    if (!('speechSynthesis' in window) || !('SpeechSynthesisUtterance' in window)) {
        status.textContent = 'Audio narration is not supported in this browser. The full introduction is available below.';
        playButton.disabled = true;
        return;
    }

    let utterance = null;

    const voiceProfiles = {
        banyan: { rate: 0.84, pitch: 0.72, names: ['David', 'Guy', 'Mark'] },
        ashoka: { rate: 0.92, pitch: 0.84, names: ['Samantha', 'Zira', 'Aria'] },
        neem: { rate: 1.0, pitch: 1.04, names: ['Sonia', 'Jenny', 'Hazel'] },
        peepal: { rate: 0.88, pitch: 0.96, names: ['Daniel', 'George', 'Alex'] },
        mango: { rate: 1.05, pitch: 1.12, names: ['Karen', 'Victoria', 'Ava'] },
        bamboo: { rate: 1.12, pitch: 1.18, names: ['Moira', 'Libby', 'Susan'] }
    };

    function getVoiceProfile() {
        const key = plantName.toLowerCase();
        return voiceProfiles[key] || { rate: 0.94, pitch: 0.96, names: [] };
    }

    function setControls(isSpeaking, isPaused) {
        playButton.disabled = isSpeaking && !isPaused;
        pauseButton.disabled = !isSpeaking;
        stopButton.disabled = !isSpeaking;
        pauseButton.innerHTML = isPaused ? '<span aria-hidden="true">▶</span> Resume' : '<span aria-hidden="true">Ⅱ</span> Pause';
        if (cartoonStage) cartoonStage.classList.toggle('is-speaking', isSpeaking && !isPaused);
    }

    function stopNarration(message = 'Ready when you are.') {
        window.speechSynthesis.cancel();
        utterance = null;
        setControls(false, false);
        status.textContent = message;
    }

    playButton.addEventListener('click', async function() {
        window.speechSynthesis.cancel();
        const language = languageSelect.value;
        let speechText = narration;

        if (language !== 'en-US') {
            status.textContent = `Preparing ${languageSelect.options[languageSelect.selectedIndex].text} narration...`;
            playButton.disabled = true;
            try {
                const translationResponse = await fetch('/api/translate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ text: narration, language })
                });
                const translation = await translationResponse.json();
                if (!translationResponse.ok || !translation.translated) {
                    throw new Error(translation.error || 'Translation unavailable');
                }
                speechText = translation.text;
            } catch (error) {
                setControls(false, false);
                status.textContent = 'This language is not available right now. Choose another installed language or read the transcript below.';
                return;
            }
        }

        utterance = new SpeechSynthesisUtterance(speechText);
        const voiceProfile = getVoiceProfile();
        const voices = window.speechSynthesis.getVoices();
        const languagePrefix = language.split('-')[0].toLowerCase();
        const languageVoices = voices.filter(voice => voice.lang.toLowerCase().startsWith(languagePrefix));
        const preferredVoice = languageVoices.find(voice => voiceProfile.names.some(name => voice.name.includes(name))) || languageVoices[0];
        if (preferredVoice) utterance.voice = preferredVoice;
        utterance.lang = language;
        utterance.rate = voiceProfile.rate;
        utterance.pitch = voiceProfile.pitch;
        utterance.onstart = () => {
            setControls(true, false);
            status.textContent = `${plantName} is speaking...`;
        };
        utterance.onend = () => stopNarration('Introduction complete. You can start again whenever you like.');
        utterance.onerror = () => stopNarration('Narration stopped. You can start it again.');
        setControls(true, false);
        status.textContent = `${plantName} is speaking...`;
        window.speechSynthesis.speak(utterance);
    });

    pauseButton.addEventListener('click', function() {
        if (window.speechSynthesis.paused) {
            window.speechSynthesis.resume();
            setControls(true, false);
            status.textContent = `${plantName} is speaking...`;
        } else {
            window.speechSynthesis.pause();
            setControls(true, true);
            status.textContent = 'Narration paused. Press Resume whenever you are ready.';
        }
    });

    stopButton.addEventListener('click', () => stopNarration('Narration stopped. You can start it again.'));

    languageSelect.addEventListener('change', function() {
        if (window.speechSynthesis.speaking || window.speechSynthesis.paused) {
            stopNarration(`Language changed to ${this.options[this.selectedIndex].text}. Press Start to listen again.`);
        } else {
            status.textContent = `${this.options[this.selectedIndex].text} narration ready.`;
        }
    });
}

function updatePlantPageUI(plantName) {
    // Update breadcrumb
    const breadcrumbLinks = document.querySelectorAll('.plant-breadcrumb a');
    if (breadcrumbLinks.length >= 2) {
        breadcrumbLinks[1].textContent = plantName;
        breadcrumbLinks[1].href = `/plant/${plantName.toLowerCase().replace(/\s/g, '-')}`;
    }

    // Update page title
    const h1 = document.querySelector('.plant-name');
    if (h1) {
        h1.textContent = plantName;
    }
}

function scrollToSection(sectionId) {
    const section = document.querySelector(`[data-section="${sectionId}"]`);
    if (section) {
        section.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

function updateDemoModeUI() {
    const demoBadges = document.querySelectorAll('.demo-badge');
    demoBadges.forEach(badge => {
        badge.style.display = 'inline-block';
    });
}

async function sendChatMessage(plantName, message) {
    const chatContainer = document.getElementById('chat-container');
    const chatStatus = document.getElementById('chat-status');

    if (!chatContainer) return;

    // Add user message
    const msgDiv = document.createElement('div');
    msgDiv.className = 'chat-message user';
    msgDiv.innerHTML = `
        <div class="message-avatar" aria-hidden="true">🧑</div>
        <div class="message-content">
            <p>${escapeHtml(message)}</p>
        </div>
    `;
    chatContainer.appendChild(msgDiv);

    // Scroll to bottom
    chatContainer.scrollTop = chatContainer.scrollHeight;

    // Show loading status
    if (chatStatus) {
        chatStatus.textContent = 'Thinking...';
        chatStatus.style.display = 'block';
    }

    try {
        const response = await fetch(`/api/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                question: message,
                plant_name: plantName,
                history: getChatHistory()
            })
        });

        const data = await response.json();

        // Remove loading status
        if (chatStatus) {
            chatStatus.style.display = 'none';
        }

        // Add assistant response
        const responseDiv = document.createElement('div');
        responseDiv.className = 'chat-message bot';
        responseDiv.setAttribute('role', 'alert');
        responseDiv.setAttribute('aria-live', 'polite');

        // Process the answer - handle both plain text and HTML
        let answerHtml = data.answer || 'No response';
        if (typeof answerHtml === 'string') {
            // Simple processing - in production, use marked or similar
            answerHtml = answerHtml.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                .replace(/\*(.*?)\*/g, '<em>$1</em>')
                .replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2">$1</a>');
        }

        responseDiv.innerHTML = `
            <div class="message-avatar" aria-hidden="true">🌳</div>
            <div class="message-content">
                <p>${answerHtml}</p>
            </div>
        `;
        chatContainer.appendChild(responseDiv);

        // Scroll to bottom
        chatContainer.scrollTop = chatContainer.scrollHeight;

        // Update sources if available
        if (data.sources && data.sources.length > 0) {
            showSourcesModal(data.sources);
        }

    } catch (error) {
        if (chatStatus) {
            chatStatus.textContent = 'Error connecting to server';
            chatStatus.style.display = 'block';
            setTimeout(() => chatStatus.style.display = 'none', 3000);
        }
        console.error('Chat error:', error);
    }
}

function getChatHistory() {
    const messages = document.querySelectorAll('.chat-message');
    const history = [];
    messages.forEach(msg => {
        const role = msg.classList.contains('user') ? 'user' : 'assistant';
        const content = msg.querySelector('.message-content p');
        if (content) {
            history.push({ role, content: content.textContent });
        }
    });
    return history.slice(-4);
}

function showSourcesModal(sources) {
    const modal = document.getElementById('sources-modal');
    const sourcesBody = document.getElementById('sources-body');

    if (!modal || !sourcesBody) return;

    sourcesBody.innerHTML = '';

    sources.forEach((source, i) => {
        const div = document.createElement('div');
        div.innerHTML = `
            <div style="margin-bottom: 1rem; padding-bottom: 1rem; border-bottom: 1px solid #eee;">
                <h4 style="margin-bottom: 0.5rem;">Source ${i + 1}: ${source.plant}</h4>
                <p style="margin: 0; font-size: 0.875rem; color: var(--muted);">${source.source_file}</p>
                <p style="margin: 0.2rem 0; font-size: 0.75rem;">${source.section || 'General'}</p>
            </div>
        `;
        sourcesBody.appendChild(div);
    });

    modal.style.display = 'block';
    modal.removeAttribute('hidden');
    modal.setAttribute('aria-modal', 'true');
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

async function generateStory(plantName) {
    const chatStatus = document.getElementById('chat-status');
    if (chatStatus) {
        chatStatus.textContent = 'Generating story...';
        chatStatus.style.display = 'block';
    }

    try {
        const response = await fetch(`/api/story/${plantName}`, {
            method: 'GET'
        });

        const data = await response.json();

        if (chatStatus) {
            chatStatus.style.display = 'none';
        }

        // Show in a simple alert or could redirect to a story page
        alert(`${plantName} Story:\n\n${data.story}`);
    } catch (error) {
        if (chatStatus) {
            chatStatus.textContent = 'Error generating story';
            chatStatus.style.display = 'block';
            setTimeout(() => chatStatus.style.display = 'none', 3000);
        }
        console.error('Story error:', error);
    }
}

async function getRandomFact(plantName) {
    const chatStatus = document.getElementById('chat-status');
    if (chatStatus) {
        chatStatus.textContent = 'Getting fact...';
        chatStatus.style.display = 'block';
    }

    try {
        const response = await fetch(`/api/fact`, {
            method: 'GET'
        });

        const data = await response.json();

        if (chatStatus) {
            chatStatus.style.display = 'none';
        }

        if (data.plant === plantName) {
            alert(`${plantName} Fact:\n\n${data.fact}`);
        } else {
            alert(`Random Nature Fact:\n\n${data.fact}\n\nAbout: ${data.plant}`);
        }
    } catch (error) {
        if (chatStatus) {
            chatStatus.textContent = 'Error getting fact';
            chatStatus.style.display = 'block';
            setTimeout(() => chatStatus.style.display = 'none', 3000);
        }
        console.error('Fact error:', error);
    }
}

async function comparePlants(plant1, plant2) {
    const compareResult = document.getElementById('compare-result');
    if (!compareResult) return;

    try {
        const response = await fetch(`/api/compare`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ plant1, plant2 })
        });

        const data = await response.json();

        if (data.error) {
            compareResult.innerHTML = `<div style="color: red;">${data.error}</div>`;
        } else {
            let html = `<h4>Comparison: ${data.plant1} vs ${data.plant2}</h4>`;
            html += `<table style="width: 100%; border-collapse: collapse; margin-top: 1rem;">`;

            data.categories.forEach((cat, i) => {
                const categoryKey = cat.toLowerCase().replace(/\s+/g, '_');
                const plant1Value = data.plant1.data[categoryKey] || 'N/A';
                const plant2Value = data.plant2.data[categoryKey] || 'N/A';
                html += `<tr style="border-bottom: 1px solid #eee;">
                    <td style="padding: 0.5rem; font-weight: bold; width: 30%;">${cat}</td>
                    <td style="padding: 0.5rem;">${escapeHtml(String(plant1Value))} vs ${escapeHtml(String(plant2Value))}</td>
                </tr>`;
            });

            html += `</table>`;
            compareResult.innerHTML = html;
        }

        compareResult.classList.add('active');
        compareResult.style.display = 'block';
    } catch (error) {
        console.error('Compare error:', error);
        compareResult.innerHTML = '<div style="color: red;">Error comparing plants</div>';
        compareResult.style.display = 'block';
    }
}

// Initialize search functionality
function initSearch() {
    // Search on home page
    const homeSearch = document.getElementById('hero-search-input');
    const homeSuggestions = document.getElementById('search-suggestions');

    // Search on explore page
    const exploreSearch = document.getElementById('explore-search');

    // Handle chip clicks to set search query
    const chips = document.querySelectorAll('.suggestion-chip');
    chips.forEach(chip => {
        chip.addEventListener('click', function() {
            const plantName = this.getAttribute('data-plant');
            if (plantName) {
                performSearch(plantName);
            }
        });
    });

    // Handle home search input
    if (homeSearch) {
        homeSearch.addEventListener('input', function() {
            const query = this.value.trim();
            if (query.length < 2) {
                homeSuggestions.innerHTML = '';
                homeSuggestions.hidden = true;
                return;
            }

            fetch(`/api/search?q=${encodeURIComponent(query)}`)
                .then(response => response.json())
                .then(data => {
                    homeSuggestions.innerHTML = (data.plants || []).slice(0, 5).map(plant => `
                        <a class="search-suggestion" role="option" href="/plant/${encodeURIComponent(plant.name)}">
                            <strong>${escapeHtml(plant.name)}</strong>
                            <span>${escapeHtml(plant.scientific_name || plant.plant_type || 'Plant profile')}</span>
                        </a>`).join('');
                    homeSuggestions.hidden = !data.plants || data.plants.length === 0;
                })
                .catch(() => {
                    homeSuggestions.innerHTML = '';
                    homeSuggestions.hidden = true;
                });
        });

        homeSearch.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                const query = this.value.trim();
                if (query) {
                    performSearch(query);
                }
            }
        });
    }

    // Handle explore search input
    if (exploreSearch) {
        exploreSearch.addEventListener('input', function() {
            const query = this.value.trim();
            if (query) {
                performExploreSearch(query);
            } else {
                window.location.reload();
            }
        });

        exploreSearch.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                const query = this.value.trim();
                if (query) {
                    performExploreSearch(query);
                }
            }
        });
    }

    // Initialize quick search from URL parameters
    const urlParams = new URLSearchParams(window.location.search);
    const quickSearch = urlParams.get('q');
    if (quickSearch) {
        if (exploreSearch) {
            exploreSearch.value = quickSearch;
            performExploreSearch(quickSearch);
        }
    }
}

function performSearch(query) {
    // Navigate to explore page with search query
    window.location.href = `/explore?q=${encodeURIComponent(query)}`;
}

function performExploreSearch(query) {
    if (!query) return;

    // Show loading state
    const resultsCount = document.getElementById('results-count');
    const emptyState = document.getElementById('empty-state');
    const plantsGrid = document.getElementById('plants-grid');
    const filterGroup = document.querySelector('.filter-group');

    if (resultsCount) resultsCount.textContent = 'Searching the botanical library...';
    if (filterGroup) filterGroup.style.display = 'none';
    if (emptyState) emptyState.hidden = true;

    // Make API call
    fetch(`/api/search?q=${encodeURIComponent(query)}`)
        .then(response => response.json())
        .then(data => {
            displaySearchResults(data.plants, query);
        })
        .catch(error => {
            console.error('Search error:', error);
            displayErrorState('Could not connect to the server. Please try again.');
        });
}

function displaySearchResults(plants, originalQuery) {
    const exploreGrid = document.getElementById('plants-grid');
    const resultsCount = document.getElementById('results-count');
    const emptyState = document.getElementById('empty-state');
    const filterGroup = document.querySelector('.filter-group');
    const plantsWindow = window.allPlants || [];

    if (resultsCount) {
        if (plants && plants.length > 0) {
            resultsCount.textContent = `${plants.length} plants found for "${originalQuery}"`;
        } else {
            resultsCount.textContent = `No plants found for "${originalQuery}".`;
            showSuggestions(originalQuery, plantsWindow);
        }
    }

    if (!plants || plants.length === 0) {
        if (emptyState) emptyState.hidden = false;
        return;
    }

    // If we have results, display them
    if (exploreGrid) {
        let html = '';
        plants.forEach(plant => {
            const plantData = plantsWindow.find(p => p.name.toLowerCase() === plant.name.toLowerCase());
            const name = plantData ? plantData.name : plant.name;
            const scientific = plantData ? plantData.scientific_name : '';
            const type = plantData ? plantData.plant_type : '';
            const family = plantData ? plantData.family : '';
            const habitat = plantData ? plantData.habitat : '';

            html += `
                <article class="plant-card" role="listitem" data-name="${name}" data-type="${type}" data-habitat="${habitat}">
                    <div class="plant-card-visual" aria-hidden="true">
                        <div class="plant-silhouette" data-plant="${name.toLowerCase()}"></div>
                    </div>
                    <div class="plant-card-overlay">
                        <a href="/plant/${name.toLowerCase().replace(/\s/g, '-')}" class="btn btn-primary">Explore</a>
                    </div>
                    <div class="plant-card-content">
                        <h3 class="plant-card-name">${name}</h3>
                        <p class="plant-card-scientific">${scientific}</p>
                        <p class="plant-card-type">${type} • ${family}</p>
                        <p class="plant-card-description">${plant.description || 'A remarkable plant with unique characteristics.'}</p>
                    </div>
                </article>`;
        });
        exploreGrid.innerHTML = html;

        // Re-attach event listeners for new cards
        attachPlantCardListeners();

        // Hide empty state and show filters
        if (emptyState) emptyState.hidden = true;
        if (filterGroup) filterGroup.style.display = 'block';
    }
}

function showSuggestions(originalQuery, plantsWindow) {
    const emptyState = document.getElementById('empty-state');
    const suggestionsSection = document.querySelector('.suggestions-section');

    if (emptyState) {
        let html = `
            <div class="empty-state" style="padding: 2rem; text-align: center;">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true" style="width: 60px; height: 60px; margin: 0 auto 1rem;">
                    <circle cx="11" cy="11" r="8"/>
                    <path d="M21 21l-4.35-4.35"/>
                </svg>
                <h3>Nothing found for "${originalQuery}"</h3>
                <p>Try searching for Banyan, Neem, Peepal or Mango.</p>
            </div>`;
        emptyState.innerHTML = html;
        emptyState.hidden = false;
    }

    // Add suggestion chips below the search
    const chipContainer = document.createElement('div');
    chipContainer.className = 'suggestions-section';
    chipContainer.innerHTML = `
        <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid #eee;">
            <h4 style="margin-bottom: 0.5rem; text-align: center;">Did you mean:</h4>
            <div style="display: flex; justify-content: center; gap: 0.5rem; flex-wrap: wrap;">
                <button class="suggestion-chip" data-plant="Banyan" style="font-size: 0.8rem;">🌳 Banyan</button>
                <button class="suggestion-chip" data-plant="Neem" style="font-size: 0.8rem;">🌿 Neem</button>
                <button class="suggestion-chip" data-plant="Peepal" style="font-size: 0.8rem;">🍃 Peepal</button>
                <button class="suggestion-chip" data-plant="Mango" style="font-size: 0.8rem;">🥭 Mango</button>
            </div>
        </div>`;

    // Insert after empty state
    const suggestionsExisting = document.querySelector('.suggestions-section');
    if (suggestionsExisting) suggestionsExisting.remove();
    const searchWrapper = document.querySelector('.search-wrapper');
    if (searchWrapper) {
        searchWrapper.appendChild(chipContainer);
    }
}

function attachPlantCardListeners() {
    const plantCards = document.querySelectorAll('.plant-card');
    plantCards.forEach(card => {
        card.addEventListener('click', function(e) {
            // Don't trigger if clicking on buttons/links inside
            if (e.target.tagName === 'A' || e.target.tagName === 'BUTTON') return;

            const name = this.getAttribute('data-name');
            if (name) {
                window.location.href = `/plant/${name.toLowerCase().replace(/\s/g, '-')}`;
            }
        });
    });
}

function displayErrorState(message) {
    const emptyState = document.getElementById('empty-state');
    const resultsCount = document.getElementById('results-count');
    const exploreGrid = document.getElementById('plants-grid');
    const filterGroup = document.querySelector('.filter-group');

    if (emptyState) {
        emptyState.innerHTML = `<div class="empty-state" style="padding: 2rem; text-align: center;"><p style="margin: 0;">${message}</p></div>`;
        emptyState.hidden = false;
    }
    if (resultsCount) resultsCount.textContent = '';
    if (exploreGrid) exploreGrid.innerHTML = '';
    if (filterGroup) filterGroup.style.display = 'none';
}

function initMobileMenu() {
    const menuBtn = document.querySelector('.mobile-menu-btn');
    const navList = document.querySelector('.nav-list');

    if (!menuBtn || !navList) return;

    menuBtn.addEventListener('click', function() {
        const isExpanded = this.getAttribute('aria-expanded') === 'true';
        this.setAttribute('aria-expanded', !isExpanded);
        navList.style.display = isExpanded ? 'none' : 'block';
    });
}