# Lotto API with PostgreSQL Integration

This is a backend application for managing Lotto operations, built using FastAPI, BeautifulSoup4 and Panda. The application scrapes and mines data from four lottery companies, processes the information, and provides in excel(.XLSX) downloaded file. 
## Main Features

- **FastAPI**: High-performance Python framework for building APIs.
- **PostgreSQL**: Reliable and robust relational database management system.
- **Async Support**: Database operations using SQLAlchemy with async support.
- **Data Scraping**: Scrapes and mines lottery data from 4 different lottery companies.
- **Scalable Architecture**: Designed to handle large volumes of data.
- **Database Integration**: Can store scraped data in a PostgreSQL database for easy querying and analysis.
---

## Prerequisites

Make sure you have the following installed on your system:

- **Python 3.9+**: [Install Python](https://www.python.org/downloads/)
- **Git**: [Install Git](https://git-scm.com/downloads)

---

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/lotto-api.git
cd lotto-api
run `uvicorn index:app --reload` to start
