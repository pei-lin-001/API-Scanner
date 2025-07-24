"""
Enhanced GitHub Search Configuration for Large-Scale API Key Detection

This module provides comprehensive search configurations to maximize
the coverage of API key detection across GitHub repositories.
"""

# 大量编程语言和文件类型 - 确保最大覆盖率
ENHANCED_LANGUAGES = [
    # 主流编程语言
    "Python", "JavaScript", "TypeScript", "Java", "C#", "C++", "C", 
    "Go", "Rust", "PHP", "Ruby", "Swift", "Kotlin", "Scala",
    
    # Web开发语言
    "HTML", "CSS", "SCSS", "SASS", "Less", "Vue", "React",
    "Angular", "Svelte", "Astro",
    
    # 脚本和配置语言
    "Shell", "PowerShell", "Bash", "Zsh", "Fish",
    "Perl", "Lua", "R", "MATLAB", "Octave",
    
    # 移动开发
    "Objective-C", "Dart", "Flutter", 
    
    # 数据科学和AI
    "Jupyter Notebook", "Julia", "Mathematica",
    
    # 配置和数据格式
    "YAML", "JSON", "TOML", "XML", "INI", "Properties",
    "Dotenv", "Makefile", "Dockerfile", "Docker Compose",
    
    # 标记语言
    "Markdown", "reStructuredText", "AsciiDoc", "Org",
    
    # 数据库
    "SQL", "PLpgSQL", "TSQL", "MySQL", "PostgreSQL", "SQLite",
    "MongoDB", "CQL", "GraphQL",
    
    # 云和基础设施
    "Terraform", "HCL", "Ansible", "Puppet", "Chef",
    "Kubernetes", "Helm", "CloudFormation",
    
    # 其他重要语言
    "Haskell", "Erlang", "Elixir", "Clojure", "F#", "Elm",
    "Crystal", "Nim", "Zig", "Deno", "Bun",
    
    # 特殊文件类型
    "Text", "Plain Text", "Log", "Config", "Env"
]

# 扩展的文件路径模式 - 覆盖更多可能包含API密钥的文件
ENHANCED_PATHS = [
    # 配置文件路径
    "path:.env OR path:.envrc OR path:.env.local OR path:.env.dev OR path:.env.prod OR path:.env.staging OR path:.env.test",
    "path:.config OR path:.conf OR path:.cfg OR path:config OR path:configs OR path:configuration",
    "path:settings OR path:setting OR path:.settings OR path:options OR path:.options",
    
    # 密钥和认证文件
    "path:.secret OR path:.secrets OR path:secrets OR path:secret OR path:.private OR path:private",
    "path:.key OR path:.keys OR path:keys OR path:key OR path:.pem OR path:.p12 OR path:.pfx",
    "path:.credentials OR path:credentials OR path:credential OR path:.credential",
    "path:auth OR path:.auth OR path:authentication OR path:.authentication",
    "path:token OR path:tokens OR path:.token OR path:.tokens",
    
    # 项目配置文件
    "path:.yml OR path:.yaml OR path:*.yml OR path:*.yaml",
    "path:.toml OR path:*.toml OR path:pyproject.toml OR path:Cargo.toml",
    "path:.ini OR path:*.ini OR path:.properties OR path:*.properties",
    "path:.json OR path:*.json OR path:package.json OR path:composer.json",
    "path:.xml OR path:*.xml OR path:pom.xml OR path:web.xml",
    
    # Docker和容器配置
    "path:Dockerfile OR path:docker-compose.yml OR path:docker-compose.yaml OR path:.dockerignore",
    "path:kubernetes OR path:k8s OR path:helm OR path:charts",
    
    # CI/CD配置文件
    "path:.github OR path:.gitlab-ci.yml OR path:.travis.yml OR path:azure-pipelines.yml",
    "path:Jenkinsfile OR path:.circleci OR path:buildspec.yml OR path:appveyor.yml",
    
    # 云服务配置
    "path:terraform OR path:*.tf OR path:*.tfvars OR path:cloudformation",
    "path:ansible OR path:playbook OR path:*.ansible",
    "path:serverless.yml OR path:sam.yml OR path:template.yml",
    
    # 数据库配置
    "path:database.yml OR path:database.yaml OR path:db.yml OR path:db.yaml",
    "path:migration OR path:migrations OR path:schema OR path:seeds",
    
    # 开发和测试文件
    "path:.vscode OR path:.idea OR path:*.code-workspace",
    "path:test OR path:tests OR path:spec OR path:specs OR path:__tests__",
    "path:example OR path:examples OR path:sample OR path:samples OR path:demo OR path:demos",
    
    # 文档和注释文件
    "path:README OR path:readme OR path:CHANGELOG OR path:changelog",
    "path:docs OR path:doc OR path:documentation OR path:man",
    
    # 备份和临时文件
    "path:.backup OR path:.bak OR path:backup OR path:bak OR path:.tmp OR path:tmp",
    "path:.old OR path:old OR path:.orig OR path:orig OR path:.copy OR path:copy",
    
    # 日志文件
    "path:.log OR path:*.log OR path:logs OR path:log OR path:*.out OR path:*.err",
    
    # 脚本文件
    "path:scripts OR path:script OR path:bin OR path:tools OR path:utils OR path:utilities",
    "path:build OR path:dist OR path:release OR path:deploy OR path:deployment",
    
    # 各种杂项文件
    "path:*.txt OR path:*.md OR path:*.rst OR path:*.asciidoc",
    "path:*.sql OR path:*.db OR path:*.sqlite OR path:*.sqlite3",
    "path:*.cache OR path:*.pid OR path:*.lock OR path:*.sock"
]

# 增强的搜索关键词组合 - 提高API密钥检测率
ENHANCED_SEARCH_PATTERNS = [
    # API密钥相关词汇
    "api_key", "apikey", "api-key", "API_KEY", "APIKEY", "API-KEY",
    "secret_key", "secretkey", "secret-key", "SECRET_KEY", "SECRETKEY", "SECRET-KEY",
    "access_key", "accesskey", "access-key", "ACCESS_KEY", "ACCESSKEY", "ACCESS-KEY",
    "private_key", "privatekey", "private-key", "PRIVATE_KEY", "PRIVATEKEY", "PRIVATE-KEY",
    
    # 认证相关
    "auth_token", "authtoken", "auth-token", "AUTH_TOKEN", "AUTHTOKEN", "AUTH-TOKEN",
    "bearer_token", "bearertoken", "bearer-token", "BEARER_TOKEN", "BEARERTOKEN", "BEARER-TOKEN",
    "access_token", "accesstoken", "access-token", "ACCESS_TOKEN", "ACCESSTOKEN", "ACCESS-TOKEN",
    "refresh_token", "refreshtoken", "refresh-token", "REFRESH_TOKEN", "REFRESHTOKEN", "REFRESH-TOKEN",
    
    # 客户端相关
    "client_id", "clientid", "client-id", "CLIENT_ID", "CLIENTID", "CLIENT-ID",
    "client_secret", "clientsecret", "client-secret", "CLIENT_SECRET", "CLIENTSECRET", "CLIENT-SECRET",
    "app_id", "appid", "app-id", "APP_ID", "APPID", "APP-ID",
    "app_secret", "appsecret", "app-secret", "APP_SECRET", "APPSECRET", "APP-SECRET",
    
    # 数据库和服务连接
    "database_url", "database-url", "DATABASE_URL", "DATABASE-URL",
    "db_url", "db-url", "DB_URL", "DB-URL",
    "connection_string", "connection-string", "CONNECTION_STRING", "CONNECTION-STRING",
    "dsn", "DSN",
    
    # 服务特定关键词
    "webhook_secret", "webhook-secret", "WEBHOOK_SECRET", "WEBHOOK-SECRET",
    "signing_secret", "signing-secret", "SIGNING_SECRET", "SIGNING-SECRET",
    "encryption_key", "encryption-key", "ENCRYPTION_KEY", "ENCRYPTION-KEY",
    "jwt_secret", "jwt-secret", "JWT_SECRET", "JWT-SECRET",
    
    # 密码相关
    "password", "passwd", "pwd", "PASSWORD", "PASSWD", "PWD",
    "passphrase", "pass_phrase", "pass-phrase", "PASSPHRASE", "PASS_PHRASE", "PASS-PHRASE",
    
    # 证书和加密
    "certificate", "cert", "CERTIFICATE", "CERT",
    "private_pem", "private-pem", "PRIVATE_PEM", "PRIVATE-PEM",
    "public_key", "public-key", "PUBLIC_KEY", "PUBLIC-KEY",
    
    # 云服务特定
    "aws_access_key", "aws-access-key", "AWS_ACCESS_KEY", "AWS-ACCESS-KEY",
    "aws_secret_key", "aws-secret-key", "AWS_SECRET_KEY", "AWS-SECRET-KEY",
    "azure_client_secret", "azure-client-secret", "AZURE_CLIENT_SECRET", "AZURE-CLIENT-SECRET",
    "gcp_key", "gcp-key", "GCP_KEY", "GCP-KEY",
    
    # 第三方服务
    "stripe_key", "stripe-key", "STRIPE_KEY", "STRIPE-KEY",
    "paypal_secret", "paypal-secret", "PAYPAL_SECRET", "PAYPAL-SECRET",
    "twilio_token", "twilio-token", "TWILIO_TOKEN", "TWILIO-TOKEN",
    "slack_token", "slack-token", "SLACK_TOKEN", "SLACK-TOKEN",
    
    # 通用密钥指示词
    "token", "TOKEN", "key", "KEY", "secret", "SECRET",
    "credential", "credentials", "CREDENTIAL", "CREDENTIALS",
    "authorization", "AUTHORIZATION", "auth", "AUTH"
]

# 常见的敏感文件名模式
SENSITIVE_FILENAMES = [
    ".env", ".env.local", ".env.development", ".env.production", ".env.staging",
    ".envrc", ".environment", "env.js", "env.json", "env.yaml", "env.yml",
    "config.json", "config.yaml", "config.yml", "configuration.json",
    "settings.json", "settings.yaml", "settings.yml", "app.config",
    "secrets.json", "secrets.yaml", "secrets.yml", ".secrets",
    "credentials.json", "credentials.yaml", "credentials.yml", ".credentials",
    "keys.json", "keys.yaml", "keys.yml", ".keys", "api-keys.json",
    "tokens.json", "auth.json", "authentication.json", ".auth",
    "database.yml", "database.yaml", "db.yml", "db.json",
    "docker-compose.yml", "docker-compose.yaml", "Dockerfile"
]

# 组织特定的搜索模式 - 针对可能泄露密钥的代码模式
CODE_PATTERNS = [
    # 变量赋值模式
    "= \"sk-", "= 'sk-", "=\"sk-", "='sk-",
    "= \"AIzaSy", "= 'AIzaSy", "=\"AIzaSy", "='AIzaSy",
    
    # 环境变量模式
    "process.env.", "os.environ", "ENV[", "getenv(",
    "System.getenv", "Environment.GetEnvironmentVariable",
    
    # 配置对象模式
    "api_key:", "apiKey:", "secret:", "token:", "key:",
    "API_KEY:", "SECRET:", "TOKEN:", "KEY:",
    
    # 函数参数模式
    "api_key=", "apiKey=", "secret=", "token=", "key=",
    "API_KEY=", "SECRET=", "TOKEN=", "KEY=",
    
    # URL模式
    "https://", "http://", "mongodb://", "postgres://", "mysql://",
    "redis://", "ftp://", "sftp://", "ssh://",
    
    # Base64编码模式
    "base64", "Base64", "BASE64", "btoa", "atob"
]

def get_comprehensive_search_config():
    """
    获取全面的搜索配置
    
    Returns:
        dict: 包含所有搜索配置的字典
    """
    return {
        "languages": ENHANCED_LANGUAGES,
        "paths": ENHANCED_PATHS,
        "patterns": ENHANCED_SEARCH_PATTERNS,
        "filenames": SENSITIVE_FILENAMES,
        "code_patterns": CODE_PATTERNS
    } 