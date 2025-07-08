# Use Ubuntu 24.04 as base image
FROM ubuntu:24.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV NODE_VERSION=18
ENV PYTHON_VERSION=3.11

# Set the environment variables from devcontainer
ENV GROQ_API_KEY="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"
ENV OPENAI_API_KEY="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"

# Update and install basic dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    git \
    gnupg \
    lsb-release \
    software-properties-common \
    build-essential \
    ca-certificates \
    sudo \
    locales \
    && rm -rf /var/lib/apt/lists/*

# Generate locale
RUN locale-gen en_US.UTF-8
ENV LANG=en_US.UTF-8
ENV LANGUAGE=en_US:en
ENV LC_ALL=en_US.UTF-8

# Install Python 3.11
RUN add-apt-repository ppa:deadsnakes/ppa -y && \
    apt-get update && \
    apt-get install -y \
    python${PYTHON_VERSION} \
    python${PYTHON_VERSION}-dev \
    python${PYTHON_VERSION}-venv \
    python3-pip \
    python3-setuptools \
    && rm -rf /var/lib/apt/lists/*

# Set Python 3.11 as default
RUN update-alternatives --install /usr/bin/python python /usr/bin/python${PYTHON_VERSION} 1 && \
    update-alternatives --install /usr/bin/python3 python3 /usr/bin/python${PYTHON_VERSION} 1

# Install pip for Python 3.11
RUN curl https://bootstrap.pypa.io/get-pip.py | python${PYTHON_VERSION}

# Install Node.js 18 and npm
RUN curl -fsSL https://deb.nodesource.com/setup_${NODE_VERSION}.x | bash - && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/*

# Install GitHub CLI
RUN curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | \
    gpg --dearmor -o /usr/share/keyrings/githubcli-archive-keyring.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | \
    tee /etc/apt/sources.list.d/github-cli.list > /dev/null && \
    apt-get update && \
    apt-get install -y gh && \
    rm -rf /var/lib/apt/lists/*

# Install node-gyp dependencies
RUN apt-get update && apt-get install -y \
    g++ \
    make \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user (similar to vscode user in devcontainer)
RUN useradd -m -s /bin/bash -u 1000 vscode && \
    usermod -aG sudo vscode && \
    echo "vscode ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# Set working directory
WORKDIR /workspace

# Copy the entire project structure
COPY --chown=vscode:vscode . /workspace/

# Switch to non-root user
USER vscode

# Install Python dependencies
RUN pip install --user -r requirements.txt && \
    pip install --user ipykernel && \
    python -m ipykernel install --user --name=python3

# Install Node.js dependencies
RUN cd /workspace/leonardos-rfq-alchemy-main && npm install

# Expose the ports mentioned in devcontainer
EXPOSE 8000 8080 8888

# Set the default command
CMD ["/bin/bash"]