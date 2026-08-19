package ranla_test

import (
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"

	ranla "github.com/Super-Send/supersendtx-sdks/go/ranla"
)

func TestNewDefaultsToRanlaHost(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Path != "/emails" || r.Method != http.MethodPost {
			t.Fatalf("unexpected request: %s %s", r.Method, r.URL.Path)
		}
		if got := r.Header.Get("Authorization"); got != "Bearer rnl_test" {
			t.Fatalf("unexpected auth header: %q", got)
		}
		_ = json.NewEncoder(w).Encode(map[string]any{"id": "msg_1", "status": "sent"})
	}))
	defer server.Close()

	client, err := ranla.NewClient("rnl_test", server.URL, server.Client())
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

func TestNewUsesRanlaHostByDefault(t *testing.T) {
	if ranla.DefaultAPIBaseURL != "https://api.ranla.ai" {
		t.Fatalf("unexpected default host: %q", ranla.DefaultAPIBaseURL)
	}

	client, err := ranla.New("rnl_test")
	if err != nil {
		t.Fatal(err)
	}
	if client.BaseURL != ranla.DefaultAPIBaseURL {
		t.Fatalf("unexpected base url: %q", client.BaseURL)
	}
}

func TestNewRejectsInvalidPrefix(t *testing.T) {
	if _, err := ranla.New("bad"); err == nil {
		t.Fatal("expected error for invalid api key prefix")
	}
}
