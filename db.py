# Module Imports
import mariadb
import sys
import logging

logger = logging.getLogger("firestorm_bot")
log_handler = logging.StreamHandler()
logger.addHandler(log_handler)
logger.setLevel(logging.INFO)

class DatasetEntry(object):
    def __init__(self, uid: int, pool: str, prompt: str, weight: int, sensitivity: str, flags: str):
        self.uid = uid
        self.pool = pool
        self.prompt = prompt
        self.weight = weight
        self.sensitivity = sensitivity
        self.flags = flags

class Db:
    """
    Wrapper around Database Operations
    """
    def __init__(self,
        password: str,
        host: str = "127.0.0.1",
        user: str = "root",
        port: int = 3306,
        database: str = "bingo-dataset"
    ):
        try:
            conn = mariadb.connect(
                user=user,
                password=password,
                host=host,
                port=port,
                database=database,
                reconnect=True

            )
            self.conn = conn
            self.cur = conn.cursor()
            logger.info(f"Successfully connected to {database}!")

            # Run migrations/database initializations
            with open('schema.sql', 'r', encoding='utf-8') as f:
                sql_script = f.read()
                self.cur.execute(sql_script)
                conn.commit()
                logger.info("Database successfully migrated.")
        except mariadb.Error as e:
            logger.error(f"DB error: {e}")
            sys.exit(1)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cur.close()
        self.conn.close()

    def add_prompt(self, pool: str, prompt: str, weight: int, sensitivity: str, flags: str):
        try:
            self.cur.execute(
                "INSERT INTO dataset (pool, prompt, weight, sensitivity, flags, approved) VALUES (?, ?, ?, ?, ?, ?)",
                (pool, prompt, weight, sensitivity, flags, False)
            )
            self.conn.commit()
            return True
        except mariadb.Error as e:
            logger.warning(f"Error adding prompt: {e}")
            return False

    def approve_prompt(self, uid: int):
        try:
            self.cur.execute("UPDATE dataset SET approved = 1 WHERE id = ?", (uid,))
            self.conn.commit()
            return True
        except mariadb.Error as e:
            logger.warning(f"Failed to approve {id}: {e}")
            return False

    def modify_prompt(self, uid: int, is_privileged_role: bool):
        """
        If privileged user, allow them to edit from dataset arbitrarily.
        If non-privileged user, only allow editing of unapproved entries.
        """
        try:
            self.cur.execute("UPDATE dataset SET prompt = ? WHERE id = ?", ("todo", uid,))
            self.conn.commit()
            return True
        except mariadb.Error as e:
            logger.warning(f"Failed to delete {id}: {e}")
            return False

    def delete_prompt(self, uid: int, is_privileged_role: bool):
        """
        If privileged user, allow them to delete from dataset arbitrarily.
        If non-privileged user, only allow deleting of unapproved entries.
        """
        try:
            self.cur.execute("DELETE FROM dataset WHERE id = ?", (uid,))
            self.conn.commit()
            return True
        except mariadb.Error as e:
            logger.warning(f"Failed to delete {id}: {e}")
            return False

    def get_pending_prompts(self):
        pass

    def get_pools(self):
        try:
            self.cur.execute("SELECT DISTINCT pool FROM dataset where approved = 1")
            for row in self.cur:
                print(row)
        except mariadb.Error as e:
            logger.warning(f"Error retrieving pools: {e}")

    def show_pool(self, pool: str):
        entries = []
        try:
            self.cur.execute("SELECT * FROM dataset WHERE pool = ? AND approved = 1", (pool,))
            for row in self.cur:
                entry = DatasetEntry(row[0], row[1], row[2], row[3], row[4], row[5])
                entries.append(entry)
        except mariadb.Error as e:
            logger.warning(f"Error showing pool {pool}: {e}")
        return entries
