# Custom Search Engine 🔍

A fully functional, **Flask-based Custom Search Engine** that fetches search results from Google, Bing, and Yahoo APIs. The results are stored in MySQL and reranked using intelligent metrics like **Mean Reciprocal Rank (MRR)** and **Mean Average Precision (MAP)** to ensure the most relevant results appear at the top.

---

## 🚀 Features

* ✅ Multi-API integration (Google, Bing, Yahoo)
* ⚙️ Custom ranking algorithms using:

  * Mean Reciprocal Rank (MRR)
  * Mean Average Precision (MAP)
  * Keyword length weighting
* 📂 MySQL database for caching and performance
* 🔎 Web UI built with HTML/CSS and Flask
* ⚖️ Designed to demonstrate backend + DSA skills

---

## 🧠 Why This Project?

> Built as a showcase of backend software development, real-world API integration, and core algorithmic thinking. Ideal for demonstrating to recruiters:
>
> * Data Structures & Algorithms skills
> * Python backend development
> * Flask application design
> * Custom relevance metrics
> * Modular, production-ready architecture

---

## 🧰 Tech Stack

| Component     | Technology          |
| ------------- | ------------------- |
| Language      | Python 3.x          |
| Framework     | Flask               |
| Database      | MySQL               |
| Algorithms    | MRR, MAP, TF        |
| Frontend      | HTML, CSS           |
| API Providers | Google, Bing, Yahoo |

---

## 📆 Project Structure

```
Custom-Search-Engine/
├── templates/
│   └── index.html
├── static/
│   └── style.css
├── app.py             # Flask app & routes
├── api_clients.py     # Handles API requests
├── ranking.py         # MRR, MAP ranking logic
├── db.py              # MySQL database logic
├── utils.py           # Tokenization, helpers
├── schema.sql         # DB schema
├── README.md
├── requirements.txt
```

---

## ⚡ How to Run

1. Clone the repository:

```bash
git clone https://github.com/Shreejit123-M/Custom-Search-Engine.git
cd Custom-Search-Engine
```

2. Set up dependencies:

```bash
pip install -r requirements.txt
```

3. Configure your `.env` file:

```
GOOGLE_API_KEY=your_key_here
BING_API_KEY=your_key_here
YAHOO_API_KEY=your_key_here
DB_HOST=localhost
DB_USER=root
DB_PASS=your_password
DB_NAME=custom_search
```

4. Set up the database:

```bash
mysql -u root -p custom_search < schema.sql
```

5. Run the app:

```bash
python app.py
```

6. Visit `http://127.0.0.1:5000` in your browser.

---

## 📊 Ranking Metrics

### Mean Reciprocal Rank (MRR)

Measures the rank position of the first relevant result:

```
MRR = 1 / rank_of_first_relevant_result
```

### Mean Average Precision (MAP)

Averages the precision at each relevant item over multiple queries.

### Keyword Weighting

Longer search queries get higher weight to boost specificity.

---

## 📈 Future Enhancements

* ⌛ Add caching layer (Redis or MySQL TTL)
* ⚖️ TF-IDF or BM25-based advanced scoring
* ✨ Result deduplication & fuzzy matching
* Ὄa Analytics dashboard for performance
* Ὂc Click feedback system for personalized ranking

---

## 👤 Author

**Shreejit Magadum**
📧 \[[Email](mailto:shreejitmagadum2003@gmail.com)]
👤 [LinkedIn Profile](https://www.linkedin.com/in/shreejitm)

---

## 📅 License

Licensed under the [MIT License](LICENSE).

---

## 🚧 Contributing

Contributions are welcome! Please open an issue or submit a pull request.

1. Fork the repo
2. Create your branch (`git checkout -b feature-name`)
3. Commit your changes
4. Push and create a pull request

---


