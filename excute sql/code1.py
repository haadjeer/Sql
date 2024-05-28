import csv
import psycopg2

def execute_query(query):
    try:
        # Connect to your PostgreSQL database
        conn = psycopg2.connect(
            dbname="postgres",
            user="postgres",
            password="1234",
            host="localhost",
            port="5432"
        )

        # Create a cursor object using cursor() method
        cursor = conn.cursor()

        # Execute the SQL query
        cursor.execute(query)

        # Fetch all the rows
        rows = cursor.fetchall()

        return rows

    except Exception as e:
        print(f"Error: {e}")

    finally:
        # Close the cursor and connection
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def add_result_column(sql_filename, csv_filename):
    try:
        # Execute all SQL queries from the file
        with open(sql_filename, 'r') as file:
            queries = file.readlines()

        results = []
        for query in queries:
            # Execute each SQL query and store the results
            result = execute_query(query.strip())
            results.append(result)

        # Open the existing CSV file and create a new CSV file with the result column added
        with open(csv_filename, 'r', newline='') as csvfile:
            reader = csv.reader(csvfile)
            rows = list(reader)
            header = rows[0]
            header.append('Result')  # Add 'Result' column to the header

            # Add result values to each row
            for i in range(1, len(rows)):
                rows[i].append(results[i-1])

        # Write the updated CSV data to a new file
        with open('data(hadjer)_with_results.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(rows)

        print("Results added to CSV successfully.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Specify the filenames
    sql_filename = "sql.txt"
    csv_filename = "data(hadjer).csv"
    # Add result column to CSV
    add_result_column(sql_filename, csv_filename)
