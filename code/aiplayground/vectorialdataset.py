import psycopg2
from psycopg2 import sql
import os

# Create the connection for the database:
def create_connection(dbname, user, host, password):
    conn = psycopg2.connect("dbname='" + dbname + "' user='" + user + "' host='" + host + "' password='" + password + "'")
    return conn

# Get the groups from the database:
def get_groups():
    conn = create_connection(os.getenv("PG_DBNAME"), os.getenv("PG_USER"), os.getenv("PG_HOST"), os.getenv("PG_PASSWORD"))
    cur = conn.cursor()
    cur.execute("SELECT * FROM group_info")
    groups = cur.fetchall()
    cur.close()
    conn.close()
    return [{'group_name': group[0], 'group_display_name': group[1], 'group_description': group[2]} for group in groups]

# Get only group names from the database:
def get_group_names():
    conn = create_connection(os.getenv("PG_DBNAME"), os.getenv("PG_USER"), os.getenv("PG_HOST"), os.getenv("PG_PASSWORD"))
    cur = conn.cursor()
    cur.execute("SELECT group_name FROM group_info")
    groups = cur.fetchall()
    cur.close()
    conn.close()
    return [group[0] for group in groups]

# Get all the files in a group:
def get_filenames(group_name):
    conn = create_connection(os.getenv("PG_DBNAME"), os.getenv("PG_USER"), os.getenv("PG_HOST"), os.getenv("PG_PASSWORD"))
    cur = conn.cursor()

    # Clean the name to be a valid identified:
    table_name = ''.join(e for e in group_name if e.isalnum() or e == '_')
    table_name = table_name.lower()

    # Search for the document:
    cur.execute("SELECT DISTINCT filename FROM {}".format(table_name))
    files = cur.fetchall()
    cur.close()
    conn.close()
    return [file[0] for file in files]

# Create a new group in the database:
def create_group(name, description):
    conn = create_connection(os.getenv("PG_DBNAME"), os.getenv("PG_USER"), os.getenv("PG_HOST"), os.getenv("PG_PASSWORD"))
    cur = conn.cursor()

    # Clean the name to be a valid identified:
    table_name = ''.join(e for e in name if e.isalnum() or e == '_')
    table_name = table_name.lower()

    # Create the table:
    cur.execute(sql.SQL("CREATE EXTENSION IF NOT EXISTS vector;"))
    cur.execute(sql.SQL("CREATE TABLE IF NOT EXISTS {} ("
                                "id SERIAL PRIMARY KEY,"
                                "embedding vector NOT NULL,"
                                "text TEXT NOT NULL,"
                                "filename VARCHAR(255) NOT NULL,"
                                "created_at TIMESTAMPTZ NOT NULL DEFAULT now()"
                            ")").format(psycopg2.sql.Identifier(table_name)))
    
    # Insert the group info:
    cur.execute("INSERT INTO group_info (group_name, group_display_name, group_description) VALUES (%s, %s, %s)", (table_name, name, description))
    conn.commit()
    cur.close()
    conn.close()


# Upload a document to a group:
def upload_document(group_name, embeddings, text, filename):
    conn = create_connection(os.getenv("PG_DBNAME"), os.getenv("PG_USER"), os.getenv("PG_HOST"), os.getenv("PG_PASSWORD"))
    cur = conn.cursor()

    # Clean the name to be a valid identified:
    table_name = ''.join(e for e in group_name if e.isalnum() or e == '_')
    table_name = table_name.lower()

    # Insert the document:
    cur.execute("INSERT INTO {} (embedding, text, filename) VALUES (%s, %s, %s)".format(table_name), (embeddings, text, filename))
    conn.commit()
    cur.close()
    conn.close()

# Search for a document in a group:
def search_document(group_name, embeddings, limit=5):
    conn = create_connection(os.getenv("PG_DBNAME"), os.getenv("PG_USER"), os.getenv("PG_HOST"), os.getenv("PG_PASSWORD"))
    cur = conn.cursor()

    # Clean the name to be a valid identified:
    table_name = ''.join(e for e in group_name if e.isalnum() or e == '_')
    table_name = table_name.lower()

    # Search for the document:
    cur.execute("""
            SELECT text, created_at, filename, 1 - (embedding <=> %s::vector) AS cosine_similarity
            FROM {} 
            ORDER BY cosine_similarity desc
            LIMIT %s""".format(table_name), (embeddings, limit))
    results = []
    for document in cur.fetchall():
        results.append({'text': document[0], 'created_at' : document[1], 'filename' : document[2], 'cosine_similarity': document[3]})
    cur.close()
    conn.close()
    return results