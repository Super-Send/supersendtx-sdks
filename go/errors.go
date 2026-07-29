package supersendtx

import "fmt"

type Error struct {
	Message    string
	Status     int
	Details    any
	Code       string
	UpgradeURL string
}

func (e *Error) Error() string {
	return e.Message
}

func ErrorFromResponse(status int, body map[string]any) *Error {
	message := fmt.Sprintf("Request failed with status %d", status)
	var details any
	code := ""
	upgradeURL := ""

	if errValue, ok := body["error"]; ok {
		switch typed := errValue.(type) {
		case string:
			message = typed
		case map[string]any:
			if msg, ok := typed["message"].(string); ok && msg != "" {
				message = msg
			}
			details = typed["details"]
			if c, ok := typed["code"].(string); ok {
				code = c
			}
			if u, ok := typed["upgrade_url"].(string); ok {
				upgradeURL = u
			}
		}
	}

	return &Error{
		Message:    message,
		Status:     status,
		Details:    details,
		Code:       code,
		UpgradeURL: upgradeURL,
	}
}
