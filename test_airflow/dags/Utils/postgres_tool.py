import psycopg2
from tabulate import tabulate
import pandas as pd
import emoji
from tqdm import tqdm
from Utils.logger import logger


class PostgresTool():
    
    def __init__(self, host, user, port, password, database):
        self.host = host
        self.user = user
        self.port = port
        self.password = password
        self.database = database

        self.conn = psycopg2.connect(
            host=host,
            database=database,
            user=user,
            port=port,
            password=password
        )
        self.conn.autocommit = False
        self.cur = self.conn.cursor()
    
    def close(self):
        self.cur.close()
        self.conn.close()

    def query(self, sql_query, show=True):
        try:
            self.cur.execute(sql_query)
            if sql_query.strip().upper().startswith("SELECT"):
                if show:
                    rows = self.cur.fetchall()
                    print(tabulate(rows, headers=[desc[0] for desc in self.cur.description], tablefmt='psql'))
                else:
                    return self.cur.fetchall()
            # For non-SELECT queries, you may want to commit the transaction here
            # if the query is an INSERT, UPDATE, or DELETE
            if not sql_query.strip().upper().startswith("SELECT"):
                self.conn.commit()
        except Exception as e:
            logger.error(f"Có lỗi xảy ra: {e}")
            self.conn.rollback()


    def get_columns(self, table_name):
        query = f"""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = '{table_name}'
        """
        self.cur.execute(query)
        columns = [row[0] for row in self.cur.fetchall()]
        return columns

    def get_all_table(self,):
        self.cur.execute("ROLLBACK")
        self.cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_type = 'BASE TABLE'")
        tables = [i[0] for i in self.cur.fetchall()]
        return tables
    
    def insert_from_dataframe(self, df, table_name):
        """Insert data from a DataFrame into a specified table in PostgreSQL, handling UUIDs and conflicts."""
        try:
            if df.empty:
                logger(f'./logs/insert_{table_name}.log', emoji.emojize(f":cross_mark: DataFrame is empty, nothing to insert into {table_name}."))
                return

            list_columns = list(df.columns)
            primary_keys = {
                "Emails": "email_id",
                "Addresses": "address_id",
                "EmailAddresses": None 
            }
            primary_key = primary_keys.get(table_name)

            columns = ', '.join([f'"{col}"' for col in list_columns])
            values = ', '.join(['%s' for _ in list_columns])
            updates = ', '.join([f'"{col}" = EXCLUDED."{col}"' for col in list_columns])

            if primary_key:
                conflict_target = f'"{primary_key}"'
                insert_stmt = f"""
                    INSERT INTO "{table_name}" ({columns})
                    VALUES ({values})
                    ON CONFLICT ({conflict_target})
                    DO UPDATE SET {updates};
                """
            else:
                insert_stmt = f"""
                    INSERT INTO "{table_name}" ({columns})
                    VALUES ({values})
                    ON CONFLICT DO NOTHING;
                """

            data = [tuple(row) for row in df.itertuples(index=False, name=None)]
            self.cur.executemany(insert_stmt, data)
            self.conn.commit()
            logger(f'./logs/insert_{table_name}.log', emoji.emojize(f":check_mark_button: {table_name} Data batch inserted successfully! :check_mark_button:"))

        except Exception as e:
            self.conn.rollback()
            error_message = f":cross_mark: Error inserting data from DataFrame into {table_name}: {str(e)}"
            logger(f'./logs/insert_{table_name}.log', emoji.emojize(error_message))
