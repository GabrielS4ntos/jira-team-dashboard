# Jira Sprint Dashboard

This project allows you to fetch all sprint tasks from the Jira Atlassian API and generate a dashboard to visualize them.

## Prerequisites

1. **Jira API Token**: Obtain an API token from your Jira account and access [this link](https://id.atlassian.com/manage-profile/security/api-tokens).

## Installation

1. Clone this repository:
    ```sh
    git clone https://github.com/joaovictor-aragao/jira-team-dashboard.git
    cd jira-team-dashboard
    ```

## Configuration

1. Create a folder and inside create a secrets file `.streamlit/secrets.toml` in the root directory and add your Jira credentials:
    ```plaintext
    JIRA_BASE_URL=https://your-domain.atlassian.net
    JIRA_EMAIL=your-email@example.com
    JIRA_API_TOKEN=your-api-token
    ```

## Usage

1. The `requirements.txt` file should list all Python libraries that your notebooks depend on, and they will be installed using:
    ```sh
    pip install -r requirements.txt
    ```

2. Run the script:
    ```sh
    streamlit run app/app.py
    ```

2. This will open the app in your browser to view the dashboard.

## Development

To contribute to this project, follow these steps:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes.
4. Commit your changes (`git commit -am 'Add some feature'`).
5. Push to the branch (`git push origin feature-branch`).
6. Create a new Pull Request.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

## Contact

For any questions or suggestions, please contact for [mail](mailto:j.victor0205@gmail.com).