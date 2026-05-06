# Lab2Launch

Backend: uvicorn main:app --reload
Frontend: streamlit run frontend/app.py

python -c "import sqlite3; conn=sqlite3.connect('ideahack.db'); conn.execute('DELETE FROM users'); conn.commit(); conn.close(); print('Users table cleared')"
