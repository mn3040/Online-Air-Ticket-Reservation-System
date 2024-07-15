# Online Air Ticket Reservation System

This project is an online air ticket reservation system developed as part of the NYU Tandon School of Engineering's Intro to Databases (CS-UY 3083) course. The system allows customers to search for flights, purchase tickets, and view flight statuses, while airline staff can manage flights, airplanes, and view customer data.

## Features

- **Customer Features:**
  - Search for flights (one way or round trip) based on source/destination cities or airports.
  - Purchase flight tickets and view future and past flights.
  - Rate and comment on past flights.
  - Track spending over a specified period.

- **Airline Staff Features:**
  - Create, update, and manage flights and airplane details.
  - View and manage flight statuses.
  - View customer details and flight ratings.
  - Generate reports on frequent customers and revenue.

## Technologies Used

- **Backend:**
  - PHP: Handles the server-side logic.
  - MySQL: Manages the relational database.

- **Frontend:**
  - HTML/CSS: Structures and styles the web pages.
  - JavaScript: Adds interactivity to the web pages.

## Database Schema

The database schema was designed and normalized based on an Entity-Relationship (ER) diagram to support complex queries and ensure data integrity. It includes tables for customers, airline staff, flights, tickets, airplanes, and airports.

## Usage

- **Customer Operations:**
  - Register and log in as a customer.
  - Search for flights and purchase tickets.
  - View and manage your bookings.

- **Airline Staff Operations:**
  - Log in as an airline staff member.
  - Create and manage flight details.
  - View and update flight statuses.

## Security

- **User Authentication:** Implemented using PHP sessions to ensure secure login and session management.
- **Prepared Statements:** Used in PHP to prevent SQL injection attacks.
- **HTTPS:** Ensures encrypted data transmission.

## Contributing

Contributions are welcome! Please fork the repository and create a pull request with your changes.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Contact

For any inquiries or issues, please contact [Matthew Nunez](mailto:mn3040@nyu.edu).

