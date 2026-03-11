# NLP and Deep Learning Experiments

This repository contains Natural Language Processing (NLP) and Deep Learning experiments, including sentiment analysis models based on BERT using Hugging Face Transformers and PyTorch.

Because machine learning projects rely heavily on third-party dependencies, we actively monitor and mitigate vulnerabilities reported by automated security tools.

This repository follows secure dependency management practices to reduce risks such as:

- Remote Code Execution (RCE)
- Deserialization of untrusted data
- Regular Expression Denial of Service (ReDoS)
- Dependency-based attacks
- Arbitrary file write vulnerabilities
- Denial of Service (DoS)

---

## Security Policy

### Supported Versions

Only the latest dependency versions are guaranteed to receive security fixes.  
Users are encouraged to regularly update dependencies:

```bash
pip install --upgrade -r requirements.txt
```

| Version            | Supported |
|--------------------|-----------|
| Latest main branch | Yes       |
| Previous releases  | Limited   |
| Archived versions  | No        |

### Dependency Security Policy

This project uses **GitHub Dependabot** to detect vulnerable dependencies.

Key monitored packages include:

- Transformers
- PyTorch
- python-multipart
- FastAPI (if used)
- tokenizers

When a vulnerability is detected, the maintainers will:

1. Investigate the vulnerability report
2. Identify affected dependencies
3. Upgrade to a secure version
4. Update the `requirements.txt` file
5. Publish a security update

### Known Vulnerability Categories

#### 1. Deserialization of Untrusted Data

Some versions of Transformers and PyTorch allow unsafe deserialization when loading models.

**Risks**  
- Remote code execution  
- Malicious model execution  

**Mitigation**  
- Avoid loading models from untrusted sources  
- Use safe loading mechanisms  
- Restrict file input  

Example of safer loading:

```python
torch.load("model.pt", map_location="cpu")
```

Avoid loading unknown serialized objects.

#### 2. PyTorch Model Loading Risks

Unsafe model loading may lead to remote code execution.

**Mitigation**  
- Only load trusted model files  
- Avoid executing arbitrary pickled objects  
- Validate model sources  

Recommended usage:

```python
from transformers import AutoModel
model = AutoModel.from_pretrained("trusted-model")
```

#### 3. Regular Expression Denial of Service (ReDoS)

Some versions of Transformers contain vulnerable regex patterns that may cause catastrophic backtracking.

**Impact**  
- CPU exhaustion  
- Application slowdown  
- Denial of service  

**Mitigation**  
- Upgrade Transformers to patched versions  
- Avoid user-controlled regex inputs  

#### 4. Multipart Upload Vulnerabilities

The dependency `python-multipart` may allow:

- Arbitrary file writes  
- Denial of Service via malformed multipart/form-data boundaries  

**Mitigation**  
- Update dependency versions  
- Validate file uploads  
- Restrict file size  

Example:

```python
MAX_UPLOAD_SIZE = 5 * 1024 * 1024
```

### Security Best Practices for Contributors

All contributors must follow these practices.

#### 1. Dependency Updates

Before submitting a Pull Request:

```bash
pip list --outdated
```

Update dependencies when necessary.

#### 2. Safe Model Loading

Never load models from:

- unknown URLs
- unverified sources
- arbitrary uploaded files

#### 3. Input Validation

Always validate:

- user inputs
- file uploads
- API requests

#### 4. Avoid Hardcoded Secrets

Never include:

- API keys
- tokens
- passwords
- private datasets

Use environment variables instead.

### Reporting a Vulnerability

If you discover a security vulnerability, please report it responsibly.

**Preferred Method**  
Open a [Private Security Advisory](https://github.com/your-repo/security/advisories) in GitHub.  
Do **not** open a public issue for sensitive vulnerabilities.

**Include the Following Information**

- Description of the vulnerability
- Steps to reproduce
- Affected dependency
- Potential impact
- Suggested fix (if available)

**Response Timeline**

| Step               | Expected Time |
|--------------------|---------------|
| Initial response   | 48 hours      |
| Investigation      | 3–5 days      |
| Security patch     | 1–7 days      |

**Responsible Disclosure**

Please do not publicly disclose vulnerabilities until a fix has been released.  
Early disclosure may expose users to unnecessary risks.

### Automated Security Monitoring

This repository uses:

- GitHub Dependabot alerts
- Dependency security updates
- Continuous integration checks

These systems help automatically detect vulnerabilities in:

- Transformers
- PyTorch
- python-multipart

---
