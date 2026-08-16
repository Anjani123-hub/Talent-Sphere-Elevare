import sqlite3

DB_NAME = "talentsphere.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def init_exam_db():

    conn = get_connection()
    cursor = conn.cursor()

    # Exams table
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS exams(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        subject TEXT,
        topic TEXT,
        difficulty TEXT,
        total_questions INTEGER,
        exam_date TEXT,
        start_time TEXT,
        end_time TEXT,
        created_by TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Questions table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS questions(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        exam_id INTEGER,
        question TEXT,
        option_a TEXT,
        option_b TEXT,
        option_c TEXT,
        option_d TEXT,
        correct_answer TEXT,
        FOREIGN KEY(exam_id) REFERENCES exams(id)
    )
    """)

    # Results table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS results(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        exam_id INTEGER,
        username TEXT,
        score INTEGER,
        total INTEGER,
        submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(exam_id) REFERENCES exams(id)
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS announcements(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        message TEXT,
        created_by TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()


def create_exam(
    title,
    subject,
    topic,
    difficulty,
    total_questions,
    exam_date,
    start_time,
    end_time,
    created_by,
):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
    """
    INSERT INTO exams(
        title,
        subject,
        topic,
        difficulty,
        total_questions,
        exam_date,
        start_time,
        end_time,
        created_by
    )
    VALUES(?,?,?,?,?,?,?,?,?)
    """,
    (
        title,
        subject,
        topic,
        difficulty,
        total_questions,
        exam_date,
        start_time,
        end_time,
        created_by,
    ),
    )

    exam_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return exam_id


def add_question(
    exam_id,
    question,
    a,
    b,
    c,
    d,
    answer,
):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO questions(
            exam_id,
            question,
            option_a,
            option_b,
            option_c,
            option_d,
            correct_answer
        )
        VALUES(?,?,?,?,?,?,?)
        """,
        (
            exam_id,
            question,
            a,
            b,
            c,
            d,
            answer,
        ),
    )

    conn.commit()
    conn.close()


def get_all_exams():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM exams ORDER BY id DESC")

    data = cursor.fetchall()

    conn.close()

    return data


def get_exam_questions(exam_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM questions
        WHERE exam_id=?
        """,
        (exam_id,),
    )

    data = cursor.fetchall()

    conn.close()

    return data


def save_result(
    exam_id,
    username,
    score,
    total,
):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO results(
            exam_id,
            username,
            score,
            total
        )
        VALUES(?,?,?,?)
        """,
        (
            exam_id,
            username,
            score,
            total,
        ),
    )

    conn.commit()
    conn.close()

def get_exam(exam_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM exams WHERE id=?",
        (exam_id,),
    )

    exam = cursor.fetchone()

    conn.close()

    return exam


def get_questions(exam_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            id,
            question,
            option_a,
            option_b,
            option_c,
            option_d,
            correct_answer
        FROM questions
        WHERE exam_id=?
        """,
        (exam_id,),
    )

    questions = cursor.fetchall()

    conn.close()

    return questions

def get_all_results():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT
        exams.title,
        results.username,
        results.score,
        results.total,
        results.submitted_at
    FROM results
    JOIN exams
    ON exams.id = results.exam_id
    ORDER BY results.submitted_at DESC
    """)

    data = cursor.fetchall()

    conn.close()

    return data

def get_student_results(username):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT
        exams.title,
        results.score,
        results.total,
        results.submitted_at
    FROM results
    JOIN exams
    ON exams.id = results.exam_id
    WHERE results.username=?
    ORDER BY results.submitted_at DESC
    """, (username,))

    data = cursor.fetchall()

    conn.close()

    return data

def add_announcement(title, message, created_by):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO announcements(
            title,
            message,
            created_by
        )
        VALUES(?,?,?)
        """,
        (
            title,
            message,
            created_by,
        ),
    )

    conn.commit()
    conn.close()


def get_announcements():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT *
    FROM announcements
    ORDER BY id DESC
    """)

    rows = cursor.fetchall()

    conn.close()

    return rows

from datetime import datetime, timedelta

def delete_expired_exams():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, exam_date, end_time
        FROM exams
    """)

    exams = cursor.fetchall()

    now = datetime.now()

    for exam in exams:

        exam_id = exam[0]
        exam_date = exam[1]
        end_time = exam[2]

        end_datetime = datetime.strptime(
            f"{exam_date} {end_time}",
            "%Y-%m-%d %H:%M:%S"
        )

        expiry = end_datetime + timedelta(hours=24)

        if now >= expiry:

            cursor.execute(
                "DELETE FROM questions WHERE exam_id=?",
                (exam_id,)
            )

            cursor.execute(
                "DELETE FROM results WHERE exam_id=?",
                (exam_id,)
            )

            cursor.execute(
                "DELETE FROM exams WHERE id=?",
                (exam_id,)
            )

    conn.commit()
    conn.close()