FROM python:3.8-slim

# Install system dependencies with proper verification
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gnupg \
    lsb-release \
    unzip \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Install Docker with proper verification
RUN curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian $(lsb_release -cs) stable" > /etc/apt/sources.list.d/docker.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends docker-ce docker-ce-cli containerd.io \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean \
    && rm -rf /var/run/docker.sock

# Create non-root user and add to docker group
RUN useradd -m -s /bin/bash platform && \
    usermod -aG docker platform

# Install Node.js and npm with proper verification
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Install AWS CLI with proper verification
RUN curl -fsSL "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" \
    && unzip awscliv2.zip \
    && ./aws/install \
    && rm -rf awscliv2.zip aws

# Install CDK
RUN npm install -g aws-cdk

# Set working directory
WORKDIR /app

# Copy requirements file with proper ownership
COPY --chown=platform:platform requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code with proper ownership
COPY --chown=platform:platform . .

# Switch to non-root user
USER platform

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    AWS_DEFAULT_REGION=eu-west-2

# Add healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:3000/health || exit 1

# Default command
CMD ["/bin/bash"] 