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
            <h2>Recommended Movies :</h2>
            <div class="recommendations-grid">
                ${recommendations.map(movie => `
                    <div class="recommendation">
                      <div class="poster-container">
                        <h3>${movie.title} (${movie.metadata.Year})</h3>
                        ${movie.poster ? 
                            `<img src="${movie.poster}" alt="${movie.title}" class="poster">` : 
                            `<div class="no-poster">Poster not available</div>`
                        }
                      </div>   
                      <p>${movie.description}</p>

                        <div class="metadata">
                            <p><strong>Genre:</strong> ${movie.metadata.Genre}</p>
                            <p><strong>Director:</strong> ${movie.metadata.Director}</p>
                            <p><strong>Cast:</strong> ${movie.metadata.Actors}</p>
                            <p><strong>Rating:</strong> ${movie.metadata.Rating}/10</p>
                            <p><strong>Runtime:</strong> ${movie.metadata.Runtime} mins</p>
                            <p><strong>Similarity:</strong> ${(movie.similarity_score * 100).toFixed(1)}%</p>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;

        // Add animation to the result box
        gsap.fromTo(resultBox,
            { opacity: 0, y: 20 },
            { opacity: 1, y: 0, duration: 1, ease: "power2.out" }
        );

        // Trigger confetti animation
        confetti({
            particleCount: 100,
            spread: 70,
            origin: { y: 0.6 }
        });

    } catch (error) {
        resultBox.innerHTML = `<p class="error">Error getting recommendation. Please try again.</p>`;
        console.error('Error:', error);
    }
};