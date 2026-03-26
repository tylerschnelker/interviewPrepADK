"""CLI entrypoint for the local interview-agent project.

The loop supports voice answers, direct typed answers, model answers, and
final readiness scoring, all orchestrated through planner-executor flow.
"""

from pathlib import Path

from session import InterviewSession


def _read_resume(path: str) -> str:
    """Loads resume text from a plain text or PDF file."""
    p = Path(path)
    if p.suffix.lower() == ".pdf":
        import pypdf
        reader = pypdf.PdfReader(str(p))
        return "\n".join(
            page.extract_text() for page in reader.pages if page.extract_text()
        )
    return p.read_text(encoding="utf-8")


def _read_multiline(prompt: str) -> str:
    """Collects multiline text until user enters a single line with END."""
    print(prompt)
    print("Finish by entering a line containing only: END")
    lines = []
    while True:
        line = input()
        if line.strip() == "END":
            break
        lines.append(line)
    return "\n".join(lines).strip()


def run() -> None:
    """Runs the complete interactive interview prep session."""
    print("=== interview-agent (local) ===")
    resume_path = input("Path to resume text file: ").strip()
    resume_text = _read_resume(resume_path)
    job_description = _read_multiline("Paste job description:")

    session = InterviewSession(resume_text=resume_text, job_description=job_description)
    print("\n" + session.step())

    while not session.state.finished:
        user = input("\nYou (/record, /model, /next, /end or typed answer): ").strip()
        output = session.step(user)
        print("\n" + output)

        # Automatically evaluate after a voice capture step for smoother flow.
        if "Now evaluating..." in output and not session.state.finished:
            print("\n" + session.step(None))

    print("\nSession complete.")


if __name__ == "__main__":
    run()
