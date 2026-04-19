"""
analyser.py — Resume Analysis Engine
All keyword matching, scoring, and feedback logic lives here.
"""

import re
from collections import Counter


# ─────────────────────────────────────────────────────────
# JOB ROLE SKILL DICTIONARIES
# ─────────────────────────────────────────────────────────
JOB_PROFILES = {
    "Software Developer (SDE)": {
        "required": [
            "java", "python", "c++", "data structures", "algorithms",
            "sql", "git", "oop", "rest api", "system design"
        ],
        "bonus": [
            "aws", "docker", "kubernetes", "ci/cd", "microservices",
            "typescript", "agile", "redis", "kafka"
        ],
    },
    "Machine Learning Engineer": {
        "required": [
            "python", "machine learning", "tensorflow", "pytorch",
            "numpy", "pandas", "scikit-learn", "statistics",
            "deep learning", "sql"
        ],
        "bonus": [
            "nlp", "computer vision", "mlops", "spark",
            "huggingface", "model deployment", "feature engineering",
            "airflow", "docker"
        ],
    },
    "Data Analyst": {
        "required": [
            "sql", "excel", "python", "tableau", "power bi",
            "statistics", "data cleaning", "visualization", "pandas", "r"
        ],
        "bonus": [
            "machine learning", "spark", "airflow", "bigquery",
            "looker", "etl", "storytelling", "powerpoint"
        ],
    },
    "Web Developer": {
        "required": [
            "html", "css", "javascript", "react", "node.js",
            "git", "rest api", "responsive design", "typescript", "mongodb"
        ],
        "bonus": [
            "next.js", "vue", "postgresql", "docker",
            "figma", "testing", "graphql", "tailwind"
        ],
    },
    "DevOps Engineer": {
        "required": [
            "linux", "docker", "kubernetes", "ci/cd",
            "jenkins", "git", "aws", "terraform", "bash", "networking"
        ],
        "bonus": [
            "ansible", "prometheus", "grafana", "helm",
            "azure", "gcp", "security", "python"
        ],
    },
    "Android Developer": {
        "required": [
            "java", "kotlin", "android", "xml", "firebase",
            "git", "rest api", "sqlite", "mvvm", "jetpack"
        ],
        "bonus": [
            "flutter", "dart", "room", "retrofit",
            "coroutines", "hilt", "compose", "unit testing"
        ],
    },
    "Cybersecurity Analyst": {
        "required": [
            "networking", "linux", "python", "firewalls", "sql",
            "penetration testing", "cryptography", "git", "siem", "nmap"
        ],
        "bonus": [
            "ethical hacking", "kali linux", "metasploit", "wireshark",
            "splunk", "aws", "incident response", "risk assessment"
        ],
    },
}

# ─────────────────────────────────────────────────────────
# PATTERNS
# ─────────────────────────────────────────────────────────
SECTION_PATTERNS = {
    "Contact Info":     re.compile(r"\b(email|phone|linkedin|github|@|\.com|\+\d{7,})\b", re.I),
    "Education":        re.compile(r"\b(b\.?tech|m\.?tech|bca|mca|bachelor|master|degree|university|college|cgpa|gpa)\b", re.I),
    "Work Experience":  re.compile(r"\b(intern|experience|worked|employed|company|ltd|pvt|inc|role|position)\b", re.I),
    "Skills":           re.compile(r"\b(skills|technologies|tools|proficient|expertise|competencies)\b", re.I),
    "Projects":         re.compile(r"\b(project|built|developed|created|implemented|deployed)\b", re.I),
    "Certifications":   re.compile(r"\b(certif|certification|course|training|google|microsoft|udemy|coursera|nptel)\b", re.I),
    "Achievements":     re.compile(r"\b(award|rank|winner|achievement|hackathon|topper|merit)\b", re.I),
}

IMPACT_VERBS = [
    "improved", "reduced", "increased", "optimised", "optimized",
    "developed", "built", "automated", "deployed", "led", "achieved",
    "delivered", "created", "designed", "implemented", "boosted",
    "streamlined", "scaled", "launched", "managed", "migrated",
    "refactored", "enhanced", "coordinated", "collaborated"
]

WEAK_PHRASES = [
    "worked on", "responsible for", "helped with",
    "assisted", "involved in", "participated in",
    "was part of", "contributed to"
]

EMAIL_RE    = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-z]{2,}")
PHONE_RE    = re.compile(r"(\+\d[\d\s\-]{8,}|\b\d{10}\b)")
LINKEDIN_RE = re.compile(r"linkedin\.com/in/\S+", re.I)
GITHUB_RE   = re.compile(r"github\.com/\S+", re.I)
QUANT_RE    = re.compile(
    r"\d+\s*%|\d+\s*x\b|\$\d+|₹\d+|\d+\s*(users|clients|requests|records|hours|days|months|projects|employees|members|teams?)",
    re.I
)


# ─────────────────────────────────────────────────────────
# MAIN ANALYSER CLASS
# ─────────────────────────────────────────────────────────
class ResumeAnalyser:
    def __init__(self, text: str, role: str):
        self.raw_text   = text
        self.text       = text.lower()
        self.role       = role
        self.profile    = JOB_PROFILES[role]
        self.word_count = len(text.split())

    def run(self) -> dict:
        contact  = self._extract_contact()
        sections = self._detect_sections()
        skills   = self._match_skills()
        content  = self._evaluate_content()
        scores   = self._compute_scores(contact, sections, skills, content)
        feedback = self._generate_feedback(contact, sections, skills, content, scores)
        keywords = self._top_keywords()

        return {
            "scores":    scores,
            "contact":   contact,
            "sections":  sections,
            "skills":    skills,
            "content":   content,
            "feedback":  feedback,
            "keywords":  keywords,
            "word_count": self.word_count,
        }

    # ── Contact ──────────────────────────────
    def _extract_contact(self):
        return {
            "Email":    bool(EMAIL_RE.search(self.raw_text)),
            "Phone":    bool(PHONE_RE.search(self.raw_text)),
            "LinkedIn": bool(LINKEDIN_RE.search(self.raw_text)),
            "GitHub":   bool(GITHUB_RE.search(self.raw_text)),
        }

    # ── Sections ─────────────────────────────
    def _detect_sections(self):
        return {
            sec: bool(rx.search(self.raw_text))
            for sec, rx in SECTION_PATTERNS.items()
        }

    # ── Skills ───────────────────────────────
    def _match_skills(self):
        found_req   = [s for s in self.profile["required"] if s in self.text]
        missing_req = [s for s in self.profile["required"] if s not in self.text]
        found_bonus = [s for s in self.profile["bonus"]    if s in self.text]
        return {
            "total_required":  len(self.profile["required"]),
            "found_required":  found_req,
            "missing_required": missing_req,
            "found_bonus":     found_bonus,
            "match_pct":       round(len(found_req) / len(self.profile["required"]) * 100),
        }

    # ── Content quality ──────────────────────
    def _evaluate_content(self):
        return {
            "impact_verbs":    [v for v in IMPACT_VERBS  if v in self.text],
            "weak_phrases":    [p for p in WEAK_PHRASES  if p in self.text],
            "quantifications": len(QUANT_RE.findall(self.raw_text)),
        }

    # ── Scoring ──────────────────────────────
    def _compute_scores(self, contact, sections, skills, content):
        # Skills — 40 pts
        skill_score = round(
            (len(skills["found_required"]) / skills["total_required"]) * 35 +
            min(len(skills["found_bonus"]), 5) / 5 * 5
        )

        # Sections — 25 pts
        sec_count     = sum(sections.values())
        section_score = round((sec_count / len(sections)) * 25)

        # Content quality — 20 pts
        impact_pts  = min(len(content["impact_verbs"])  * 2, 10)
        quant_pts   = min(content["quantifications"]    * 3, 8)
        weak_pen    = min(len(content["weak_phrases"])  * 2, 6)
        content_score = max(0, min(impact_pts + quant_pts - weak_pen, 20))

        # Contact — 10 pts
        contact_score = (
            (4 if contact["Email"]    else 0) +
            (3 if contact["Phone"]    else 0) +
            (2 if contact["LinkedIn"] else 0) +
            (1 if contact["GitHub"]   else 0)
        )

        # Length — 5 pts
        wc = self.word_count
        length_score = 5 if 200 <= wc <= 700 else (3 if 100 <= wc < 200 or wc > 700 else 1)

        total = min(100, skill_score + section_score + content_score + contact_score + length_score)
        grade = "A" if total >= 85 else "B" if total >= 70 else "C" if total >= 55 else "D" if total >= 40 else "F"

        return {
            "total": total,
            "grade": grade,
            "breakdown": {
                "Skills":          {"score": skill_score,    "max": 40},
                "Sections":        {"score": section_score,  "max": 25},
                "Content Quality": {"score": content_score,  "max": 20},
                "Contact Info":    {"score": contact_score,  "max": 10},
                "Length":          {"score": length_score,   "max": 5},
            }
        }

    # ── Feedback ─────────────────────────────
    def _generate_feedback(self, contact, sections, skills, content, scores):
        tips = []

        if not contact["Email"]:
            tips.append(("🔴 Critical", "No email address found. Add it at the top of your resume."))
        if not contact["Phone"]:
            tips.append(("🟡 Warning", "Phone number missing. Recruiters need this to contact you."))
        if not contact["LinkedIn"]:
            tips.append(("🟡 Warning", "LinkedIn profile URL not found. It boosts your credibility."))
        if not contact["GitHub"] and self.role in ("Software Developer (SDE)", "Web Developer", "Machine Learning Engineer", "DevOps Engineer"):
            tips.append(("🟡 Warning", "GitHub link not found. Highly recommended for technical roles."))

        if not sections["Projects"]:
            tips.append(("🔴 Critical", "Projects section not found. This is essential for freshers."))
        if not sections["Education"]:
            tips.append(("🔴 Critical", "Education section not clearly found. Make sure it's present."))
        if not sections["Certifications"]:
            tips.append(("🟡 Warning", "No certifications detected. Add relevant online courses or certifications."))
        if not sections["Achievements"]:
            tips.append(("🔵 Tip", "Consider adding an Achievements section — hackathons, ranks, awards."))

        if skills["missing_required"]:
            tips.append(("🟡 Warning", f"Missing key skills: **{', '.join(skills['missing_required'][:5])}**. Add them if you know them."))
        if skills["match_pct"] < 50:
            tips.append(("🔴 Critical", f"Only {skills['match_pct']}% of required skills matched. Tailor your resume to the job."))

        if content["quantifications"] == 0:
            tips.append(("🔴 Critical", "No quantified achievements found. Add numbers like 'improved speed by 40%' or 'served 10,000 users'."))
        elif content["quantifications"] < 3:
            tips.append(("🟡 Warning", f"Only {content['quantifications']} quantified result(s). Aim for 4+ measurable achievements."))
        else:
            tips.append(("🟢 Good", f"{content['quantifications']} quantified achievements found. Great for recruiter impact!"))

        if len(content["impact_verbs"]) < 3:
            tips.append(("🟡 Warning", "Use more action verbs: built, deployed, optimised, reduced, scaled, led…"))
        else:
            tips.append(("🟢 Good", f"{len(content['impact_verbs'])} strong action verbs used. Keeps your resume dynamic."))

        if content["weak_phrases"]:
            tips.append(("🟡 Warning", f"Weak phrasing detected: '{content['weak_phrases'][0]}'. Replace with strong action verbs."))

        wc = self.word_count
        if wc < 150:
            tips.append(("🔴 Critical", f"Resume is too short ({wc} words). Aim for 300–600 words."))
        elif wc > 900:
            tips.append(("🟡 Warning", f"Resume might be too long ({wc} words). Keep it under 700 words (1 page)."))
        else:
            tips.append(("🟢 Good", f"Word count ({wc} words) is in the ideal range."))

        return tips

    # ── Top Keywords ─────────────────────────
    def _top_keywords(self):
        stopwords = {
            "the","and","for","with","was","are","from","this","that","have",
            "has","not","but","you","your","our","will","been","more","than",
            "into","also","them","they","were","its","can","all","which","who",
            "a","an","in","is","it","of","on","to","at","as","by","or","be"
        }
        clean  = re.sub(r"[^a-z\s]", " ", self.text)
        tokens = [w for w in clean.split() if len(w) > 3 and w not in stopwords]
        return Counter(tokens).most_common(15)
