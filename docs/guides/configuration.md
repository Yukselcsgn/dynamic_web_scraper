# Configuration Guide

Learn how to configure the Dynamic Web Scraper for your needs.

## Configuration File

The main configuration is in `config.json`:

```json
{
  "user_agents": [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
  ],
  "proxies": [
    "http://proxy1.example.com:8080"
  ],
  "use_proxy": true,
  "max_retries": 3,
  "retry_delay": 2,
  "rate_limiting": {
    "requests_per_minute": 60
  }
}
```

## Configuration Options

### Proxies

```json
{
  "use_proxy": true,
  "proxies": [
    "http://proxy1.example.com:8080",
    "socks5://proxy2.example.com:1080"
  ]
}
```

### User Agents

```json
{
  "user_agents": [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
  ]
}
```

### Rate Limiting

```json
{
  "rate_limiting": {
    "requests_per_minute": 60,
    "burst_limit": 10
  }
}
```

### Retry Logic

```json
{
  "max_retries": 3,
  "retry_delay": 2,
  "exponential_backoff": true
}
```

##Environment Variables

Override config with environment variables:

```bash
export SCRAPER_USE_PROXY=true
export SCRAPER_MAX_RETRIES=5
```

## Advanced Configuration

### Using Configuration Manager

```python
from scraper.customization.config_manager import ConfigManager

config_manager = ConfigManager("config.json")
config = config_manager.get_config()

# Modify settings
config_manager.set("max_retries", 5)
config_manager.save_config()
```

### Multiple Configurations

Create environment-specific configs:
- `config.dev.json` - Development
- `config.prod.json` - Production
- `config.test.json` - Testing

Load specific config:
```python
config_manager = ConfigManager("config.prod.json")
```

## Best Practices

1. **Never commit secrets** - Use environment variables
2. **Version your configs** - Track configuration changes
3. **Document custom settings** - Help future maintainers
4. **Test config changes** - Validate before deploying

## See Also

- [Anti-Bot Evasion Guide](anti-bot-evasion.md)
- [Plugin System Documentation](../architecture/plugins.md)
