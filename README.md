# OLX Parser

This Python project allows you to parse offers from OLX and create a web interface to view them.

## Features

- Offer Parsing: The project includes functionality to scrape and parse offers from OLX.
- Web Interface: It provides a user-friendly web interface to view the parsed offers.
- Query Builder: Choose OLX locale (.ro or .pl) and enter a search term instead of a full URL.
- Infinite Scrolling: Initial results load on search, with a "Load More" button to fetch additional pages dynamically.
- Truncated Descriptions: Long descriptions are shortened with a "See More" toggle for better readability.

## Installation

1. Clone the repository:

    ```shell
    git clone https://github.com/your-username/olx_parser.git
    ```

2. Install the required dependencies:

    ```shell
    pip install -r requirements.txt
    ```

## Usage

1. Run the following command to start the web interface:

    ```shell
    flask --app main run
    ```

2. Open your web browser and navigate to `http://localhost:5000` to access the web interface.
3. In the search form:
    - Select the OLX locale (.ro or .pl).
    - Enter your search term (e.g., "tricou napoli").
    - Optionally enable or disable sponsored offers, set sorting and price filters.
    - Click **Search** to view initial results.
    - Click **Load More** at the bottom to fetch more pages.

## Contributing

Contributions are welcome! If you have any ideas or improvements, please submit a pull request.
### Suggestions for future enhancements
- Add caching or rate-limiting to reduce repeated requests.
- Provide Docker and CI configuration for easier deployment and testing.
- Implement robust error handling and logging for production readiness.
- Add automated tests (unit and integration) and linters (flake8, black).

## Note

In the future, I'll probably host it on a server.

## License

This project is licensed under the [MIT License](LICENSE).
