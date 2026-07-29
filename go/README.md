# SuperSend TX Go SDK

Official Go client for the [SuperSend TX](https://supersendtx.com) transactional email API.

```bash
go get github.com/Super-Send/supersendtx-sdks/go@v0.8.2
```

```go
package main

import (
	"fmt"
	"log"

	supersendtx "github.com/Super-Send/supersendtx-sdks/go"
)

func main() {
	client, err := supersendtx.New("stx_your_key_here")
	if err != nil {
		log.Fatal(err)
	}

	result, err := client.Emails.Send(map[string]any{
		"from":    "you@yourdomain.com",
		"to":      "user@example.com",
		"subject": "Hello",
		"html":    "<p>It works.</p>",
	})
	if err != nil {
		log.Fatal(err)
	}

	fmt.Println(result["id"], result["status"])
}
```

Docs: https://docs.supersendtx.com/sdks/go
