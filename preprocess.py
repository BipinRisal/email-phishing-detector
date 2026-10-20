import re, html

def clean_text(t):
    t = html.unescape(str(t))
    t = re.sub(r"<[^>]+>", " ", t)
    t = re.sub(r"https?://\S+|www\.\S+", " URL ", t)
    t = re.sub(r"\S+@\S+", " EMAIL ", t)
    t = re.sub(r"\s+", " ", t).strip().lower()
    return t

def clean_v2(t):
    t = re.sub(r"\b(re|fw|fwd)\s*:\s*", " ", t)
    t = re.sub(r"\bwrote\b", " ", t)
    t = re.sub(r"\d+", " num ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t

def clean_model2(subject, body):
    s = str(subject) if subject else ""
    b = str(body) if body else ""
    t = s + " " + b
    t = t.replace("<|URL|>", " URL ")
    t = re.sub(r"\[+[A-Z_]+\]+", " ", t)
    return clean_v2(clean_text(t))
