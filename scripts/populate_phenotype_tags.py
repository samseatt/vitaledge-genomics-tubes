import psycopg2

DB_CONFIG = {
    "dbname": "vitaledge_datalake",
    "user": "samseatt",
    "password": "password",
    "host": "localhost",
    "port": 5432
}

def add_phenotype_tags(tags):
    """
    Add a list of phenotype tags to the phenotype_tags table.
    - tags: List of tag strings to add.
    """
    try:
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Query to check if a tag exists
        check_query = "SELECT id FROM phenotype_tags WHERE name = %s;"

        # Query to insert a new tag
        insert_query = "INSERT INTO phenotype_tags (name) VALUES (%s) RETURNING id;"

        for tag in tags:
            # Check if the tag already exists
            cursor.execute(check_query, (tag,))
            result = cursor.fetchone()

            if result:
                tag_id = result[0]
                print(f"Tag '{tag}' already exists with ID {tag_id}.")
            else:
                # Insert the tag if it doesn't exist
                cursor.execute(insert_query, (tag,))
                tag_id = cursor.fetchone()[0]
                print(f"Tag '{tag}' added with ID {tag_id}.")

        # Commit the transaction
        conn.commit()

    except psycopg2.Error as e:
        print(f"Database error: {e}")
        if conn:
            conn.rollback()
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


if __name__ == "__main__":
    # Example list of tags to add
    tags_to_add = [
        "Mouth", 
        "Autoimmunity", 
        "Eyes", 
        "Sleep", 
        "Mind", 
        "Skin", 
        "Heart"
    ]

    add_phenotype_tags(tags_to_add)
