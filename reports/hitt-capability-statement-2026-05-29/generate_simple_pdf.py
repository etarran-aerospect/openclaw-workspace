#!/usr/bin/env python3
"""Generate a dependency-free one-page PDF capability statement.

The HTML file is the editable styled source. This script creates a basic PDF
artifact for upload in environments without Chromium, wkhtmltopdf, or LaTeX.
"""

from __future__ import annotations

from pathlib import Path
from textwrap import wrap


OUT = Path(__file__).with_name("AeroSpect-HITT-Capability-Statement.pdf")


def esc(text: str) -> str:
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def line(text: str, x: int, y: int, size: int = 10, font: str = "F1", color: tuple[float, float, float] = (0, 0, 0)) -> str:
    r, g, b = color
    return f"{r:.3f} {g:.3f} {b:.3f} rg BT /{font} {size} Tf {x} {y} Td ({esc(text)}) Tj ET\n"


def rect(x: int, y: int, w: int, h: int, color: tuple[float, float, float]) -> str:
    r, g, b = color
    return f"{r:.3f} {g:.3f} {b:.3f} rg {x} {y} {w} {h} re f\n"


def stroke_rect(x: int, y: int, w: int, h: int, color: tuple[float, float, float]) -> str:
    r, g, b = color
    return f"{r:.3f} {g:.3f} {b:.3f} RG {x} {y} {w} {h} re S\n"


def wrapped(text: str, x: int, y: int, width: int, size: int = 9, leading: int = 12, font: str = "F1") -> tuple[str, int]:
    chars = max(28, int(width / (size * 0.48)))
    chunks = wrap(text, chars)
    out = []
    for chunk in chunks:
        out.append(line(chunk, x, y, size, font, (0.09, 0.13, 0.20)))
        y -= leading
    return "".join(out), y


def bullets(items: list[str], x: int, y: int, width: int, size: int = 8, leading: int = 11) -> tuple[str, int]:
    out = []
    chars = max(24, int(width / (size * 0.48)))
    for item in items:
        parts = wrap(item, chars)
        if not parts:
            continue
        out.append(line("- " + parts[0], x, y, size, "F1", (0.09, 0.13, 0.20)))
        y -= leading
        for part in parts[1:]:
            out.append(line("  " + part, x, y, size, "F1", (0.09, 0.13, 0.20)))
            y -= leading
    return "".join(out), y


def heading(text: str, x: int, y: int) -> str:
    return line(text.upper(), x, y, 10, "F2", (0.09, 0.42, 0.56))


def build_stream() -> bytes:
    teal = (0.09, 0.42, 0.56)
    pale = (0.92, 0.96, 0.98)
    border = (0.78, 0.84, 0.89)
    stream = []
    stream.append(rect(0, 775, 612, 17, teal))
    stream.append(line("AeroSpect Inc.", 42, 735, 25, "F2", (0.07, 0.20, 0.28)))
    stream.append(line("Aerial Reality Capture, GIS Mapping & Site Intelligence for Mission Critical Construction", 42, 715, 10, "F2", (0.25, 0.31, 0.39)))
    stream.append(line("Capability statement prepared for HITT Contracting", 42, 699, 9, "F1", (0.39, 0.44, 0.52)))
    stream.append(stroke_rect(42, 687, 528, 1, border))

    # Company snapshot
    stream.append(rect(42, 560, 318, 110, pale))
    stream.append(stroke_rect(42, 560, 318, 110, border))
    stream.append(heading("Company Snapshot", 54, 652))
    y = 637
    txt, y = wrapped(
        "AeroSpect Inc. provides professional drone-based aerial data capture, photogrammetry, GIS mapping, thermal imaging, and construction progress documentation.",
        54,
        y,
        292,
        8,
        11,
    )
    stream.append(txt)
    txt, y = wrapped(
        "Led by a former commercial general contractor and former government contractor for security installations on military bases, with more than 3,000 licensed drone flight hours across construction, energy, agriculture, and infrastructure environments.",
        54,
        y - 2,
        292,
        8,
        11,
    )
    stream.append(txt)
    txt, y = wrapped(
        "AeroSpect understands jobsite sequencing, access control, site logistics, owner documentation, and repeatable field intelligence for PMs, VDC teams, owner reps, and trade partners.",
        54,
        y - 2,
        292,
        8,
        11,
    )
    stream.append(txt)

    # Best fit
    stream.append(rect(374, 560, 196, 110, pale))
    stream.append(stroke_rect(374, 560, 196, 110, border))
    stream.append(heading("Best-Fit Project Types", 386, 652))
    txt, _ = bullets(
        [
            "Mission critical and data center construction",
            "Industrial and energy sites",
            "Large-site civil and infrastructure work",
            "Security, perimeter, and access-control documentation",
            "Construction technology and VDC support",
            "Recurring regional site documentation",
        ],
        386,
        636,
        170,
        8,
        10,
    )
    stream.append(txt)

    # Core services
    stream.append(stroke_rect(42, 333, 254, 205, border))
    stream.append(heading("Core Services", 54, 520))
    txt, _ = bullets(
        [
            "Recurring aerial construction progress documentation",
            "High-resolution existing-condition photo records",
            "Orthomosaic mapping and photogrammetry deliverables",
            "GIS-ready site layers, annotations, and map packages",
            "Site logistics, laydown, access road, drainage, and utility corridor documentation",
            "Thermal imaging support for roofs, electrical infrastructure, equipment, and site heat concerns",
            "Perimeter and security infrastructure documentation",
            "Stakeholder-ready reporting for PMs, owner reps, consultants, and field teams",
        ],
        54,
        504,
        226,
        8,
        11,
    )
    stream.append(txt)

    # Data center applications
    stream.append(stroke_rect(316, 333, 254, 205, border))
    stream.append(heading("Mission Critical / Data Center Applications", 328, 520))
    txt, _ = bullets(
        [
            "Pre-construction site baseline documentation",
            "Weekly or monthly progress flights for large campus-style builds",
            "Earthwork, grading, trenching, and utility corridor documentation",
            "Visual status records for subcontractor coordination and owner reporting",
            "GIS-based tracking of site access, circulation, perimeter controls, and phased work areas",
            "Thermal and multispectral support where specialty sensing adds value",
            "Rapid independent documentation after weather, site events, disputes, or schedule impacts",
        ],
        328,
        504,
        226,
        8,
        11,
    )
    stream.append(txt)

    # Differentiators
    stream.append(rect(42, 214, 528, 92, pale))
    stream.append(stroke_rect(42, 214, 528, 92, border))
    stream.append(heading("Differentiators", 54, 288))
    badges = [
        "Former commercial GC perspective",
        "Military-base security installation background",
        "3,000+ licensed drone flight hours",
        "GIS analyst capability",
        "Thermal and multispectral specialization",
        "Established Northern California operator",
    ]
    x_positions = [54, 224, 394]
    y_positions = [260, 236]
    i = 0
    for y in y_positions:
        for x in x_positions:
            stream.append(rect(x, y, 150, 17, (0.84, 0.92, 0.95)))
            stream.append(line(badges[i], x + 6, y + 5, 7, "F2", (0.07, 0.20, 0.28)))
            i += 1

    # Compliance and contact
    stream.append(stroke_rect(42, 90, 254, 98, border))
    stream.append(heading("Compliance & Deliverable Note", 54, 170))
    txt, _ = wrapped(
        "AeroSpect provides aerial data capture, construction documentation, photogrammetry, GIS mapping, and site intelligence services. Stamped boundary, topographic, or other regulated survey deliverables can be coordinated with a licensed survey professional where required.",
        54,
        154,
        226,
        8,
        11,
    )
    stream.append(txt)

    stream.append(stroke_rect(316, 90, 254, 98, border))
    stream.append(heading("Contact", 328, 170))
    stream.append(line("Ethan Tarrant, AeroSpect Inc.", 328, 153, 9, "F2", (0.07, 0.20, 0.28)))
    stream.append(line("Website: https://www.aerospectinc.com", 328, 139, 8, "F1", (0.09, 0.13, 0.20)))
    txt, _ = wrapped(
        "COI, W-9, NAICS information, safety documentation, references, and TradeTapp onboarding materials can be provided upon request.",
        328,
        122,
        226,
        8,
        11,
    )
    stream.append(txt)

    return "".join(stream).encode("latin-1")


def write_pdf(content: bytes) -> None:
    objects = []
    objects.append(b"<< /Type /Catalog /Pages 2 0 R >>")
    objects.append(b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>")
    objects.append(
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        b"/Resources << /Font << /F1 4 0 R /F2 5 0 R >> >> /Contents 6 0 R >>"
    )
    objects.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
    objects.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>")
    objects.append(b"<< /Length " + str(len(content)).encode("ascii") + b" >>\nstream\n" + content + b"endstream")

    pdf = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for idx, obj in enumerate(objects, start=1):
        offsets.append(len(pdf))
        pdf.extend(f"{idx} 0 obj\n".encode("ascii"))
        pdf.extend(obj)
        pdf.extend(b"\nendobj\n")

    xref = len(pdf)
    pdf.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    pdf.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        pdf.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    pdf.extend(
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode("ascii")
    )
    OUT.write_bytes(pdf)


if __name__ == "__main__":
    write_pdf(build_stream())
    print(OUT)

