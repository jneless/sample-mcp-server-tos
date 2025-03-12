# Sample TOS Model Context Protocol Server

An MCP server implementation for retrieving data from TOS.

## Features
### Resources
Expose volcengine TOS Data through **Resources**. (think of these sort of like GET endpoints; they are used to load information into the LLM's context). Currently only **PDF** documents supported and limited to **1000** objects.


### Tools
- **ListBuckets**
  - Returns a list of all buckets owned by the authenticated sender of the request
- **ListObjectsV2**
  - Returns some or all (up to 1,000) of the objects in a bucket with each request
- **GetObject**
  - Retrieves an object from volcengine TOS. In the GetObject request, specify the full key name for the object. General purpose buckets - Both the virtual-hosted-style requests and the path-style requests are supported


## Configuration

### Setting up volcengine Credentials
1. Obtain volcengine access key ID, secret access key, and region from the volcengine Management Console and configure credentials files using **Default** profile
2. Ensure these credentials have appropriate permission READ/WRITE  permissions for TOS.

### Usage with Claude Desktop

#### Claude Desktop

On MacOS: `~/Library/Application\ Support/Claude/claude_desktop_config.json`
On Windows: `%APPDATA%/Claude/claude_desktop_config.json`

<details>
  <summary>Development/Unpublished Servers Configuration</summary>

```json
{
  "mcpServers": {
    "tos-mcp-server": {
      "command": "uv",
      "args": [
        "--directory",
        "/Users/user/generative_ai/model_context_protocol/tos-mcp-server",
        "run",
        "tos-mcp-server"
      ]
    }
  }
}
```

</details>

<details>
  <summary>Published Servers Configuration</summary>

```json
{
  "mcpServers": {
    "TOS-mcp-server": {
      "command": "uvx",
      "args": [
        "tos-mcp-server"
      ]
    }
  }
}
  ```
</details>

## Development

### Building and Publishing

To prepare the package for distribution:

1. Sync dependencies and update lockfile:
```bash
uv sync
```

2. Build package distributions:
```bash
uv build
```

This will create source and wheel distributions in the `dist/` directory.

3. Publish to PyPI:
```bash
uv publish
```

Note: You'll need to set PyPI credentials via environment variables or command flags:
- Token: `--token` or `UV_PUBLISH_TOKEN`
- Or username/password: `--username`/`UV_PUBLISH_USERNAME` and `--password`/`UV_PUBLISH_PASSWORD`

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.