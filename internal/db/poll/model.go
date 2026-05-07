package poll

type Poll struct {
	ID        int64    `json:"id"`
	Question  string   `json:"question"`
	CreatedAt string   `json:"created_at"`
	Options   []Option `json:"options"`
}

type Option struct {
	ID     int64  `json:"id"`
	PollID int64  `json:"poll_id"`
	Text   string `json:"text"`
}

type CreatePollInput struct {
	Question string   `json:"question"`
	Options  []string `json:"options"`
}
