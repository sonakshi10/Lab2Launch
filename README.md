# Lab2Launch

Backend: uvicorn main:app --reload

Alternative backend command: python backend/run.py
Frontend: streamlit run frontend/app.py

python -c "import sqlite3; conn=sqlite3.connect('ideahack.db'); conn.execute('DELETE FROM users'); conn.commit(); conn.close(); print('Users table cleared')"
