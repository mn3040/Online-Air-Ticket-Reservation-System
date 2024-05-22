// Define the base URL for the API
const baseURL = 'http://127.0.0.1:5500';
document.getElementById('addAirplane').addEventListener('click', function(event) {
    event.preventDefault();
    const mainContent = document.getElementById('main-content');
    mainContent.innerHTML = `
        <h2>Add a New Airplane</h2>
        <form id="airplaneForm">
            <input type="text" id="airplane_id_number" placeholder="Airplane ID Number" required>
            <input type="text" id="airline_name" placeholder="Airline Name" required>
            <input type="text" id="num_seats" placeholder="Number of Seats" required>
            <input type="text" id="manufacturing_company" placeholder="Manufacturing Company" required>
            <input type="text" id="model_number" placeholder="Model Number" required>
            <input type="date" id="manufacturing_date" placeholder="Manufacturing Date" required>
            <button type="submit">Add Airplane</button>
        </form>
    `;
    document.getElementById('airplaneForm').addEventListener('submit', function(e) {
        e.preventDefault();
        const airplane_id_number = document.getElementById('airplane_id_number').value;
        const airline_name = document.getElementById('airline_name').value;
        const num_seats = document.getElementById('num_seats').value;
        const manufacturing_company = document.getElementById('manufacturing_company').value;
        const model_number = document.getElementById('model_number').value;
        const manufacturing_date = document.getElementById('manufacturing_date').value;
        fetch(`${baseURL}/airplanes`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({airplane_id_number, airline_name, num_seats, manufacturing_company, model_number, manufacturing_date})
        })
        .then(response => response.json())
        .then(data => alert('Airplane added successfully!'))
        .catch(error => alert('Error adding airplane: ' + error.message));
    });
});

