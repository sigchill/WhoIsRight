package poll

import (
	"database/sql"
	"fmt"
)

type Store struct {
	db *sql.DB
}

func NewStore(db *sql.DB) *Store {
	return &Store{
		db: db,
	}
}

// store method to create a poll with options
func (s *Store) Create(input CreatePollInput) (*Poll, error) {

	tx, err := s.db.Begin()
	if err != nil {
		return nil, fmt.Errorf("begin tx : %w", err)
	}
	defer tx.Rollback()

	result, err := tx.Exec(
		"INSERT INTO polls (question) VALUES (?)",
		input.Question,
	)
	if err != nil {
		return nil, fmt.Errorf("insert poll tx : %w", err)
	}

	pollID, err := result.LastInsertId()
	if err != nil {
		return nil, fmt.Errorf("get poll id : %w", err)
	}

	options := make([]Option, len(input.Options))

	for _, text := range input.Options {
		res, err := tx.Exec(
			"INSERT INTO options (poll_id, text) VALUES (?,?)",
			pollID,
			text,
		)
		if err != nil {
			return nil, fmt.Errorf("insert option tx : %w", err)
		}
		optID, err := res.LastInsertId()
		if err != nil {
			return nil, fmt.Errorf("get option id : %w", err)
		}
		options = append(options, Option{
			ID:     optID,
			PollID: pollID,
			Text:   text,
		})
	}
	if err := tx.Commit(); err != nil {
		return nil, fmt.Errorf("commit tx : %w", err)
	}
	return s.GetByID(pollID)
}


func *s *Store) GetByID(id int64) (*Poll, error) {
	var p Poll

	err:= s.db.QueryRow(
		"SELECT id, question, created_at FROM polls WHERE id = ?",
		id,
	).Scan(&p.ID, &p.Question, &p.CreatedAt)
	if err != nil {
		return nil, fmt.Errorf("query poll : %w", err)
	}
	
	rows, err := s.db.Query(
		"SELECT id,poll_id, text FROM options WHERE poll_id = ?",
		id,
	)
	if err != nil {
		return nil, fmt.Errorf("query options : %w", err)
	}
	defer rows.Close()

	for rows.Next() {
		var opt Option
		if err := rows.Scan(&opt.ID, &opt.PollID, &opt.Text); err != nil {
			return nil, fmt.Errorf("scan option : %w", err)
		}
		p.Options = append(p.Options, opt)
	}
	return &p, nil
}