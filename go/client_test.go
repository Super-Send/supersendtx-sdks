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

func TestNewAcceptsRnlPrefix(t *testing.T) {
	client, err := supersendtx.New("rnl_test")
	if err != nil {
		t.Fatal(err)
	}
	if client.APIKey != "rnl_test" {
		t.Fatalf("unexpected api key: %q", client.APIKey)
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

// requestedURI runs one call against a stub server and returns the path and query it received.
func requestedURI(t *testing.T, call func(*supersendtx.Client) (map[string]any, error)) string {
	t.Helper()
	got := make(chan string, 1)
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		got <- r.URL.RequestURI()
		_ = json.NewEncoder(w).Encode(map[string]any{})
	}))
	defer server.Close()

	client, err := supersendtx.NewClient("stx_test", server.URL, server.Client())
	if err != nil {
		t.Fatal(err)
	}
	if _, err := call(client); err != nil {
		t.Fatal(err)
	}
	return <-got
}

func TestListQueryStrings(t *testing.T) {
	limit := 25
	inbound := true
	notInbound := false

	tests := []struct {
		name string
		call func(*supersendtx.Client) (map[string]any, error)
		want string
	}{
		{
			name: "domains without filters omits nil pointers",
			call: func(c *supersendtx.Client) (map[string]any, error) { return c.Domains.List(nil, "", nil) },
			want: "/domains",
		},
		{
			name: "domains dereferences limit and inbound_enabled",
			call: func(c *supersendtx.Client) (map[string]any, error) { return c.Domains.List(&limit, "cur_1", &inbound) },
			want: "/domains?cursor=cur_1&inbound_enabled=true&limit=25",
		},
		{
			name: "domains keeps inbound_enabled=false",
			call: func(c *supersendtx.Client) (map[string]any, error) { return c.Domains.List(nil, "", &notInbound) },
			want: "/domains?inbound_enabled=false",
		},
		{
			name: "emails",
			call: func(c *supersendtx.Client) (map[string]any, error) { return c.Emails.List(&limit, "") },
			want: "/emails?limit=25",
		},
		{
			name: "webhooks without filters",
			call: func(c *supersendtx.Client) (map[string]any, error) { return c.Webhooks.List(nil, "") },
			want: "/webhooks",
		},
		{
			name: "templates",
			call: func(c *supersendtx.Client) (map[string]any, error) { return c.Templates.List(nil, "", "published") },
			want: "/templates?status=published",
		},
		{
			name: "suppressions",
			call: func(c *supersendtx.Client) (map[string]any, error) {
				return c.Suppressions.List(&limit, "", "a@example.com")
			},
			want: "/suppressions?email=a%40example.com&limit=25",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := requestedURI(t, tt.call); got != tt.want {
				t.Fatalf("requested %q, want %q", got, tt.want)
			}
		})
	}
}

func TestEmailsSendAndBatchForwardCategory(t *testing.T) {
	bodies := make(chan map[string]any, 2)
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		var body map[string]any
		_ = json.NewDecoder(r.Body).Decode(&body)
		bodies <- body
		_ = json.NewEncoder(w).Encode(map[string]any{})
	}))
	defer server.Close()

	client, err := supersendtx.NewClient("stx_test", server.URL, server.Client())
	if err != nil {
		t.Fatal(err)
	}

	email := map[string]any{
		"from":        "a@example.com",
		"to":          "b@example.com",
		"subject":     "News",
		"html":        "<p>News</p>",
		"category":    "newsletter",
		"unsubscribe": false,
	}
	if _, err := client.Emails.Send(email); err != nil {
		t.Fatal(err)
	}
	if _, err := client.Emails.Batch([]map[string]any{email}); err != nil {
		t.Fatal(err)
	}

	sent := <-bodies
	batched := (<-bodies)["emails"].([]any)[0].(map[string]any)
	for _, body := range []map[string]any{sent, batched} {
		if body["category"] != "newsletter" || body["unsubscribe"] != false {
			t.Fatalf("category/unsubscribe not forwarded: %#v", body)
		}
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
