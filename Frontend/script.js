// Sample data for demonstration - Updated with better image URLs
const trendingMovies = [
    { 
        title: "Dune: Part Two", 
        year: 2024, 
        poster: "images/dune 2.jpeg" 
    },
    { 
        title: "Oppenheimer", 
        year: 2023, 
        poster: "images/oppenheimer.jpeg" 
    },
    { 
        title: "Barbie", 
        year: 2023, 
        poster: "images/barbie.jpeg" 
    },
    { 
        title: "Poor Things", 
        year: 2023, 
        poster: "images/poor_things.jpeg"
    },
    { 
        title: "The Batman", 
        year: 2022, 
        poster: "images/the_batman.jpeg"
    },
    { 
        title: "Spider-Man: No Way Home", 
        year: 2021, 
        poster: "images/spider_man_no_way_home.jpeg"
    }
];

const popularPosters = [
    "images/dune.jpeg",
    "images/oppenheimer.jpeg",
    "images/barbie.jpeg",
    "images/poor_things.jpeg",
    "images/the_batman.jpeg",
    "images/spider_man_no_way_home.jpeg"
];

// DOM Elements
const randomPoster = document.getElementById('random-poster');
const searchBox = document.getElementById('search-box');
const searchBtn = document.getElementById('search-btn');
const inputText = document.getElementById('inputText');
const trendingMoviesContainer = document.getElementById('trending-movies');
const resultBox = document.getElementById('result');
const findMoviesBtn = document.getElementById('find-movies-btn');
const surpriseMeBtn = document.querySelector('.secondary-button');

// Initialize the page
function init() {
    // Set random poster
    setRandomPoster();
    
    // Load trending movies
    loadTrendingMovies();
    
    // Set up event listeners
    setupEventListeners();
}

// Set random poster with error handling
function setRandomPoster() {
    const randomIndex = Math.floor(Math.random() * popularPosters.length);
    randomPoster.src = popularPosters[randomIndex];
    
    // Add error handling in case images fail to load
    randomPoster.onerror = function() {
        this.src = 'https://images.unsplash.com/photo-1489599102910-59206b8ca314?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1200&h=600&q=80';
        console.log('Random poster image failed to load, using fallback');
    };
}

// Load trending movies with error handling
function loadTrendingMovies() {
    trendingMoviesContainer.innerHTML = '';
    
    trendingMovies.forEach(movie => {
        const movieCard = document.createElement('div');
        movieCard.className = 'movie-card';
        movieCard.innerHTML = `
            <img src="${movie.poster}" alt="${movie.title}" class="movie-poster" onerror="this.src='https://images.unsplash.com/photo-1489599102910-59206b8ca314?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=200&h=300&q=80'">
            <div class="movie-info">
                <h3 class="movie-title">${movie.title}</h3>
                <p class="movie-year">${movie.year}</p>
            </div>
        `;
        
        // Add click event to search for this movie
        movieCard.addEventListener('click', () => {
            inputText.value = `I want to watch a movie like ${movie.title}`;
            expandSearch();
            getRecommendations();
        });
        
        trendingMoviesContainer.appendChild(movieCard);
    });
}

// Set up event listeners
function setupEventListeners() {
    // Search button click
    searchBtn.addEventListener('click', function() {
        if (searchBox.classList.contains('compact')) {
            expandSearch();
        } else {
            getRecommendations();
        }
    });
    
    // Find Movies button click
    findMoviesBtn.addEventListener('click', getRecommendations);
    
    // Surprise Me button click
    surpriseMeBtn.addEventListener('click', surpriseMe);
    
    // Click outside to collapse search
    document.addEventListener('click', function(e) {
        if (searchBox.classList.contains('expanded') && 
            !searchBox.contains(e.target) && 
            e.target !== searchBtn &&
            e.target !== findMoviesBtn &&
            e.target !== surpriseMeBtn) {
            collapseSearch();
        }
    });
    
    // Prevent closing when clicking inside search box
    searchBox.addEventListener('click', function(e) {
        e.stopPropagation();
    });
    
    // Enter key to search
    inputText.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && searchBox.classList.contains('expanded')) {
            e.preventDefault();
            getRecommendations();
        }
    });
}

// Expand search box
function expandSearch() {
    searchBox.classList.remove('compact');
    searchBox.classList.add('expanded');
    inputText.focus();
}

// Collapse search box
function collapseSearch() {
    if (inputText.value.trim() === '') {
        searchBox.classList.remove('expanded');
        searchBox.classList.add('compact');
    }
}

// Surprise Me function
function surpriseMe() {
    const surpriseQueries = [
        "Recommend a movie that will surprise me",
        "I want to watch something unexpected",
        "Suggest a hidden gem movie",
        "Show me a film that will blow my mind",
        "Recommend a movie with a great plot twist",
        "I'm feeling adventurous, suggest something unique"
    ];
    
    const randomQuery = surpriseQueries[Math.floor(Math.random() * surpriseQueries.length)];
    inputText.value = randomQuery;
    
    // If search is compact, expand it
    if (searchBox.classList.contains('compact')) {
        expandSearch();
    }
    
    // Get recommendations
    getRecommendations();
}

// Get recommendations
async function getRecommendations() {
    const text = inputText.value;
    
    if (!text) {
        showError("Please describe the type of movie you want!");
        return;
    }

    try {
        showLoading();
        
        // Send request to backend
        const response = await axios.post('http://127.0.0.1:5000/recommend', { 
            text: text 
        }, {
            headers: {
                'Content-Type': 'application/json'
            },
            timeout: 30000
        });

        // Check if response has the expected data
        if (response.data && response.data.recommendations) {
            displayRecommendations(response.data.recommendations);
        } else {
            throw new Error('Invalid response format from server');
        }

    } catch (error) {
        console.error('API Error:', error);
        
        if (error.response) {
            showError(`Server error: ${error.response.status} - ${error.response.data.message || 'Please try again'}`);
        } else if (error.request) {
            showError('Network error: Could not connect to the server. Please check your connection.');
        } else {
            showError(`Error: ${error.message || 'Failed to get recommendations'}`);
        }
    }
}

// Show loading state
function showLoading() {
    resultBox.innerHTML = `
        <div class="loading">
            <i class="fas fa-spinner"></i> 
            <p>Finding the perfect movies for you...</p>
            <p class="loading-subtext">This may take a few moments</p>
        </div>
    `;
    resultBox.classList.add('show');
}

// Show error message
function showError(message) {
    resultBox.innerHTML = `
        <div class="error">
            <i class="fas fa-exclamation-triangle"></i>
            <p>${message}</p>
            <button onclick="getRecommendations()">Try Again</button>
        </div>
    `;
    resultBox.classList.add('show');
}

// Display recommendations
function displayRecommendations(recommendations) {
    resultBox.innerHTML = `
        <div class="recommendations-grid">
            ${recommendations.map(movie => `
                <div class="recommendation">
                    <div class="poster-container">
                        ${movie.poster ? 
                            `<img src="${movie.poster}" alt="${movie.title}" class="poster" onerror="this.src='https://images.unsplash.com/photo-1489599102910-59206b8ca314?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=300&h=450&q=80'">` : 
                            `<div class="no-poster">Poster not available</div>`
                        }
                    </div>
                    <div class="movie-details">
                        <h3>${movie.title} (${movie.year})</h3>
                        <p><strong>Description:</strong> ${movie.description}</p>
                        
                        <div class="metadata">
                            <p><strong>Genre:</strong> ${movie.genre}</p>
                            <p><strong>Director:</strong> ${movie.director}</p>
                            <p><strong>Cast:</strong> ${movie.actors}</p>
                            <p><strong>Year:</strong> ${movie.year}</p>
                            <p><strong>Runtime:</strong> ${movie.runtime} minutes</p>
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
        origin: { y: 0.6 },
        colors: ['#ff6b6b', '#4ecdc4', '#45aaf2', '#fd9644', '#a55eea']
    });
}

// Initialize the app when the page loads
document.addEventListener('DOMContentLoaded', init);