document.getElementById('recommend-btn').onclick = async function () {
    const text = document.getElementById('inputText').value;
    const resultBox = document.getElementById('result');

    if (!text) {
        alert("Please describe the type of movie you want!");
        return;
    }

    try {
        // Show loading animation
        resultBox.innerHTML = `
            <div class="loading">
                <i class="fas fa-spinner"></i> Loading...
            </div>
        `;
        resultBox.classList.add('show');

        // Send request to backend
        const response = await axios.post('http://127.0.0.1:5000/recommend', { text });

        // Display the recommendations
        const recommendations = response.data.recommendations;
        resultBox.innerHTML = `
            <h2>Recommended Movies</h2>
            <div class="recommendations-grid">
                ${recommendations.map(movie => `
                    <div class="recommendation">
                        <div class="poster-container">
                            <h3>${movie.title} (${movie.year})</h3>
                            ${movie.poster ? 
                                `<img src="${movie.poster}" alt="${movie.title}" class="poster">` : 
                                `<div class="no-poster">Poster not available</div>`
                            }
                        </div>
                        <div class="movie-details">
                            <p><strong>Description:</strong> ${movie.description}</p>
                            
                            <div class="metadata">
                                <p><strong>Genre:</strong> ${movie.genre}</p>
                                <p><strong>Director:</strong> ${movie.director}</p>
                                <p><strong>Cast:</strong> ${movie.actors}</p> <!-- Added Cast -->
                                <p><strong>Year:</strong> ${movie.year}</p>
                                <p><strong>Runtime:</strong> ${movie.runtime} minutes</p> <!-- Fixed Runtime -->
                                <p><strong>Rating:</strong> ${movie.rating}/10</p>
                                <p><strong>Votes:</strong> ${movie.votes}</p>
                                <p><strong>Revenue:</strong> $${movie.revenue} million</p>
                                <p><strong>Metascore:</strong> ${movie.metascore}</p>
                            </div>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;

        // Animation
        gsap.from(".recommendation", { 
            opacity: 0, 
            y: 20, 
            duration: 0.8, 
            stagger: 0.1 
        });

        // Confetti
        confetti({
            particleCount: 100,
            spread: 70,
            origin: { y: 0.6 }
        });

    } catch (error) {
        resultBox.innerHTML = `
            <div class="error">
                <i class="fas fa-exclamation-triangle"></i>
                <p>Error: ${error.message || 'Failed to get recommendations'}</p>
            </div>
        `;
        console.error('Error:', error);
    }
};