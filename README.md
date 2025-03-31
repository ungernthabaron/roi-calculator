![ROI Calculator](https://github.com/ungernthabaron/roi-calculator/blob/main/Logo.png)

# Instruction how to use: https://github.com/ungernthabaron/roi-calculator/wiki/How-to-use

# ROI Calculator

A Streamlit-based web application for calculating Return on Investment (ROI) for IT projects. The application allows customers to submit project proposals, project managers to estimate costs, and IT directors to approve projects based on ROI calculations.

## Features

- User authentication with different roles (Customer, Project Manager, IT Director)
- Project creation and management
- ROI calculation with detailed breakdowns
- Descartes Square analysis for project evaluation
- Modern and responsive UI
- Real-time updates and calculations

## Installation

1. Clone the repository:
```bash
git clone https://github.com/ungernthabaron/roi-calculator.git
cd roi-calculator
```

2. Create and activate a virtual environment:
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the application:
```bash
streamlit run main.py
```

2. Open your web browser and navigate to the URL shown in the terminal (typically http://localhost:8501)

3. Login with your credentials:
   - For customers: Create an account or use existing credentials
   - For Project Managers and IT Directors: Use the default password "Vbhjyjdf4?1"

## Project Structure

```
roi-calculator/
├── main.py              # Main application file
├── database.py          # Database operations
├── utils.py            # Utility functions
├── requirements.txt    # Project dependencies
├── .gitignore         # Git ignore file
└── README.md          # Project documentation
```

## Database

The application uses SQLite as its database. The database file will be created automatically when you first run the application.

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Streamlit for the amazing web framework
- SQLAlchemy for database operations
- Plotly for data visualization 
