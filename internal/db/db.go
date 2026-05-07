package db

import (
	"database/sql"
	"fmt"
	"os"

	_ "modernc.org/sqlite"
)

func Open(path string) (*sql.DB, error) {
	conn, err := sql.Open("sqlite", path)
	if err != nil {
		return nil, fmt.Errorf("open db : %w", err)
	}

	if err := conn.Ping(); err != nil {
		return nil, fmt.Errorf("Ping db : %w", err)
	}

	return conn, nil
}

func Migrate(conn *sql.DB, migrationFile string) error {

	sqlBytes, err := os.ReadFile(migrationFile)
	if err != nil {
		return fmt.Errorf("read file : %w", err)
	}
	if _, err := conn.Exec(string(sqlBytes)); err != nil {
		return fmt.Errorf("exec migration : %w", err)
	}
	return nil

}
