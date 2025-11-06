import psycopg2

class Conexion:

    def __init__(self, dsn):
        self.dsn = dsn
        self.connection = psycopg2.connect(self.dsn)
        
    def conectar(self):
        if self.connection is None or self.connection.closed:
            try:
                self.connection = psycopg2.connect(self.dsn)
            except Exception as e:
                print(f"ERROR al conectar a la DB: {e}")
                raise

    def cur(self):
        self.conectar() 
        return self.connection.cursor()

    def commit(self):
        self.connection.commit()
    
    def rollback(self):
        self.connection.rollback()

    #Estoy probando conexiones para solucionar "cursor already closed"
    def close(self):
        if self.connection and not self.connection.closed:
            self.connection.close()
    
    def __enter__(self):
        self.conectar()
        self._cursor = self.connection.cursor()
        return self._cursor
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._cursor:
            self._cursor.close() 
        
        if exc_type is not None:
            self.rollback()
        else:
            self.commit()
        
        self._cursor = None
        return False
