const searchBtn = document.getElementById('search-btn');
const searchInput = document.getElementById('search-input');
const resultsDiv = document.getElementById('results');
const recsDiv = document.getElementById('recommendations');
const audioPlayer = document.getElementById('audio-player');
const themeToggleBtn = document.getElementById('theme-toggle');

function setSearch(query) {
    searchInput.value = query;
}

function playSong(audioUrl, trackName, button) {
    // Check if the URL is a placeholder from the backend
    if (audioUrl.includes('example.com')) {
        // Use a custom modal or message box instead of alert
        const message = 'Audio preview is not available for this song. This is a demo application.';
        // Simple example: a floating div that disappears
        const msgDiv = document.createElement('div');
        msgDiv.textContent = message;
        msgDiv.style.cssText = 'position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); padding: 20px; background-color: rgba(0,0,0,0.8); color: white; border-radius: 10px; z-index: 1000; text-align: center;';
        document.body.appendChild(msgDiv);
        setTimeout(() => {
            document.body.removeChild(msgDiv);
        }, 3000);
        return;
    }
    
    if (audioPlayer.src !== audioUrl) {
        audioPlayer.src = audioUrl;
    }
    if (audioPlayer.paused) {
        audioPlayer.play().catch(err => {
            // Use a custom message box instead of alert
            const message = 'Unable to play audio. The audio file may not be available.';
            const msgDiv = document.createElement('div');
            msgDiv.textContent = message;
            msgDiv.style.cssText = 'position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); padding: 20px; background-color: rgba(0,0,0,0.8); color: white; border-radius: 10px; z-index: 1000; text-align: center;';
            document.body.appendChild(msgDiv);
            setTimeout(() => {
                document.body.removeChild(msgDiv);
            }, 3000);
            console.error('Audio play error:', err);
        });
        button.textContent = '⏸️ Pause';
        console.log(`Playing: ${trackName}`);
    } else {
        audioPlayer.pause();
        button.textContent = '▶️ Play';
        console.log(`Paused: ${trackName}`);
    }
}

searchBtn.addEventListener('click', () => {
    const query = searchInput.value.trim();
    if (!query) {
        // Use a custom message box instead of alert
        const message = 'Please enter a search query';
        const msgDiv = document.createElement('div');
        msgDiv.textContent = message;
        msgDiv.style.cssText = 'position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); padding: 20px; background-color: rgba(0,0,0,0.8); color: white; border-radius: 10px; z-index: 1000; text-align: center;';
        document.body.appendChild(msgDiv);
        setTimeout(() => {
            document.body.removeChild(msgDiv);
        }, 3000);
        return;
    }

    resultsDiv.innerHTML = '<h2>Search Results</h2><p>Loading...</p>';
    recsDiv.innerHTML = '';
    
    fetch(`/search?q=${encodeURIComponent(query)}`)
        .then(response => response.json())
        .then(data => {
            resultsDiv.innerHTML = '<h2>Search Results</h2>';
            if (data.results.length === 0) {
                resultsDiv.innerHTML += '<p>No songs found. Try a different query.</p>';
                return;
            }

            data.results.forEach(song => {
                const div = document.createElement('div');
                div.className = 'song';
                div.innerHTML = `
                    <div class="song-content">
                        ${song.album_cover_64x64 ? `<img src="${song.album_cover_64x64}" alt="Album cover" class="album-cover">` : ''}
                        <div class="song-info">
                            <strong>${song.track_name}</strong><br>
                            <small>by ${song.primary_artist_name}</small><br>
                            <small><em>${song.album_name || 'Unknown Album'}</em></small>
                        </div>
                        <button class="play-btn" onclick="playSong('${song.audio_url}', '${song.track_name}', this)">▶️ Play</button>
                        <button class="recommend-btn" data-track-id="${song.track_id}">🎵</button>
                    </div>
                `;
                resultsDiv.appendChild(div);
            });
        })
        .catch(err => {
            resultsDiv.innerHTML = '<h2>Search Results</h2><p>Error loading search results.</p>';
            console.error(err);
        });
});

resultsDiv.addEventListener('click', (event) => {
    if (event.target.classList.contains('recommend-btn')) {
        const trackId = event.target.dataset.trackId;
        console.log(`Getting recommendations for ${trackId}`);
        recsDiv.innerHTML = '<h2>Recommendations</h2><p>Loading recommendations...</p>';

        fetch('/recommend', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ track_id: trackId }),
        })
        .then(response => response.json())
        .then(data => {
            recsDiv.innerHTML = '<h2>Recommendations</h2>';
            if (data.recommendations.length === 0) {
                recsDiv.innerHTML += '<p>No recommendations found.</p>';
                return;
            }

            data.recommendations.forEach(song => {
                const div = document.createElement('div');
                div.className = 'song';
                const genres = song.genres ? song.genres.replace(/[\\[\\]']/g, '').split(', ').slice(0, 2).join(', ') : '';
                div.innerHTML = `
                    <div class="song-content">
                        ${song.album_cover_64x64 ? `<img src="${song.album_cover_64x64}" alt="Album cover" class="album-cover">` : ''}
                        <div class="song-info">
                            <strong>${song.track_name}</strong><br>
                            <small>by ${song.primary_artist_name}</small><br>
                            <small><em>${song.album_name || 'Unknown Album'}</em></small>
                            ${genres ? `<br><small class="genres">${genres}</small>` : ''}
                        </div>
                        <button class="play-btn" onclick="playSong('${song.audio_url}', '${song.track_name}', this)">▶️ Play</button>
                    </div>
                `;
                recsDiv.appendChild(div);
            });
        })
        .catch(err => {
            recsDiv.innerHTML = '<h2>Recommendations</h2><p>Error loading recommendations.</p>';
            console.error(err);
        });
    }
});

// Theme toggle functionality
themeToggleBtn.addEventListener('click', () => {
    document.body.classList.toggle('light-mode');
    const isLightMode = document.body.classList.contains('light-mode');
    themeToggleBtn.innerHTML = isLightMode ? '<i class="fas fa-sun"></i>' : '<i class="fas fa-moon"></i>';
});