"""Genera la home del sito (index.md) e la pagina 'Il corso giorno per giorno'.

Responsabilità: leggere i nomi delle note dal repository delle note e scrivere due file Markdown
con wikilink e un po' di HTML per le schede (stili in quartz/styles/custom.scss).
Non si occupa di: costruire il sito né di pubblicare.

Uso: python3 scripts/build_home.py <cartella delle note>   (default: content)
I due file vengono scritti nella stessa cartella delle note; il workflow lo esegue a ogni build.
"""
import re
import sys
from pathlib import Path

NOTES = Path(sys.argv[1] if len(sys.argv) > 1 else "content")
OUT = NOTES

# Note d'esame per priorità (nomi dei file, senza .md), come nell'indice del vault.
PRIORITIES = [
    ("critico", "Critico", [
        "Subnetting - Fondamentali e Calcolo Rapido", "VLAN - Trunking & Inter-VLAN Routing",
        "Static Routing & Floating Routes", "OSPF - Open Shortest Path First",
        "ACL - Access Control Lists (Standard & Extended)", "NAT - Network Address Translation"]),
    ("importante", "Molto importante", [
        "STP (802.1D) & Rapid-PVST+ (802.1w)", "STP Toolkit", "Wireless",
        "DHCP - Dynamic Host Configuration Protocol", "DNS - Domain Name System", "DHCP Snooping",
        "DAI (Dynamic ARP Inspection)", "Security Fundamentals (AAA, VPN, Threats, WPA3)",
        "Wireless - AP Modes & Management Access",
        "IP Services (NTP, SNMP, Syslog, SSH, CDP-LLDP, FTP-TFTP)", "00 Automation - Riassunto"]),
    ("medio", "Medio", [
        "Etherchannel", "Port Security (Layer 2)", "FHRP (First Hop Redundancy Protocol)", "IPv6", "QoS",
        "TCP vs UDP & Modello OSI", "Cloud, Virtualizzazione & WAN", "Componenti di Rete (Ruoli e Funzioni)",
        "Switching Concepts (MAC Table, ARP)", "Interfacce, Cablaggio & Troubleshooting",
        "Verifica IP Client & Troubleshooting (ping, traceroute)"]),
]

# Domini del blueprint 200-301 v1.1: (nome, peso %, note principali).
DOMAINS = [
    ("Fondamenti di rete", 20, ["Subnetting - Fondamentali e Calcolo Rapido", "IPv6", "Componenti di Rete (Ruoli e Funzioni)",
                                 "TCP vs UDP & Modello OSI", "Switching Concepts (MAC Table, ARP)", "Cloud, Virtualizzazione & WAN"]),
    ("Accesso alla rete", 20, ["VLAN - Trunking & Inter-VLAN Routing", "STP (802.1D) & Rapid-PVST+ (802.1w)", "Etherchannel", "Wireless"]),
    ("Connettività IP", 25, ["Static Routing & Floating Routes", "OSPF - Open Shortest Path First", "FHRP (First Hop Redundancy Protocol)"]),
    ("Servizi IP", 10, ["NAT - Network Address Translation", "DHCP - Dynamic Host Configuration Protocol", "DNS - Domain Name System",
                         "IP Services (NTP, SNMP, Syslog, SSH, CDP-LLDP, FTP-TFTP)", "QoS"]),
    ("Sicurezza", 15, ["ACL - Access Control Lists (Standard & Extended)", "Port Security (Layer 2)", "DHCP Snooping",
                       "DAI (Dynamic ARP Inspection)", "Security Fundamentals (AAA, VPN, Threats, WPA3)"]),
    ("Automazione", 10, ["00 Automation - Riassunto"]),
]
MAX_WEIGHT = 25  # PERCHÉ: la barra più lunga (25%) occupa tutta la larghezza.

# Cartelle con le note per giorno, e come chiamare l'area nella pagina.
DAY_AREAS = [
    ("10_Fondamenti", "Fondamenti"), ("20_Routing_Switching", "Routing e switching"), ("30_Servizi", "Servizi"),
    ("40_Sicurezza", "Sicurezza"), ("50_Wireless_Wan", "Wireless e WAN"),
    ("60_CCNA Exam/02 🟠 Molto importante/Automation", "Automazione"),
]
DAY_NAME = re.compile(r"^(?:day|DAY) (\d+)", re.IGNORECASE)
PART = re.compile(r"\((?:part|parte|Part) ?(\d)\)", re.IGNORECASE)


def link(name: str, label: str | None = None) -> str:
    return f"[[{name}|{label}]]" if label else f"[[{name}]]"


def exam_note_exists(name: str) -> bool:
    return any(NOTES.rglob(f"{name}.md"))


def build_home() -> str:
    lines = ["---", "title: Appunti CCNA 200-301",
             "description: Sintesi per il ripasso dell'esame CCNA 200-301, per priorità e per dominio.", "---", "",
             "Sintesi per il ripasso dell'esame **CCNA 200-301**: prima per importanza, poi per peso sull'esame.", "",
             "## Per priorità", "", '<div class="home-grid">', ""]
    for css, title, names in PRIORITIES:
        lines += [f'<div class="home-card {css}">', "", f'<p class="card-title">{title} <span>{len(names)} note</span></p>', ""]
        lines += [f"- {link(n)}" for n in names if exam_note_exists(n)]
        lines += ["", "</div>", ""]
    lines += ["</div>", "", "## Peso sull'esame", "", '<div class="home-grid wide">', ""]
    for name, weight, notes in DOMAINS:
        bar = round(weight / MAX_WEIGHT * 100)
        lines += ['<div class="home-card">', "",
                  f'<p class="card-title">{name} <span>{weight}%</span></p>',
                  f'<div class="bar"><i style="width:{bar}%"></i></div>', "",
                  " · ".join(link(n) for n in notes if exam_note_exists(n)), "", "</div>", ""]
    lines += ["</div>", "", "## Il corso", "", "Tutte le note del video-corso, giorno per giorno: [[Il corso giorno per giorno]].", ""]
    return "\n".join(lines)


def day_label(stem: str) -> tuple[int, int, str]:
    day = int(DAY_NAME.match(stem).group(1))
    part = PART.search(stem)
    suffix = f" · parte {part.group(1)}" if part else ""
    return day, int(part.group(1)) if part else 0, f"Day {day}{suffix}"


def build_days() -> str:
    lines = ["---", "title: Il corso giorno per giorno",
             "description: Le note del video-corso, ordinate per giorno e raggruppate per area.", "---", "",
             "Le note del video-corso, ordinate per giorno e raggruppate per area.", ""]
    for folder, area in DAY_AREAS:
        entries = []
        for path in sorted((NOTES / folder).rglob("*.md")):
            if DAY_NAME.match(path.stem):
                entries.append(day_label(path.stem) + (path.stem,))
        if entries:
            lines += [f"## {area}", "", '<div class="chips">', "",
                      " ".join(link(stem, label) for _, _, label, stem in sorted(entries)), "", "</div>", ""]
    return "\n".join(lines)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "index.md").write_text(build_home(), encoding="utf-8")
    (OUT / "Il corso giorno per giorno.md").write_text(build_days(), encoding="utf-8")
    print("scritti:", OUT / "index.md", "e", OUT / "Il corso giorno per giorno.md", flush=True)


if __name__ == "__main__":
    main()
