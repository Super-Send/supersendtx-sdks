package supersendtx_test

import (
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"

	supersendtx "github.com/Super-Send/supersendtx-sdks/go"
)

func TestNewRequiresStxPrefix(t *testing.T) {
	if _, err := supersendtx.New("bad"); err == nil {
		t.Fatal("expected error for invalid api key prefix")
	}
}

func TestEmailsSend(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Path != "/emails" || r.Method != http.MethodPost {
			t.Fatalf("unexpected request: %s %s", r.Method, r.URL.Path)
		}
		if got := r.Header.Get("Authorization"); got != "Bearer stx_test" {
			t.Fatalf("unexpected auth header: %q", got)
		}
		_ = json.NewEncoder(w).Encode(map[string]any{"id": "msg_1", "status": "sent"})
	}))
	defer server.Close()

	client, err := supersendtx.NewClient("stx_test", server.URL, server.Client())
	if err != nil {
		t.Fatal(err)
	}

	result, err := client.Emails.Send(map[string]any{
		"from":    "a@example.com",
		"to":      "b@example.com",
		"subject": "Hi",
		"html":    "<p>Hi</p>",
	})
	if err != nil {
		t.Fatal(err)
	}
	if result["id"] != "msg_1" {
		t.Fatalf("unexpected result: %#v", result)
	}
}

func TestErrorResponse(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusUnauthorized)
		_ = json.NewEncoder(w).Encode(map[string]any{"error": map[string]any{"message": "Invalid API key"}})
	}))
	defer server.Close()

	client, err := supersendtx.NewClient("stx_test", server.URL, server.Client())
	if err != nil {
		t.Fatal(err)
	}

	_, err = client.Emails.Send(map[string]any{
		"from":    "a@example.com",
		"to":      "b@example.com",
		"subject": "Hi",
		"html":    "<p>Hi</p>",
	})
	if err == nil {
		t.Fatal("expected error")
	}
	apiErr, ok := err.(*supersendtx.Error)
	if !ok {
		t.Fatalf("expected *supersendtx.Error, got %T", err)
	}
	if apiErr.Status != 401 || apiErr.Message != "Invalid API key" {
		t.Fatalf("unexpected error: %#v", apiErr)
	}
}
