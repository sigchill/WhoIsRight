package main

import (
	"fmt"
	"log"
	"net/http"

	"github.com/go-chi/chi/v5"
	"github.com/go-chi/chi/v5/middleware"
	"github.com/sigschill/whoisright/internal/db"
)

func main() {

	conn, err := db.Open("pollgame.db")
	if err != nil {
		log.Fatal(err)
	}
	defer conn.Close()

	if err := db.Migrate(conn, "internal/db/migrations/001_init.sql"); err != nil {
		log.Fatal(err)
	}

	r := chi.NewRouter()

	r.Use(middleware.Logger)

	r.Get("/", func(w http.ResponseWriter, r *http.Request) {
		fmt.Fprintln(w, " welcome to pollgame")
	})

	log.Println("server starting at :8080")

	if err := http.ListenAndServe(":8080", r); err != nil {
		log.Fatal(err)
	}

}
