# ranla

Official Go client for the Ranla email API.

```bash
go get github.com/Super-Send/supersendtx-sdks/go/ranla@v0.8.4
```

```go
package main

import (
	"log"
	"os"

	ranla "github.com/Super-Send/supersendtx-sdks/go/ranla"
)

func main() {
	client, err := ranla.New(os.Getenv("RANLA_API_KEY"))
	if err != nil {
		log.Fatal(err)
	}

	result, err := client.Emails.Send(map[string]any{
		"from":    "ops@yourdomain.com",
		"to":      "user@example.com",
		"subject": "Your receipt",
		"html":    "<p>Thanks for your purchase.</p>",
	})
	if err != nil {
		log.Fatal(err)
	}
	log.Println(result["id"], result["status"])
}
```

Defaults to `https://api.ranla.ai`. API keys may start with `rnl_` or `stx_`.

The legacy `github.com/Super-Send/supersendtx-sdks/go` module remains supported.

## License

MIT
