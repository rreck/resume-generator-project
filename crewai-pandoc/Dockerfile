# Copyright (c) RRECKTEK LLC
# Version: 1.1.0
# Built: @EPOCH

FROM debian:stable-slim

ENV DEBIAN_FRONTEND=noninteractive

# Core system tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates wget xz-utils fontconfig locales \
    python3 python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Python daemon and HTTP server dependencies
RUN pip3 install --no-cache-dir python-daemon --break-system-packages

# TeX Live (large enough to cover complex templates)
RUN apt-get update && apt-get install -y --no-install-recommends \
    texlive-latex-recommended \
    texlive-latex-extra \
    texlive-fonts-recommended \
    texlive-fonts-extra \
    texlive-xetex \
    texlive-luatex \
    texlive-bibtex-extra \
    biber \
    && rm -rf /var/lib/apt/lists/*

# Fonts (cover Inter + common fallback families)
RUN apt-get update && apt-get install -y --no-install-recommends \
    fonts-inter \
    fonts-noto \
    fonts-noto-cjk \
    fonts-dejavu \
    fonts-liberation \
    fonts-lmodern \
    && rm -rf /var/lib/apt/lists/*

# Extras often required by Pandoc + LaTeX templates
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-pygments \
    ghostscript \
    inkscape \
    graphviz \
    && rm -rf /var/lib/apt/lists/*

# Install Pandoc (static binary)
ARG PANDOC_VER=3.2.1
RUN wget -qO /tmp/pandoc.tar.gz https://github.com/jgm/pandoc/releases/download/${PANDOC_VER}/pandoc-${PANDOC_VER}-linux-amd64.tar.gz \
 && tar -xzf /tmp/pandoc.tar.gz -C /tmp \
 && mv /tmp/pandoc-${PANDOC_VER}/bin/pandoc /usr/local/bin/pandoc \
 && rm -rf /tmp/pandoc*

# Create application directory and copy main script
WORKDIR /opt/app
COPY app/main.py /opt/app/

# Create necessary directories
RUN mkdir -p /work/input /work/output /work/output/logs /var/run /var/log

# Expose metrics and API ports
EXPOSE 9090 8080

# Default environment variables
ENV INPUT_DIR=/work/input \
    OUTPUT_DIR=/work/output \
    TEMPLATE_FILE=/opt/app/template.tex \
    PIDFILE=/var/run/pandoc-agent.pid \
    METRICS_PORT=9090 \
    API_PORT=8080

# Healthcheck: verifies pandoc works and services are running
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD pandoc -v && \
        curl -f http://localhost:9090/metrics > /dev/null && \
        curl -f http://localhost:8080/health > /dev/null || exit 1

# Default command (can be overridden)
CMD ["python3", "/opt/app/main.py", "--daemon", "-i", "/work/input", "-o", "/work/output"]
