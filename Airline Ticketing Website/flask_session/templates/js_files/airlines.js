// Define the base URL for the API
const baseURL = 'http://127.0.0.1:5500';

document.getElementById('viewAirlines').addEventListener('click', function(event) {
    event.preventDefault();
    fetch(`${baseURL}/airlines`)
    .then(response => response.json())
    .then(data => {
        const mainContent = document.getElementById('main-content');
        mainContent.innerHTML = '<h2>List of Airlines</h2>';
        data.forEach(airline => {
            mainContent.innerHTML += `<p>${airline.airline_name}</p>`;
        });
    });
});