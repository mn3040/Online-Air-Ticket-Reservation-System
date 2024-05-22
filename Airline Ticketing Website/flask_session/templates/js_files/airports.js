// Define the base URL for the API
const baseURL = 'http://127.0.0.1:5500';

document.getElementById('viewAirports').addEventListener('click', function(event) {
    event.preventDefault();
    fetch(`${baseURL}/airports`)
    .then(response => response.json())
    .then(data => {
        const mainContent = document.getElementById('main-content');
        mainContent.innerHTML = '<h2>List of Airports</h2>';
        data.forEach(airport => {
            mainContent.innerHTML += `<p>${airport.name}, ${airport.city}, ${airport.country}</p>`;
        });
    });
});