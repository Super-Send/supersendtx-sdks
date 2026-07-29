package supersendtx

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"strings"
)

const DefaultAPIBaseURL = "https://api.supersendtx.com"

type Client struct {
	APIKey     string
	BaseURL    string
	HTTPClient *http.Client

	Emails       EmailsService
	Domains      DomainsService
	Webhooks     WebhooksService
	Templates    TemplatesService
	Suppressions SuppressionsService
}

func New(apiKey string) (*Client, error) {
	return NewClient(apiKey, DefaultAPIBaseURL, nil)
}

func NewClient(apiKey, baseURL string, httpClient *http.Client) (*Client, error) {
	if !strings.HasPrefix(apiKey, "stx_") {
		return nil, fmt.Errorf("SuperSend TX API key must start with stx_")
	}
	if httpClient == nil {
		httpClient = http.DefaultClient
	}
	c := &Client{
		APIKey:     apiKey,
		BaseURL:    strings.TrimRight(baseURL, "/"),
		HTTPClient: httpClient,
	}
	c.Emails = EmailsService{client: c}
	c.Domains = DomainsService{client: c}
	c.Webhooks = WebhooksService{client: c}
	c.Templates = TemplatesService{client: c}
	c.Suppressions = SuppressionsService{client: c}
	return c, nil
}

func (c *Client) Request(method, path string, body any, headers map[string]string) (map[string]any, error) {
	var reader io.Reader
	if body != nil {
		payload, err := json.Marshal(body)
		if err != nil {
			return nil, err
		}
		reader = bytes.NewReader(payload)
	}

	req, err := http.NewRequest(method, c.BaseURL+path, reader)
	if err != nil {
		return nil, err
	}
	req.Header.Set("Authorization", "Bearer "+c.APIKey)
	req.Header.Set("Content-Type", "application/json")
	for key, value := range headers {
		req.Header.Set(key, value)
	}

	resp, err := c.HTTPClient.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	raw, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, err
	}

	if resp.StatusCode >= 400 {
		var parsed map[string]any
		_ = json.Unmarshal(raw, &parsed)
		return nil, ErrorFromResponse(resp.StatusCode, parsed)
	}

	if len(raw) == 0 {
		return map[string]any{}, nil
	}

	var out map[string]any
	if err := json.Unmarshal(raw, &out); err != nil {
		return nil, err
	}
	return out, nil
}

func queryString(params map[string]any) string {
	values := url.Values{}
	for key, value := range params {
		if value == nil {
			continue
		}
		values.Set(key, fmt.Sprint(value))
	}
	encoded := values.Encode()
	if encoded == "" {
		return ""
	}
	return "?" + encoded
}

type EmailsService struct{ client *Client }

func (s EmailsService) List(limit *int, cursor string) (map[string]any, error) {
	params := map[string]any{"limit": limit, "cursor": nilString(cursor)}
	return s.client.Request(http.MethodGet, "/emails"+queryString(params), nil, nil)
}

func (s EmailsService) Get(id string) (map[string]any, error) {
	return s.client.Request(http.MethodGet, "/emails/"+url.PathEscape(id), nil, nil)
}

func (s EmailsService) Send(body map[string]any) (map[string]any, error) {
	headers := map[string]string{}
	if key, ok := body["idempotency_key"].(string); ok && key != "" {
		headers["Idempotency-Key"] = key
	}
	if key, ok := body["idempotencyKey"].(string); ok && key != "" {
		headers["Idempotency-Key"] = key
	}
	return s.client.Request(http.MethodPost, "/emails", body, headers)
}

func (s EmailsService) Batch(emails []map[string]any) (map[string]any, error) {
	return s.client.Request(http.MethodPost, "/emails/batch", map[string]any{"emails": emails}, nil)
}

func (s EmailsService) Cancel(id string) (map[string]any, error) {
	return s.client.Request(http.MethodPatch, "/emails/"+url.PathEscape(id), map[string]any{"cancel": true}, nil)
}

func (s EmailsService) Resend(id string) (map[string]any, error) {
	return s.client.Request(http.MethodPost, "/emails/"+url.PathEscape(id)+"/resend", nil, nil)
}

func (s EmailsService) TestWebhook(body map[string]any) (map[string]any, error) {
	return s.client.Request(http.MethodPost, "/emails/test", body, nil)
}

func (s EmailsService) Insights(window string) (map[string]any, error) {
	if window == "" {
		window = "30d"
	}
	return s.client.Request(http.MethodGet, "/deliverability"+queryString(map[string]any{"window": window}), nil, nil)
}

type DomainsService struct{ client *Client }

func (s DomainsService) List(limit *int, cursor string, inboundEnabled *bool) (map[string]any, error) {
	params := map[string]any{"limit": limit, "cursor": nilString(cursor), "inbound_enabled": inboundEnabled}
	return s.client.Request(http.MethodGet, "/domains"+queryString(params), nil, nil)
}

func (s DomainsService) Get(idOrName string) (map[string]any, error) {
	return s.client.Request(http.MethodGet, "/domains/"+url.PathEscape(idOrName), nil, nil)
}

func (s DomainsService) Create(name string, inboundEnabled *bool) (map[string]any, error) {
	body := map[string]any{"name": name}
	if inboundEnabled != nil {
		body["inbound_enabled"] = *inboundEnabled
	}
	return s.client.Request(http.MethodPost, "/domains", body, nil)
}

func (s DomainsService) Verify(idOrName string) (map[string]any, error) {
	return s.client.Request(http.MethodPost, "/domains/"+url.PathEscape(idOrName), map[string]any{"action": "verify"}, nil)
}

func (s DomainsService) Apply(idOrName, provider string, credentials map[string]any) (map[string]any, error) {
	if provider == "" {
		provider = "cloudflare"
	}
	body := map[string]any{"action": "apply", "provider": provider}
	if credentials != nil {
		body["credentials"] = credentials
	}
	return s.client.Request(http.MethodPost, "/domains/"+url.PathEscape(idOrName), body, nil)
}

func (s DomainsService) Update(idOrName string, body map[string]any) (map[string]any, error) {
	return s.client.Request(http.MethodPatch, "/domains/"+url.PathEscape(idOrName), body, nil)
}

func (s DomainsService) Delete(idOrName string) (map[string]any, error) {
	return s.client.Request(http.MethodDelete, "/domains/"+url.PathEscape(idOrName), nil, nil)
}

type WebhooksService struct{ client *Client }

func (s WebhooksService) List(limit *int, cursor string) (map[string]any, error) {
	params := map[string]any{"limit": limit, "cursor": nilString(cursor)}
	return s.client.Request(http.MethodGet, "/webhooks"+queryString(params), nil, nil)
}

func (s WebhooksService) Get(id string) (map[string]any, error) {
	return s.client.Request(http.MethodGet, "/webhooks/"+url.PathEscape(id), nil, nil)
}

func (s WebhooksService) Create(body map[string]any) (map[string]any, error) {
	return s.client.Request(http.MethodPost, "/webhooks", body, nil)
}

func (s WebhooksService) Update(id string, body map[string]any) (map[string]any, error) {
	return s.client.Request(http.MethodPatch, "/webhooks/"+url.PathEscape(id), body, nil)
}

func (s WebhooksService) Delete(id string) (map[string]any, error) {
	return s.client.Request(http.MethodDelete, "/webhooks/"+url.PathEscape(id), nil, nil)
}

type TemplatesService struct{ client *Client }

func (s TemplatesService) List(limit *int, cursor, status string) (map[string]any, error) {
	params := map[string]any{"limit": limit, "cursor": nilString(cursor), "status": nilString(status)}
	return s.client.Request(http.MethodGet, "/templates"+queryString(params), nil, nil)
}

func (s TemplatesService) Get(idOrAlias string) (map[string]any, error) {
	return s.client.Request(http.MethodGet, "/templates/"+url.PathEscape(idOrAlias), nil, nil)
}

func (s TemplatesService) Create(body map[string]any) (map[string]any, error) {
	return s.client.Request(http.MethodPost, "/templates", body, nil)
}

func (s TemplatesService) Update(idOrAlias string, body map[string]any) (map[string]any, error) {
	return s.client.Request(http.MethodPatch, "/templates/"+url.PathEscape(idOrAlias), body, nil)
}

func (s TemplatesService) Delete(idOrAlias string) (map[string]any, error) {
	return s.client.Request(http.MethodDelete, "/templates/"+url.PathEscape(idOrAlias), nil, nil)
}

func (s TemplatesService) Publish(idOrAlias string) (map[string]any, error) {
	return s.client.Request(http.MethodPost, "/templates/"+url.PathEscape(idOrAlias), map[string]any{"action": "publish"}, nil)
}

type SuppressionsService struct{ client *Client }

func (s SuppressionsService) List(limit *int, cursor, email string) (map[string]any, error) {
	params := map[string]any{"limit": limit, "cursor": nilString(cursor), "email": nilString(email)}
	return s.client.Request(http.MethodGet, "/suppressions"+queryString(params), nil, nil)
}

func (s SuppressionsService) Create(body map[string]any) (map[string]any, error) {
	return s.client.Request(http.MethodPost, "/suppressions", body, nil)
}

func (s SuppressionsService) Remove(idOrEmail string) (map[string]any, error) {
	if strings.Contains(idOrEmail, "@") {
		return s.client.Request(http.MethodDelete, "/suppressions"+queryString(map[string]any{"email": idOrEmail}), nil, nil)
	}
	return s.client.Request(http.MethodDelete, "/suppressions/"+url.PathEscape(idOrEmail), nil, nil)
}

func nilString(value string) any {
	if value == "" {
		return nil
	}
	return value
}
