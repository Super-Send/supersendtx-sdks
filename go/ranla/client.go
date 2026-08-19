package ranla

import (
	"net/http"

	supersendtx "github.com/Super-Send/supersendtx-sdks/go"
)

// DefaultAPIBaseURL is the Ranla API host. The supersendtx module keeps api.supersendtx.com.
const DefaultAPIBaseURL = "https://api.ranla.ai"

type (
	Client = supersendtx.Client
	Error  = supersendtx.Error
)

// New builds a client with DefaultAPIBaseURL.
func New(apiKey string) (*Client, error) {
	return NewClient(apiKey, DefaultAPIBaseURL, nil)
}

// NewClient builds a client against an explicit base URL.
func NewClient(apiKey, baseURL string, httpClient *http.Client) (*Client, error) {
	return supersendtx.NewClient(apiKey, baseURL, httpClient)
}
